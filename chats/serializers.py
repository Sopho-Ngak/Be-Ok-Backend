from django.db.models import Q

from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from accounts.serializers import UserInfoSerializer
from chats.models import Chat, Message
from accounts.models import User



class ChatSerializer(serializers.ModelSerializer):
    sender_info = serializers.SerializerMethodField()
    receiver_info = serializers.SerializerMethodField()
    sender= serializers.HiddenField(default=serializers.CurrentUserDefault())
    #message = serializers.CharField(required=False)

    class Meta:
        model = Chat
        fields = [
            'id',
            'sender',
            'sender_info',
            'receiver_info',
            'message_chat',
            'image_message',
            'voice_note',
            'video',
            'created_on',
        ]
        read_only_fields = ['receiver']

    def get_sender_info(self, obj):
        # user = User.objects.get(id=obj.sender.id)
        # print("################",user)
        return UserInfoSerializer(obj.sender, context=self.context).data
    
    def get_receiver_info(self, obj):
        # user = User.objects.get(id=obj.receiver.id)
        return UserInfoSerializer(obj.receiver, context=self.context).data

    def validate(self, attrs):
        if attrs['sender'] == attrs['receiver']:
            raise ValidationError("You can't send message to yourself")
        return attrs


class MessageSerializer(serializers.ModelSerializer):
    sender_info = serializers.SerializerMethodField()
    receiver_info = serializers.SerializerMethodField()
    # chats = serializers.SerializerMethodField()
    chats = serializers.SerializerMethodField()
    message = serializers.CharField(required=False)
    sender = serializers.HiddenField(default=serializers.CurrentUserDefault())
    receiver = serializers.CharField(required=True)
    image_message = serializers.ImageField(required=False)
    voice_note = serializers.FileField(required=False)
    video = serializers.FileField(required=False)

    class Meta:
        model = Message
        fields = [
            'id',
            'sender',
            'receiver',
            'sender_info',
            'receiver_info',
            'message',
            'image_message',
            'voice_note',
            'video',
            'chats',
            'created_on',
        ]
        read_only_fields = ['sender', 'receiver']

    def get_sender_info(self, obj: Message):
        # user = User.objects.get(id=obj.sender.id)
        # print("################",user)
        return UserInfoSerializer(obj.sender, context=self.context).data
    
    def get_receiver_info(self, obj: Message):
        # user = User.objects.get(id=obj.receiver.id)
        return UserInfoSerializer(obj.receiver, context=self.context).data
    
    def get_chats(self, obj: Message):
        return ChatSerializer(obj.chats.all(), many=True, context=self.context).data

    def validate(self, attrs: dict):
        if attrs['sender'] == attrs['receiver']:
            raise ValidationError("You can't send message to yourself")
        return attrs
    
    def create(self, validated_data: dict):

        if not validated_data.get('message') \
            and not validated_data.get('image_message') \
                and not validated_data.get('voice_note') \
                    and not validated_data.get('video'):
                raise ValidationError("You can not send empty message")

        try:
            receiver = User.objects.get(id=validated_data['receiver'])
        except User.DoesNotExist:
            raise ValidationError("Invalid receiver")
        
        validated_data['receiver'] = receiver
        try:
            previous_message = Message.objects.get(
                Q(sender=validated_data['sender'], receiver=validated_data['receiver']) |
                Q(sender=validated_data['receiver'], receiver=validated_data['sender']) 
            )
        except Message.DoesNotExist:
            # print(validated_data)
            previous_message = Message.objects.create(sender=validated_data['sender'], receiver=validated_data['receiver'])
            
        chat_instance = Chat.objects.create(
            sender=self.context['request'].user,
            receiver=validated_data['receiver'],
            message_chat=validated_data.get('message'),
            image_message=validated_data.get('image_message'),
            voice_note=validated_data.get('voice_note'),
            video=validated_data.get('video'),
        )
        previous_message.chats.add(chat_instance)
        return previous_message


        
        



