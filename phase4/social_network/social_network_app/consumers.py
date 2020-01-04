from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
import json
from .models import *
from datetime import datetime
from django.db.models import Q


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



class NotificationConsumer(WebsocketConsumer):
    def connect(self):
        self.room_name = "notification"
        self.room_group_name = 'notification'

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
        print("heiiii")
        text_data = json.loads(text_data)
        state_names = text_data['state_names']
        states = text_data['states']
        item_id = text_data['item_id']

        item = Item.objects.get(pk=item_id)
        item.__setattr__(state_names, int(states))
        if item.detail > item.view:
            item.view = item.detail
            # messages.warning(request,
            #                  'Detail permission cannot have higher priority than view permission. View permission also be set ' +
            #                  STATE_TYPE[int(item.detail)])

        if item.borrow > item.view:
            item.borrow = item.view
            # messages.warning(request,
            #                  'Borrow permission cannot have higher priority than view permission. Borrow permission also be set ' +
            #                  STATE_TYPE[int(item.view)])


        if state_names == 'borrow':
            requests = WatchRequest.objects.filter(Q(item=item) & Q(watch_method=1))
            text = f'{item.owner.first_name} {item.owner.last_name} changed borrow state to {STATE_TYPE[int(states)]} for the item with title {item.title}.'
            for cr in requests:
                notification =Notification.objects.create(sender_user=item.owner, receiver_user=cr.user, item_id=item.id,
                                            text=text, date=datetime.now())
        if state_names == 'comment':
            requests = WatchRequest.objects.filter(Q(item=item) & Q(watch_method=0))
            text = f'{item.owner.first_name} {item.owner.last_name} changed comment state to {STATE_TYPE[int(states)]} for the item with title {item.title}.'
            for cr in requests:
                notification =Notification.objects.create(sender_user=item.owner, receiver_user=cr.user, item_id=item.id,
                                            text=text, date=datetime.now())
        print("heiiii")
        item.save()


        # Send message to room group
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'notification_handler',
                'notification_id': notification.id
            }
        )

    # Receive message from room group
    def notification_handler(self, event):
        notification_id = event['notification_id']

        # Send message to WebSocket
        self.send(text_data=json.dumps({
            'notification_id': notification_id
        }))