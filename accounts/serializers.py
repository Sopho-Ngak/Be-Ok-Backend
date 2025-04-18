from random import choice
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenRefreshSerializer
from rest_framework import serializers, exceptions
from django.utils import timezone
from django.contrib.auth.password_validation import validate_password
from django.core import exceptions as django_exceptions
from django.contrib.auth import authenticate

from accounts.models import User, VerificationCode, ProfilePicture
from accounts.tasks import send_activation_code_via_email
from utils.generate_code import get_random_code
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):

    def validate(self, attrs):
        data = {}
        authenticate_kwargs = {
            self.username_field: attrs[self.username_field],
            "password": attrs["password"],
        }
        try:
            authenticate_kwargs["request"] = self.context["request"]
        except KeyError:
            pass

        self.user = authenticate(**authenticate_kwargs)

        if not self.user or not self.user.is_active:
            raise serializers.ValidationError({
                "login_error": "Email/username or password is incorrect",
                }
            )

        data['user_short_detail'] = {
            'id': self.user.id,
            'username': self.user.username,
            'full_name': self.user.full_name,
            'email': self.user.email,
            'phone_number': self.user.phone_number,
            'address': self.user.address,
            'user_type': self.user.user_type,
        }
        
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
    
class GoogleLoginSerializer(serializers.Serializer):
    google_id_token = serializers.CharField(write_only=True, required=False)
    google_access_token = serializers.CharField(write_only=True, required=False)
    user_type = serializers.CharField(write_only=True, required=True)

    def validate(self, attrs):
        if attrs.get('user_type') not in ['patient', 'doctor']:
            raise serializers.ValidationError("Invalid user type. choce from ['patient', 'doctor']")
        
        if not attrs.get('google_id_token') and not attrs.get('google_access_token'):
            raise serializers.ValidationError("Either google_id_token or google_access_token is required")
        
        if not self.context['request'].query_params.get('auth_type'):
            raise serializers.ValidationError("query param auth_type is required")
        
        elif self.context['request'].query_params.get('auth_type') not in ['id_token', 'access_token']:
            raise serializers.ValidationError("Invalid value for auth_type. Choose from ['id_token', 'access_token']")
        
        if self.context['request'].query_params.get('auth_type') == 'id_token':
            if not attrs.get('google_id_token'):
                raise serializers.ValidationError("google_id_token is required")
        else:
            if not attrs.get('google_access_token'):
                raise serializers.ValidationError("google_access_token is required")
        return attrs

class CustomTokenRefreshSerializer(TokenRefreshSerializer):
    pass

class UserCreateSerializer(serializers.ModelSerializer):
    # fcm_token = serializers.CharField(write_only=True, required=False)
    # device_type = serializers.CharField(write_only=True, required=False)
    # device_id = serializers.CharField(write_only=True, required=False)
    # device_name = serializers.CharField(write_only=True, required=False)
    username = serializers.CharField(
        max_length=255, 
        required=False, 
        allow_blank=True,
        help_text="Optional, if not provided will be generated from email"
    )
    class Meta:
        model = User
        fields = [
            'username', 
            'full_name', 
            'email', 
            'phone_number', 
            'address',
            # 'user_type',
            'gender',
            'marital_status',
            'date_of_birth',
            # 'fcm_token',
            # 'device_type',
            # 'device_id',
            # 'device_name', 
            'password'
            ]
        extra_kwargs = {'password': {'write_only': True}}

    # def validate(self, attrs: dict):
    #     if User.objects.filter(email=attrs.get('email')).exists():
    #         raise serializers.ValidationError("Email already exists")
    #     username: str = attrs.get('username')
    #     if username.isnumeric():
    #         raise serializers.ValidationError("Username cannot be all numbers")
    #     if len(username.split()) > 1:
    #         raise serializers.ValidationError("Username cannot contain spaces and must be a single word") 
        
    #     fcm_token = attrs.get('fcm_token')
    #     device_type = attrs.get('device_type')
    #     device_id = attrs.get('device_id')
    #     device_name = attrs.get('device_name')
    #     if fcm_token and device_type and device_id and device_name:
    #         del attrs['fcm_token']
    #         del attrs['device_type']
    #         del attrs['device_id']
    #         del attrs['device_name']

    #     user = User(**attrs)
    #     password = attrs.get("password")
    #     try:
    #         validate_password(password, user)
    #     except django_exceptions.ValidationError as e:
    #         serializer_error = serializers.as_serializer_error(e)
    #         raise serializers.ValidationError(
    #             {"password": serializer_error["non_field_errors"]}
    #         )
    #     return attrs
    
    def create(self, validated_data):
        if not validated_data.get('username'):
            validated_data['username'] = validated_data.get('email').split('@')[0]
        user = User.objects.create(**validated_data)
        return user


    # def create(self, validated_data: dict):
    #     if validated_data.get('device_id') and validated_data.get('fcm_token') and validated_data.get('device_id') and validated_data.get('device_name'):
    #         device_id = validated_data.pop('device_id')
    #         fcm_token = validated_data.pop('fcm_token')
    #         device_type = validated_data.pop('device_type')
    #         device_name = validated_data.pop('device_name')
    #         created = super().create(validated_data)
    #         if fcm_token and device_type and device_id and device_name:
    #             FCMDevice.objects.create(
    #                 user=created,
    #                 name=device_name,
    #                 device_id=device_id,
    #                 registration_id=fcm_token,
    #                 type=device_type
    #             )
    #         return created
    #     else:
    #         return super().create(validated_data)
    
class ProfilePictureSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProfilePicture
        fields = [
            'id',
            # 'user',
            'image',
            # 'created_at',
        ]


class UserInfoSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(read_only=True)
    user_type = serializers.CharField(read_only=True)
    age = serializers.SerializerMethodField(read_only=True)
    profile_image = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'profile_image',
            'full_name',
            'email',
            'phone_number',
            'address',
            'user_type',
            'is_active',
            'about_me',
            'gender',
            'marital_status',
            'date_of_birth',
            'age',

        ]

    def get_age(self, obj):
        if obj.date_of_birth:
            return timezone.now().year - obj.date_of_birth.year
        return None
    
    def get_profile_image(self, obj):
        request = self.context.get('request')
        url = request.build_absolute_uri(obj.profile_picture.image.url)
        return url

    
class ResetPasswordSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)

    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email does not exists")
        return value
    
    class Meta:
        model = VerificationCode
        fields = [
            'email',
        ]

    def create(self, validated_data):
        user = User.objects.get(email=validated_data.get('email'))
        verification_code = VerificationCode.objects.create(
            user=user, code=get_random_code(4))
        send_activation_code_via_email(id=verification_code.id, reset_pass=True)
        return verification_code

    
class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(min_length=8, write_only=True)
    new_password = serializers.CharField(min_length=8, write_only=True)
    confirm_password = serializers.CharField(min_length=8, write_only=True)

    def validate(self, attrs):
        if attrs.get('new_password') != attrs.get('confirm_password'):
            raise serializers.ValidationError("Passwords do not match")
        return attrs

class SetNewPasswordSerializer(serializers.Serializer):
    password = serializers.CharField(min_length=8, write_only=True)
    code = serializers.CharField(min_length=4, write_only=True)

    # def validate(self, attrs):
    #     if not VerificationCode.objects.filter(code=attrs.get('code')).exists():
    #         raise serializers.ValidationError("Code is not valid")
    #     return attrs
    

