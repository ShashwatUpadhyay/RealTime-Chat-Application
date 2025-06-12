from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import json
# Create your models here.
class Room(models.Model):
    code = models.CharField(max_length=8, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.code


class Message(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    user = models.CharField(max_length=200)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.user + " " + self.content

    @staticmethod
    def create_message(room_id, user, content):
        message = Message.objects.create(room_id=room_id, user=user, content=content)
        return message
    
@receiver(post_save, sender=Message)
def get_latest_message(sender, instance, created, **kwargs):
    if created:
        channel_layer = get_channel_layer()
        data = {
            "user": instance.user,
            "content": instance.content,
            "created_at": instance.created_at.isoformat(),
        }
        async_to_sync(channel_layer.group_send)(
            f"chat_{instance.room.code}",
            {
                "type": "chat_message",
                "value": json.dumps(data),
            }
        )