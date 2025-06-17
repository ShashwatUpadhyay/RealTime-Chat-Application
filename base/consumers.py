from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync
import json
from base.models import Room, Message

class ChatConsumer(WebsocketConsumer):
    def connect(self, **kwargs):
        self.room_name = self.scope['url_route']['kwargs']['code'] 
        self.room_group_name = f'chat_{self.room_name}'
        
        
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name)
        self.accept()
    
        room = Room.objects.get(code=self.room_name)
        self.send(text_data=json.dumps({
            'type': 'connection_established',
            'message': 'You are now connected to the chat room',
            'room_name': self.room_name,
            'channel_name': self.channel_name,
        }))
    
    def chat_message(self, event):
        data = json.loads(event['value'])
        print(data)
        self.send(text_data=json.dumps(data))
    
    def receive(self, text_data=None, bytes_data=None): 
        data = json.loads(text_data)
        print("Received data:", data)
        
        if data.get('user') and data.get('content'):
            user = data.get('user')
            content = data.get('content')
            room = Room.objects.get(code=self.room_name)
            Message.create_message(room.id, user, content)
            
        
        # Broadcast chat message to room
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'send_sdp',
                'value': json.dumps(data)
            }
        )

        
    def send_sdp(self, event):
        self.send(text_data=event["value"])

    
    def disconnect(self, code):
        print("disconnected")
        self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
