"""
WebSocket consumers for real-time communication.
Comprehensive implementation with Redis for chat, notifications, and presence.
"""
import json
import logging
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from django.utils import timezone
from asgiref.sync import sync_to_async

logger = logging.getLogger(__name__)
User = get_user_model()


class ChatConsumer(AsyncJsonWebsocketConsumer):
    """
    WebSocket consumer for real-time chat.

    Features:
    - Send/receive messages with emoji support (UTF-8)
    - Typing indicators
    - Read receipts
    - Delivery status
    - Online/offline status
    - Message history

    Endpoint: ws://domain/ws/chat/?token=YOUR_TOKEN

    Message types:
    - message: Send a chat message
    - typing: Send typing indicator
    - read_receipt: Mark messages as read
    - delivery_receipt: Confirm message delivery
    - get_online_status: Check if user is online
    """

    async def connect(self):
        """Handle WebSocket connection."""
        self.user = self.scope.get("user")

        if not self.user or not self.user.is_authenticated:
            logger.warning("Unauthorized WebSocket connection attempt")
            await self.close(code=4001)
            return

        # User-specific group for receiving messages
        self.user_group_name = f"chat_user_{self.user.id}"

        # Join user's personal group
        await self.channel_layer.group_add(
            self.user_group_name,
            self.channel_name
        )

        # Mark user as online in Redis
        await self.set_user_online(self.user.id)

        # Accept connection
        await self.accept()

        # Send connection success message
        await self.send_json({
            'type': 'connection',
            'status': 'connected',
            'user_id': self.user.id,
            'timestamp': timezone.now().isoformat()
        })

        # Notify contacts that user is online
        await self.broadcast_online_status(self.user.id, True)

        logger.info(f"ChatConsumer: User {self.user.id} connected")

    async def disconnect(self, close_code):
        """Handle WebSocket disconnection."""
        if hasattr(self, 'user_group_name'):
            # Leave user group
            await self.channel_layer.group_discard(
                self.user_group_name,
                self.channel_name
            )

        if hasattr(self, 'user') and self.user and self.user.is_authenticated:
            # Mark user as offline
            await self.set_user_offline(self.user.id)

            # Notify contacts that user is offline
            await self.broadcast_online_status(self.user.id, False)

            logger.info(f"ChatConsumer: User {self.user.id} disconnected (code: {close_code})")

    async def receive_json(self, content, **kwargs):
        """
        Handle incoming WebSocket messages.

        Supported message types:
        - message: {"type": "message", "receiver_id": 123, "message": "Hello", "attachment": "url"}
        - typing: {"type": "typing", "receiver_id": 123, "is_typing": true}
        - read_receipt: {"type": "read_receipt", "message_ids": [1,2,3]}
        - get_online_status: {"type": "get_online_status", "user_id": 123}
        """
        message_type = content.get('type', 'message')

        try:
            if message_type == 'message':
                await self.handle_chat_message(content)
            elif message_type == 'typing':
                await self.handle_typing_indicator(content)
            elif message_type == 'read_receipt':
                await self.handle_read_receipt(content)
            elif message_type == 'delivery_receipt':
                await self.handle_delivery_receipt(content)
            elif message_type == 'get_online_status':
                await self.handle_online_status_request(content)
            else:
                await self.send_json({
                    'type': 'error',
                    'error': f'Unknown message type: {message_type}'
                })
        except Exception as e:
            logger.error(f"Error handling message: {e}", exc_info=True)
            await self.send_json({
                'type': 'error',
                'error': str(e)
            })

    async def handle_chat_message(self, content):
        """Handle sending a chat message."""
        receiver_id = content.get('receiver_id')
        message_content = content.get('message', '').strip()
        attachment = content.get('attachment')

        # Validation
        if not receiver_id:
            await self.send_json({
                'type': 'error',
                'error': 'receiver_id is required'
            })
            return

        if not message_content and not attachment:
            await self.send_json({
                'type': 'error',
                'error': 'message or attachment is required'
            })
            return

        # Save message to database
        saved_message = await self.save_message(
            receiver_id=receiver_id,
            message=message_content,
            attachment=attachment
        )

        if not saved_message:
            await self.send_json({
                'type': 'error',
                'error': 'Failed to send message. Receiver not found.'
            })
            return

        # Get attachment URL if present
        attachment_url = await self.get_attachment_url(saved_message)

        # Prepare message data
        message_data = {
            'type': 'message',
            'id': saved_message['id'],
            'conversation_id': saved_message['conversation_id'],
            'sender_id': self.user.id,
            'sender_name': self.user.get_full_name() or self.user.username,
            'sender_avatar': await self.get_user_avatar(self.user),
            'receiver_id': receiver_id,
            'message': message_content,
            'attachment': attachment_url,
            'attachment_type': saved_message.get('attachment_type'),
            'timestamp': saved_message['timestamp'],
            'is_read': False,
            'delivered_at': saved_message.get('delivered_at'),
        }

        # Send to receiver's group
        receiver_group = f"chat_user_{receiver_id}"
        await self.channel_layer.group_send(
            receiver_group,
            {
                'type': 'chat_message',
                **message_data
            }
        )

        # Send confirmation to sender
        await self.send_json({
            'type': 'message_sent',
            'id': saved_message['id'],
            'conversation_id': saved_message['conversation_id'],
            'timestamp': saved_message['timestamp'],
            'temp_id': content.get('temp_id'),  # For client-side tracking
        })

    async def handle_typing_indicator(self, content):
        """Handle typing indicator."""
        receiver_id = content.get('receiver_id')
        is_typing = content.get('is_typing', True)

        if not receiver_id:
            return

        # Update typing indicator in database
        await self.update_typing_indicator(receiver_id, is_typing)

        # Send typing event to receiver
        receiver_group = f"chat_user_{receiver_id}"
        await self.channel_layer.group_send(
            receiver_group,
            {
                'type': 'typing_indicator',
                'sender_id': self.user.id,
                'sender_name': self.user.get_full_name() or self.user.username,
                'is_typing': is_typing,
                'timestamp': timezone.now().isoformat()
            }
        )

    async def handle_read_receipt(self, content):
        """Handle read receipt for messages."""
        message_ids = content.get('message_ids', [])
        conversation_id = content.get('conversation_id')
        sender_id = content.get('sender_id')

        if not message_ids and not conversation_id and not sender_id:
            await self.send_json({
                'type': 'error',
                'error': 'Provide message_ids, conversation_id, or sender_id'
            })
            return

        # Mark messages as read
        marked_messages = await self.mark_messages_read(
            message_ids=message_ids,
            conversation_id=conversation_id,
            sender_id=sender_id
        )

        # Send read receipts to original senders
        for msg_data in marked_messages:
            sender_group = f"chat_user_{msg_data['sender_id']}"
            await self.channel_layer.group_send(
                sender_group,
                {
                    'type': 'read_receipt',
                    'message_id': msg_data['message_id'],
                    'conversation_id': msg_data['conversation_id'],
                    'reader_id': self.user.id,
                    'reader_name': self.user.get_full_name() or self.user.username,
                    'read_at': msg_data['read_at'],
                }
            )

        # Send confirmation
        await self.send_json({
            'type': 'read_receipt_sent',
            'count': len(marked_messages)
        })

    async def handle_delivery_receipt(self, content):
        """Handle delivery receipt for messages."""
        message_id = content.get('message_id')

        if not message_id:
            return

        # Mark message as delivered
        result = await self.mark_message_delivered(message_id)

        if result:
            # Notify sender
            sender_group = f"chat_user_{result['sender_id']}"
            await self.channel_layer.group_send(
                sender_group,
                {
                    'type': 'delivery_receipt',
                    'message_id': message_id,
                    'delivered_at': result['delivered_at'],
                }
            )

    async def handle_online_status_request(self, content):
        """Handle request to check if a user is online."""
        user_id = content.get('user_id')

        if not user_id:
            return

        is_online = await self.check_user_online(user_id)

        await self.send_json({
            'type': 'online_status',
            'user_id': user_id,
            'is_online': is_online,
            'timestamp': timezone.now().isoformat()
        })

    # Channel layer event handlers

    async def chat_message(self, event):
        """Send chat message to WebSocket."""
        await self.send_json(event)

        # Send automatic delivery receipt
        if 'id' in event:
            await self.handle_delivery_receipt({'message_id': event['id']})

    async def typing_indicator(self, event):
        """Send typing indicator to WebSocket."""
        await self.send_json(event)

    async def read_receipt(self, event):
        """Send read receipt to WebSocket."""
        await self.send_json(event)

    async def delivery_receipt(self, event):
        """Send delivery receipt to WebSocket."""
        await self.send_json(event)

    async def online_status_changed(self, event):
        """Send online status change to WebSocket."""
        await self.send_json(event)

    # Database operations (async wrapped)

    @database_sync_to_async
    def save_message(self, receiver_id, message, attachment=None):
        """Save chat message to database."""
        from .models import ChatMessage, Conversation

        try:
            receiver = User.objects.get(id=receiver_id)

            # Get or create conversation
            conversation = Conversation.get_or_create_conversation(self.user, receiver)

            # Create message
            chat_message = ChatMessage.objects.create(
                sender=self.user,
                receiver=receiver,
                conversation=conversation,
                message=message,
                attachment=attachment,
                delivered_at=timezone.now()
            )

            # Update conversation metadata
            conversation.last_message = message[:100] if message else "[Attachment]"
            conversation.last_message_at = chat_message.timestamp
            conversation.last_message_by = self.user
            conversation.increment_unread(receiver)
            conversation.save()

            return {
                'id': chat_message.id,
                'conversation_id': conversation.id,
                'timestamp': chat_message.timestamp.isoformat(),
                'attachment_type': chat_message.attachment_type,
                'delivered_at': chat_message.delivered_at.isoformat() if chat_message.delivered_at else None,
            }
        except User.DoesNotExist:
            logger.warning(f"User {receiver_id} not found")
            return None
        except Exception as e:
            logger.error(f"Error saving message: {e}", exc_info=True)
            return None

    @database_sync_to_async
    def get_attachment_url(self, message_data):
        """Get attachment URL from message."""
        from .models import ChatMessage

        try:
            if message_data and message_data.get('id'):
                message = ChatMessage.objects.get(id=message_data['id'])
                if message.attachment:
                    try:
                        return message.attachment.url
                    except:
                        return str(message.attachment)
        except:
            pass
        return None

    @database_sync_to_async
    def get_user_avatar(self, user):
        """Get user avatar URL."""
        try:
            if hasattr(user, 'avatar') and user.avatar:
                return user.avatar.url
        except:
            pass
        return None

    @database_sync_to_async
    def update_typing_indicator(self, receiver_id, is_typing):
        """Update typing indicator in database."""
        from .models import TypingIndicator

        try:
            receiver = User.objects.get(id=receiver_id)
            TypingIndicator.objects.update_or_create(
                user=self.user,
                conversation_partner=receiver,
                defaults={'is_typing': is_typing}
            )
        except Exception as e:
            logger.error(f"Error updating typing indicator: {e}")

    @database_sync_to_async
    def mark_messages_read(self, message_ids=None, conversation_id=None, sender_id=None):
        """Mark messages as read."""
        from .models import ChatMessage, Conversation

        marked = []

        try:
            # Build query
            messages = ChatMessage.objects.filter(
                receiver=self.user,
                is_read=False
            )

            if message_ids:
                messages = messages.filter(id__in=message_ids)
            elif conversation_id:
                messages = messages.filter(conversation_id=conversation_id)
            elif sender_id:
                messages = messages.filter(sender_id=sender_id)

            # Mark as read
            read_time = timezone.now()
            messages_list = list(messages.select_related('sender'))

            for msg in messages_list:
                msg.is_read = True
                msg.read_at = read_time
                msg.save(update_fields=['is_read', 'read_at', 'updated_at'])

                marked.append({
                    'message_id': msg.id,
                    'conversation_id': msg.conversation_id,
                    'sender_id': msg.sender_id,
                    'read_at': read_time.isoformat()
                })

            # Reset unread count in conversation
            if conversation_id:
                try:
                    conversation = Conversation.objects.get(id=conversation_id)
                    conversation.reset_unread(self.user)
                except Conversation.DoesNotExist:
                    pass

            return marked
        except Exception as e:
            logger.error(f"Error marking messages read: {e}", exc_info=True)
            return []

    @database_sync_to_async
    def mark_message_delivered(self, message_id):
        """Mark message as delivered."""
        from .models import ChatMessage

        try:
            message = ChatMessage.objects.get(id=message_id, receiver=self.user)
            if not message.delivered_at:
                message.delivered_at = timezone.now()
                message.save(update_fields=['delivered_at', 'updated_at'])

            return {
                'sender_id': message.sender_id,
                'delivered_at': message.delivered_at.isoformat()
            }
        except ChatMessage.DoesNotExist:
            return None
        except Exception as e:
            logger.error(f"Error marking message delivered: {e}")
            return None

    # Redis operations for presence

    async def set_user_online(self, user_id):
        """Mark user as online in Redis."""
        from .redis_utils import set_user_online_ws
        await sync_to_async(set_user_online_ws)(user_id)

    async def set_user_offline(self, user_id):
        """Mark user as offline in Redis."""
        from .redis_utils import set_user_offline_ws
        await sync_to_async(set_user_offline_ws)(user_id)

    async def check_user_online(self, user_id):
        """Check if user is online."""
        from .redis_utils import is_user_online_ws
        return await sync_to_async(is_user_online_ws)(user_id)

    async def broadcast_online_status(self, user_id, is_online):
        """Broadcast online status to all contacts."""
        # Get user's recent contacts
        contact_ids = await self.get_recent_contacts(user_id)

        # Notify each contact
        for contact_id in contact_ids:
            contact_group = f"chat_user_{contact_id}"
            await self.channel_layer.group_send(
                contact_group,
                {
                    'type': 'online_status_changed',
                    'user_id': user_id,
                    'is_online': is_online,
                    'timestamp': timezone.now().isoformat()
                }
            )

    @database_sync_to_async
    def get_recent_contacts(self, user_id):
        """Get list of recent contact IDs for a user."""
        from .models import Conversation
        from django.db.models import Q

        try:
            # Get all conversations where user is participant
            conversations = Conversation.objects.filter(
                Q(user1_id=user_id) | Q(user2_id=user_id),
                is_active=True
            ).values_list('user1_id', 'user2_id')[:50]

            # Extract contact IDs
            contact_ids = set()
            for user1_id, user2_id in conversations:
                if user1_id != user_id:
                    contact_ids.add(user1_id)
                if user2_id != user_id:
                    contact_ids.add(user2_id)

            return list(contact_ids)
        except Exception as e:
            logger.error(f"Error getting recent contacts: {e}")
            return []


class NotificationConsumer(AsyncJsonWebsocketConsumer):
    """
    WebSocket consumer for real-time notifications.

    Features:
    - In-app notifications
    - System notifications
    - College-wide broadcasts
    - Read/unread tracking
    - Priority notifications

    Endpoint: ws://domain/ws/notifications/?token=YOUR_TOKEN

    Message types:
    - mark_read: Mark notification as read
    - mark_all_read: Mark all notifications as read
    - get_unread_count: Get unread notification count
    """

    async def connect(self):
        """Handle WebSocket connection."""
        self.user = self.scope.get("user")

        if not self.user or not self.user.is_authenticated:
            logger.warning("Unauthorized notification WebSocket connection")
            await self.close(code=4001)
            return

        # User-specific notification group
        self.user_notification_group = f"notifications_user_{self.user.id}"
        await self.channel_layer.group_add(
            self.user_notification_group,
            self.channel_name
        )

        # College-wide notification group
        college_id = await self.get_user_college_id()
        if college_id:
            self.college_notification_group = f"notifications_college_{college_id}"
            await self.channel_layer.group_add(
                self.college_notification_group,
                self.channel_name
            )

        await self.accept()

        # Send connection success and unread count
        unread_count = await self.get_unread_notification_count()
        await self.send_json({
            'type': 'connection',
            'status': 'connected',
            'user_id': self.user.id,
            'unread_count': unread_count,
            'timestamp': timezone.now().isoformat()
        })

        logger.info(f"NotificationConsumer: User {self.user.id} connected")

    async def disconnect(self, close_code):
        """Handle WebSocket disconnection."""
        if hasattr(self, 'user_notification_group'):
            await self.channel_layer.group_discard(
                self.user_notification_group,
                self.channel_name
            )

        if hasattr(self, 'college_notification_group'):
            await self.channel_layer.group_discard(
                self.college_notification_group,
                self.channel_name
            )

        logger.info(f"NotificationConsumer: User {self.user.id} disconnected")

    async def receive_json(self, content, **kwargs):
        """
        Handle incoming WebSocket messages.

        Supported message types:
        - mark_read: {"type": "mark_read", "notification_id": 123}
        - mark_all_read: {"type": "mark_all_read"}
        - get_unread_count: {"type": "get_unread_count"}
        """
        message_type = content.get('type')

        try:
            if message_type == 'mark_read':
                await self.handle_mark_read(content)
            elif message_type == 'mark_all_read':
                await self.handle_mark_all_read()
            elif message_type == 'get_unread_count':
                await self.handle_get_unread_count()
            else:
                await self.send_json({
                    'type': 'error',
                    'error': f'Unknown message type: {message_type}'
                })
        except Exception as e:
            logger.error(f"Error handling notification message: {e}", exc_info=True)
            await self.send_json({
                'type': 'error',
                'error': str(e)
            })

    async def handle_mark_read(self, content):
        """Mark a notification as read."""
        notification_id = content.get('notification_id')

        if not notification_id:
            await self.send_json({
                'type': 'error',
                'error': 'notification_id is required'
            })
            return

        success = await self.mark_notification_read(notification_id)

        if success:
            unread_count = await self.get_unread_notification_count()
            await self.send_json({
                'type': 'notification_read',
                'notification_id': notification_id,
                'unread_count': unread_count
            })

    async def handle_mark_all_read(self):
        """Mark all notifications as read."""
        count = await self.mark_all_notifications_read()

        await self.send_json({
            'type': 'all_notifications_read',
            'count': count,
            'unread_count': 0
        })

    async def handle_get_unread_count(self):
        """Get unread notification count."""
        unread_count = await self.get_unread_notification_count()

        await self.send_json({
            'type': 'unread_count',
            'count': unread_count
        })

    # Channel layer event handlers

    async def notification(self, event):
        """Send notification to WebSocket."""
        await self.send_json(event)

    async def notification_update(self, event):
        """Send notification update to WebSocket."""
        await self.send_json(event)

    # Database operations

    @database_sync_to_async
    def get_user_college_id(self):
        """Get user's college ID."""
        return getattr(self.user, 'college_id', None)

    @database_sync_to_async
    def get_unread_notification_count(self):
        """Get unread notification count."""
        from .models import InAppNotification

        try:
            return InAppNotification.objects.filter(
                recipient=self.user,
                is_read=False,
                is_active=True
            ).count()
        except Exception as e:
            logger.error(f"Error getting unread count: {e}")
            return 0

    @database_sync_to_async
    def mark_notification_read(self, notification_id):
        """Mark notification as read."""
        from .models import InAppNotification

        try:
            notification = InAppNotification.objects.get(
                id=notification_id,
                recipient=self.user
            )
            notification.mark_as_read()
            return True
        except InAppNotification.DoesNotExist:
            return False
        except Exception as e:
            logger.error(f"Error marking notification read: {e}")
            return False

    @database_sync_to_async
    def mark_all_notifications_read(self):
        """Mark all notifications as read."""
        from .models import InAppNotification

        try:
            notifications = InAppNotification.objects.filter(
                recipient=self.user,
                is_read=False
            )
            read_time = timezone.now()
            count = notifications.update(is_read=True, read_at=read_time)
            return count
        except Exception as e:
            logger.error(f"Error marking all notifications read: {e}")
            return 0
