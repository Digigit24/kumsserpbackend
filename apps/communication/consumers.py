import logging
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model

logger = logging.getLogger(__name__)
User = get_user_model()


class ChatConsumer(AsyncJsonWebsocketConsumer):
    """
    Consumer for real-time chat between users.
    Endpoint: /ws/chat/
    """
    async def connect(self):
        self.user = self.scope.get("user")
<<<<<<< HEAD

        if self.user and self.user.is_authenticated:
            self.room_group_name = f"chat_user_{self.user.id}"
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )
            await self.accept()
=======
        
        # Accept the connection first
        await self.accept()

        if self.user and self.user.is_authenticated:
            try:
                # Join a personal room based on user ID for Chat
                self.room_group_name = f"chat_user_{self.user.id}"
                logger.debug(f"ChatConsumer: User {self.user.id} joining group {self.room_group_name}")
                
                await self.channel_layer.group_add(
                    self.room_group_name,
                    self.channel_name
                )
            except Exception as e:
                logger.error(f"ChatConsumer group_add error: {e}")
>>>>>>> 070d882ad79c5c57ba35dff647ddc6eb2b9320c3
        else:
            logger.warning("ChatConsumer: Unauthorized connection attempt")
            # Close with code 4003 on auth failure
            await self.close(code=4003)

    async def disconnect(self, close_code):
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )

    async def receive_json(self, content, **kwargs):
        """
        Handle incoming WebSocket messages.
        Expects JSON: {"receiver_id": int, "message": str, "attachment": str (optional)}
        """
        receiver_id = content.get("receiver_id")
        message_content = (content.get("message") or "").strip()
        attachment = content.get("attachment")

        if not receiver_id:
            await self.send_json({
                "type": "error",
                "error": "receiver_id is required"
            })
            return

        if not message_content and not attachment:
            await self.send_json({
                "type": "error",
                "error": "message or attachment is required"
            })
            return

        saved_msg = await self.save_message(receiver_id, message_content, attachment)

<<<<<<< HEAD
        if saved_msg:
            attachment_url = None
            if saved_msg.attachment:
                try:
                    attachment_url = saved_msg.attachment.url
                except Exception:
                    attachment_url = str(saved_msg.attachment)

            receiver_group = f"chat_user_{receiver_id}"
            await self.channel_layer.group_send(
                receiver_group,
                {
                    "type": "chat_message",
                    "id": saved_msg.id,
                    "sender_id": self.user.id,
                    "sender_name": self.user.get_full_name(),
                    "message": message_content,
                    "attachment": attachment_url,
                    "timestamp": saved_msg.timestamp.isoformat(),
                }
            )
=======
            if saved_msg:
                # Type 1: Send New Chat Message to receiver's group
                receiver_group = f"chat_user_{receiver_id}"
                await self.channel_layer.group_send(
                    receiver_group,
                    {
                        "type": "chat_message",
                        "id": saved_msg.id,
                        "sender_id": self.user.id,
                        "sender_name": self.user.get_full_name() or self.user.username,
                        "message": message_content,
                        "attachment": attachment,  # URL string or null
                        "timestamp": saved_msg.timestamp.isoformat() if saved_msg.timestamp else "",
                    }
                )

                # Type 2: Send Acknowledgement back to sender
                await self.send(text_data=json.dumps({
                    "type": "message_sent",
                    "id": saved_msg.id
                }))
            else:
                await self.send(text_data=json.dumps({
                    "type": "error",
                    "error": "User not found"
                }))
>>>>>>> 070d882ad79c5c57ba35dff647ddc6eb2b9320c3

            await self.send_json({
                "type": "message_sent",
                "id": saved_msg.id
            })
        else:
            await self.send_json({
                "type": "error",
                "error": "Failed to send message. Receiver not found."
            })

    async def chat_message(self, event):
        """
        Receive message from channel group and send to WebSocket.
        """
<<<<<<< HEAD
        await self.send_json(event)
=======
        # Exclude internal channel event type if needed, but standard is to send 'type' which matches the spec
        await self.send(text_data=json.dumps(event))
>>>>>>> 070d882ad79c5c57ba35dff647ddc6eb2b9320c3

    @database_sync_to_async
    def save_message(self, receiver_id, message, attachment=None):
        from .models import ChatMessage
        try:
            receiver = User.objects.get(id=receiver_id)
            return ChatMessage.objects.create(
                sender=self.user,
                receiver=receiver,
                message=message,
                attachment=attachment
            )
        except User.DoesNotExist:
            logger.warning(f"User {receiver_id} not found when saving message")
            return None
        except Exception as e:
            logger.error(f"Error saving message: {str(e)}", exc_info=True)
            return None


class NotificationConsumer(AsyncJsonWebsocketConsumer):
    """
    Consumer for real-time system notifications and alerts.
    Endpoint: /ws/notifications/
    """
    async def connect(self):
        self.user = self.scope.get("user")
<<<<<<< HEAD

        if self.user and self.user.is_authenticated:
            self.user_room = f"user_{self.user.id}"
            await self.channel_layer.group_add(
                self.user_room,
                self.channel_name
            )

            college_id = getattr(self.user, 'college_id', None)
            if college_id:
                self.college_room = f"college_notifications_{college_id}"
=======
        
        # Accept the connection first
        await self.accept()

        if self.user and self.user.is_authenticated:
            try:
                # Join room based on user ID for Notifications
                self.room_group_name = f"user_{self.user.id}"
                logger.debug(f"NotificationConsumer: User {self.user.id} joining group {self.room_group_name}")
                
>>>>>>> 070d882ad79c5c57ba35dff647ddc6eb2b9320c3
                await self.channel_layer.group_add(
                    self.room_group_name,
                    self.channel_name
                )
<<<<<<< HEAD

            await self.accept()
=======
            except Exception as e:
                logger.error(f"NotificationConsumer group_add error: {e}")
>>>>>>> 070d882ad79c5c57ba35dff647ddc6eb2b9320c3
        else:
            logger.warning("NotificationConsumer: Unauthorized connection attempt")
            # Close with code 4003 on auth failure
            await self.close(code=4003)

    async def disconnect(self, close_code):
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )

    async def notify(self, event):
        """
<<<<<<< HEAD
        Notification handler.
        """
        await self.send_json(event)
=======
        Generic notification handler.
        Payload structure MUST match:
        {
          "type": "notify",
          "id": 123,
          "title": "New Alert",
          "message": "Content...",
          "notification_type": "info",
          "timestamp": "ISO-8601-String"
        }
        """
        await self.send(text_data=json.dumps(event))

>>>>>>> 070d882ad79c5c57ba35dff647ddc6eb2b9320c3
