from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers

from accounts.models import User

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        refresh = self.get_token(self.user)
        data['refresh'] = str(refresh)
        data['access'] = str(refresh.access_token)
        return data

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['username'] = user.username
        token['full_name'] = user.full_name
        token['email'] = user.email
        token['phone_number'] = user.phone_number
        token['address'] = user.address
        token['user_type'] = user.user_type
        return token


class UserCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'username', 
            'full_name', 
            'email', 
            'phone_number', 
            'address',
            'user_type', 
            'password'
            ]
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        if not validated_data.get('username'):
            validated_data['username'] = validated_data.get('email').split('@')[0]
        user = User.objects.create(**validated_data)
        return user

class UserInfoSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(read_only=True)
    user_type = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'full_name',
            'email',
            'phone_number',
            'address',
            'user_type',
            'about_me',
            'user_type',
        ]