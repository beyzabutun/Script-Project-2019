from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
import json
from .models import *
from datetime import datetime


class AnnouncementConsumer(WebsocketConsumer):
    def connect(self):
        self.room_name = "announcement"
        self.room_group_name = 'announcement'

        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )

        self.accept()

    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['msg']
        print(text_data_json['states'])
        states = text_data_json['states']
        item_id = text_data_json['item_id']
        item = Item.objects.get(id=item_id)

        announcement = Announcement.objects.create(item_id=item_id, friend_state=int(states), msg=message,
                                    date=datetime.now())



        # Send message to room group
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'announcement_handler',
                'announcement_id': announcement.id
            }
        )

    # Receive message from room group
    def announcement_handler(self, event):
        announcement_id = event['announcement_id']

        # Send message to WebSocket
        self.send(text_data=json.dumps({
            'announcement_id': announcement_id
        }))