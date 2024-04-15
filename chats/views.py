from django.conf import settings
from django.db.models import Q


from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from chats.models import Message
from chats.serializers import MessageSerializer


class ChatViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Message.objects.all()
    serializer_class = MessageSerializer

    def get_serializer_class(self):
        match self.action:
            case 'chat':
                return MessageSerializer
        return super().get_serializer_class()

    def get_permissions(self):
        return super().get_permissions()

    @action(detail=False, methods=['post', 'patch', 'get'], url_path='message_chat')
    def chat(self, request, *args, **kwargs):
        '''
        This view handle all the chat module from iniating to getting chats
        '''
        if request.method == 'GET':
            message_id = self.request.query_params.get('message_id')
            if message_id:
                try:
                    messae_chat = Message.objects.get(id=message_id)
                    serializer = self.get_serializer(
                        messae_chat, context={'request': request})
                    return Response(serializer.data, status=status.HTTP_200_OK)
                except Message.DoesNotExist:
                    return Response({"message": "Message not found"}, status=status.HTTP_404_NOT_FOUND)

            q = Message.objects.filter(
                Q(sender=self.request.user) | Q(receiver=self.request.user)
            )
            serializer = self.get_serializer(
                q, context={'request': request}, many=True)

            return Response(serializer.data, status=status.HTTP_200_OK)

        if request.method == 'POST':
            serializer = self.get_serializer(
                data=request.data, context={'request': request})
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
