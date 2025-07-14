import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User
from .models import Message
from django.utils import timezone


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Get the user from the scope
        self.user = self.scope["user"]
        
        if not self.user.is_authenticated:
            await self.close()
            return
        
        # Get the other user from the URL parameters
        self.other_user_username = self.scope['url_route']['kwargs']['other_user']
        
        try:
            self.other_user = await self.get_user(self.other_user_username)
        except User.DoesNotExist:
            await self.close()
            return
        
        # Create a unique room name for this conversation
        user_ids = sorted([self.user.id, self.other_user.id])
        self.room_name = f"chat_{user_ids[0]}_{user_ids[1]}"
        self.room_group_name = f"chat_{self.room_name}"
        
        # Join the room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # Mark messages as read when user connects
        await self.mark_messages_as_read()
    
    async def disconnect(self, close_code):
        # Leave the room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_type = text_data_json.get('type', 'message')
        
        if message_type == 'message':
            message_text = text_data_json['message']
            
            # Save the message to database
            message = await self.save_message(message_text)
            
            # Send message to room group
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': message_text,
                    'sender_username': self.user.username,
                    'sender_full_name': self.user.get_full_name() or self.user.username,
                    'timestamp': message.timestamp.isoformat(),
                    'message_id': message.id,
                }
            )
    
    async def chat_message(self, event):
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'message',
            'message': event['message'],
            'sender_username': event['sender_username'],
            'sender_full_name': event['sender_full_name'],
            'timestamp': event['timestamp'],
            'message_id': event['message_id'],
        }))
    
    @database_sync_to_async
    def get_user(self, username):
        return User.objects.get(username=username)
    
    @database_sync_to_async
    def save_message(self, message_text):
        return Message.objects.create(
            sender=self.user,
            recipient=self.other_user,
            content=message_text,
            timestamp=timezone.now()
        )
    
    @database_sync_to_async
    def mark_messages_as_read(self):
        Message.objects.filter(
            sender=self.other_user,
            recipient=self.user,
            is_read=False
        ).update(is_read=True) 