from email.mime import image
import uuid
from django.db import models
from doctors.models import Doctor
from patients.models import Patient
from accounts.models import User
from django.utils.translation import gettext_lazy as _
from cloudinary.models import CloudinaryField

def chat_upload_path(instance, filename):
    return '/'.join(['chats', f"sender-{instance.sender.username}/receiver-{instance.receiver.username}", filename])


class Chat(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    sender = models.ForeignKey(
        User, on_delete=models.SET_NULL, related_name="message_sender", blank=True, null=True
    )
    receiver = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="message_receiver"
    )
    message_chat = models.TextField(null=True, blank=True)
    image_message = models.ImageField(upload_to=chat_upload_path, null=True, blank=True)
    voice_note = CloudinaryField('media', resource_type='video', null=True, blank=True)
    display = models.BooleanField(default=True)
    read = models.BooleanField(default=False)
    created_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("Message")
        verbose_name_plural = _("Messages")
        ordering = ('-created_on', )

class Message(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    sender = models.ForeignKey(
        User, on_delete=models.SET_NULL, related_name="user_sender", blank=True, null=True
    )
    receiver = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="user_receiver", blank=True, null=True
    )
    chats = models.ManyToManyField(
        Chat, blank=True, related_name="users_chat"
    )
    created_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("Chat")
        verbose_name_plural = _("Chats")
        ordering = ('-created_on', )

    def __str__(self):
        return f"{self.sender} - {self.receiver}"