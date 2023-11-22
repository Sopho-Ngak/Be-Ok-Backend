from django.shortcuts import render
from django.conf import settings
from django.db.models import Q


from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from chats.models import Chat, Message
from chats.serializers import ChatSerializer, MessageSerializer


class ChatViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    # queryset = Message.objects.all()
    serializer_class = MessageSerializer

    def get_queryset(self, *args, **kwargs):
        chat_id = self.kwargs.get('chat_id')
        if chat_id:
            try:
                messae_chat = Message.objects.get(id=chat_id)
                serializer = self.get_serializer(messae_chat)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except Message.DoesNotExist:
                return Response({"message": "Message not found"}, status=status.HTTP_404_NOT_FOUND)
            # message_chats = Message.objects.filter(
            #     Q(user=request.user) | Q(receiver=request.user)
            # )
            # serializer = self.get_serializer(message_chats, many=True)
            # return Response(serializer.data, status=status.HTTP_200_OK)
        q = Message.objects.filter(
            Q(sender=self.request.user) | Q(receiver=self.request.user)
        )
        return q

    def get_serializer_class(self):
        match self.action:
            case 'chat':
                return ChatSerializer
        return super().get_serializer_class()
    
    def get_permissions(self):
        return super().get_permissions()
    
    @action(detail=False, methods=['post', 'patch'], url_path='(?P<chat_id>[^/.]+)')
    def chat(self, request, chat_id=None):
        if request.method == 'POST':
            serializer = self.get_serializer(data=request.data, context={'request': request})
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

