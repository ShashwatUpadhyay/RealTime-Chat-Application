from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync
import json
from base.models import Room, Message

class ChatConsumer(WebsocketConsumer):
    connected_peers = {}
    def connect(self, **kwargs):
        self.room_name = self.scope['url_route']['kwargs']['code'] 
        self.room_group_name = f'chat_{self.room_name}'
        
        if self.room_name not in ChatConsumer.connected_peers:
            ChatConsumer.connected_peers[self.room_name] = []
        ChatConsumer.connected_peers[self.room_name].append(self.channel_name)
        print("Connected peers:", ChatConsumer.connected_peers)
        
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name)
        self.accept()
        
        room = Room.objects.get(code=self.room_name)
        receiver_channel_name = ''
        for i in ChatConsumer.connected_peers[self.room_name]:
            if i != self.channel_name:
                receiver_channel_name = i
        self.send(text_data=json.dumps({
            'type': 'connection_established',
            'message': 'You are now connected to the chat room',
            'room_name': self.room_name,
            'peer': self.channel_name,
            'action': 'new-peer',
            'message': {
                'receiver_channel_name': receiver_channel_name
            },
            'connected_peers': ChatConsumer.connected_peers[self.room_name]
        }))
    
    def chat_message(self, event):
        data = json.loads(event['value'])
        print(data)
        self.send(text_data=json.dumps(data))
    
    def receive(self, text_data=None, bytes_data=None): 
        data = json.loads(text_data)
        print("Received data:", data)
        
        # Handle chat messages
        if 'user' in data and 'content' in data:
            user = data.get('user')
            content = data.get('content')
            room = Room.objects.get(code=self.room_name)
            Message.create_message(room.id, user, content)
            
            # Broadcast chat message to room
            self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'value': json.dumps({
                        'connected_peers': ChatConsumer.connected_peers[self.room_name],
                        'peer': self.channel_name,
                        'user': user,
                        'content': content
                    })
                }
            )
            return

        # Handle WebRTC signaling
        if 'action' in data and 'message' in data:
            action = data['action']
            message = data['message']
            
            if action in ['new-peer', 'new-answer']:
                receiver_channel_name = message.get('receiver_channel_name')
                if receiver_channel_name:
                    print("Sending to receiver channel:", receiver_channel_name, " - " , self.channel_name)
                    self.channel_layer.group_send(
                        self.room_group_name,
                        {
                            'connected_peers': ChatConsumer.connected_peers[self.room_name],
                            'peer': self.channel_name,
                            'type': 'send_sdp',
                            'value': json.dumps(data)
                        }
                    )
                else:
                    data['message']['receiver_channel_name'] = self.channel_name
                    self.channel_layer.group_send(
                        self.room_group_name,
                        {
                            'type': 'send_sdp',
                            'value': json.dumps(data)
                        }
                    )
                    return
                
    def send_sdp(self, event):
        data = json.loads(event['value'])
        print("Received data from send_sdp:", data)
        self.send(text_data=json.dumps(data))
    
    def disconnect(self, code):
        print("disconnected")
        self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        if self.room_name in ChatConsumer.connected_peers:
            ChatConsumer.connected_peers[self.room_name] = [
                ch for ch in ChatConsumer.connected_peers[self.room_name]
                if ch != self.channel_name
            ]
