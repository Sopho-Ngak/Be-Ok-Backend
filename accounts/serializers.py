from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers
from django.utils import timezone

from accounts.models import User, VerificationCode, ProfilePicture
from accounts.tasks import send_activation_code_via_email
from utils.generate_code import get_random_code
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    default_error_messages = {
        'no_active_account': 'User not found or invalid credentials (Make sure your account is activated)',
    }
    def validate(self, attrs):
        data = super().validate(attrs)
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
    
class ProfilePictureSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProfilePicture
        fields = [
            'id',
            'user',
            'image',
            'created_at',
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
        # try:
        instance = ProfilePicture.objects.get(user=obj)
        request = self.context.get('request')
        url = request.build_absolute_uri(instance.image.url)
        # serializers = ProfilePictureSerializer(instance, context={"request":self.context}).data
        return url
        # except:
        #     return None
    
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


class SetNewPasswordSerializer(serializers.Serializer):
    password = serializers.CharField(min_length=8, write_only=True)
    code = serializers.CharField(min_length=4, write_only=True)

    def validate(self, attrs):
        if not VerificationCode.objects.filter(code=attrs.get('code')).exists():
            raise serializers.ValidationError("Code is not valid")
        return attrs
    

