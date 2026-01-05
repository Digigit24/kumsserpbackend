import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model

User = get_user_model()

class ChatConsumer(AsyncWebsocketConsumer):
    """
    Consumer for real-time chat between users.
    """
    async def connect(self):
        self.user = self.scope["user"]
        
        if self.user.is_authenticated:
            # Join a personal room based on user ID
            self.room_group_name = f"user_{self.user.id}"
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )
            await self.accept()
        else:
            await self.close()

    async def disconnect(self, close_code):
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )

    async def receive(self, text_data):
        """
        Handle incoming WebSocket messages.
        Expects JSON: {"receiver_id": int, "message": str}
        """
        data = json.loads(text_data)
        receiver_id = data.get("receiver_id")
        message_content = data.get("message")

        if not receiver_id or not message_content:
            return

        # Save message to database
        saved_msg = await self.save_message(receiver_id, message_content)
        
        if saved_msg:
            # Send message to receiver's group
            receiver_group = f"user_{receiver_id}"
            await self.channel_layer.group_send(
                receiver_group,
                {
                    "type": "chat_message",
                    "id": saved_msg.id,
                    "sender_id": self.user.id,
                    "sender_name": self.user.get_full_name(),
                    "message": message_content,
                    "timestamp": str(saved_msg.timestamp),
                }
            )
            
            # Send confirmation back to sender
            await self.send(text_data=json.dumps({
                "type": "message_sent",
                "id": saved_msg.id,
                "status": "delivered"
            }))

    async def chat_message(self, event):
        """
        Receive message from channel group and send to WebSocket.
        """
        await self.send(text_data=json.dumps(event))

    @database_sync_to_async
    def save_message(self, receiver_id, message):
        from .models import ChatMessage
        try:
            receiver = User.objects.get(id=receiver_id)
            return ChatMessage.objects.create(
                sender=self.user,
                receiver=receiver,
                message=message
            )
        except User.DoesNotExist:
            return None


class NotificationConsumer(AsyncWebsocketConsumer):
    """
    Consumer for real-time system notifications and alerts.
    """
    async def connect(self):
        self.user = self.scope["user"]
        
        if self.user.is_authenticated:
            # Join room based on user ID and optional college ID
            self.user_room = f"notifications_{self.user.id}"
            await self.channel_layer.group_add(
                self.user_room,
                self.channel_name
            )
            
            # If user has a college, join college-wide room
            college_id = getattr(self.user, 'college_id', None)
            if college_id:
                self.college_room = f"college_notifications_{college_id}"
                await self.channel_layer.group_add(
                    self.college_room,
                    self.channel_name
                )
            
            await self.accept()
        else:
            await self.close()

    async def disconnect(self, close_code):
        if hasattr(self, 'user_room'):
            await self.channel_layer.group_discard(
                self.user_room,
                self.channel_name
            )
        if hasattr(self, 'college_room'):
            await self.channel_layer.group_discard(
                self.college_room,
                self.channel_name
            )

    async def notify(self, event):
        """
        Generic notification handler.
        """
        await self.send(text_data=json.dumps(event))
