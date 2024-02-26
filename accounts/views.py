
# Third party imports
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import action

# Django imports
from django.conf import settings
from django.contrib.auth import update_session_auth_hash, logout

# Local imports
from accounts.serializers import (
    CustomTokenObtainPairSerializer,CustomTokenRefreshSerializer, UserCreateSerializer, UserInfoSerializer, ResetPasswordSerializer, 
    SetNewPasswordSerializer, ProfilePictureSerializer, ChangePasswordSerializer)
from accounts.models import (User, VerificationCode, ProfilePicture)
from utils.generate_code import get_random_code
from accounts.tasks import send_activation_code_via_email


class UserLogin(viewsets.ModelViewSet):
    permission_classes = (AllowAny,)
    serializer_class = CustomTokenObtainPairSerializer

    def get_serializer_class(self):
        if self.action == 'user_login':
            return CustomTokenObtainPairSerializer
        if self.action == 'refresh_token':
            return CustomTokenRefreshSerializer
        return super().get_serializer_class()
    
    def get_permissions(self):
        if self.action == 'user_logout':
            self.permission_classes = (IsAuthenticated,)
        return super().get_permissions()
    
    @action(detail=False, methods=['post'], url_path='login')
    def user_login(self, request):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['post'], url_path='refresh-token')
    def refresh_token(self, request):
        # try:
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data, status=status.HTTP_200_OK)
        # except Exception as e:
        #     return Response({'message': 'Invalid refresh token'}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'], url_path='logout')
    def user_logout(self, request):
        copy_user = request.user.username
        logout(request)
        return Response({'message': 'Logged out successfully', 'user': copy_user}, status=status.HTTP_200_OK)

    # def create(self, request):
    #     serializer = CustomTokenObtainPairSerializer(data=request.data)
    #     serializer.is_valid(raise_exception=True)
    #     return Response(serializer.validated_data, status=status.HTTP_200_OK)
        


class UserViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = UserCreateSerializer

    def get_serializer_class(self):
        if self.action == 'account_activation':
            return CustomTokenObtainPairSerializer
        if self.action == 'create':
            return UserCreateSerializer
        if self.action == 'edit_profile':
            return UserInfoSerializer
        elif self.action == "reset_password":
            if self.request.method == "POST" or self.request.method == "PUT":
                return ResetPasswordSerializer
            return SetNewPasswordSerializer
        elif self.action == 'profile_picture':
            return ProfilePictureSerializer
        elif self.action == 'change_password':
            return ChangePasswordSerializer
        return super().get_serializer_class()

    def get_permissions(self):
        if self.action in [
            'account_activation', 
            'reset_password',
            'create',
            'resend_verification_code'
            ]:
            self.permission_classes = (AllowAny,)
        # elif self.action == 'reset_password'
        # if self.action == 'create':
        #     self.permission_classes = (AllowAny,)
        # if self.action == 'edit_profile':
        #     self.permission_classes = (IsAuthenticated,)
        # if self.action == 'resend_verification_code':
        #     self.permission_classes = (AllowAny,)
        return super().get_permissions()

    def create(self, request):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            serializer.instance.set_password(serializer.validated_data['password'])
            serializer.instance.save()
            return Response({"message": "Account created successfully"}, status=status.HTTP_201_CREATED)
        
        # Custom error message to remove array from error message
        error_data = {}
        if serializer.errors.get('email'):
            error_data['email'] = serializer.errors.get('email')[0]
        if serializer.errors.get('phone_number'):
            error_data['phone_number'] = serializer.errors.get('phone_number')[0]
        if serializer.errors.get('username'):
            error_data['username'] = serializer.errors.get('username')[0]
            
        return Response(error_data, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'], url_path='account-activation')
    def account_activation(self, request):
        try:
            verification_code = VerificationCode.objects.get(
                code=request.data.get('code'))

            if verification_code.is_used:
                return Response({'message': 'OTP already used'}, status=status.HTTP_400_BAD_REQUEST)

            if verification_code.is_expired:
                verification_code.delete()
                return Response({'message': 'Verification code expired'}, status=status.HTTP_400_BAD_REQUEST)

            user = verification_code.user
            user.is_active = True
            user.save()
            token = self.get_serializer().get_token(user)
            verification_code.delete()
            return Response({
                'refresh': str(token),
                'access': str(token.access_token)}, status=status.HTTP_200_OK)

        except VerificationCode.DoesNotExist:
            return Response({'message': 'Invalid OTP'}, status=status.HTTP_400_BAD_REQUEST)
        
    @action(detail=False, methods=['post'], url_path='set-new-password')
    def change_password(self, request):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        try:
            user = User.objects.get(username=request.user.username)
            old_password = serializer.validated_data.get('old_password')
            if not user.check_password(old_password):
                return Response({'message': 'Invalid old password'}, status=status.HTTP_400_BAD_REQUEST)
            user.set_password(serializer.validated_data.get('new_password'))
            user.save() 
            return Response({'message': 'Password reset successful'}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'message': 'Invalid user'}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post', 'patch', 'put'], url_path='reset-password')
    def reset_password(self, request):
        if request.method == 'POST':
            serializer = self.get_serializer(data=request.data, context={'request': request})
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({'message': 'OTP sent successfully'}, status=status.HTTP_200_OK)
        
        elif request.method == 'PUT':
            try:
                code = VerificationCode.objects.get(code=request.data.get('code'))
                return Response({'message': 'verified'}, status=status.HTTP_200_OK)
            except VerificationCode.DoesNotExist:
                return Response({'message': 'Invalid OTP'}, status=status.HTTP_400_BAD_REQUEST)
        
        elif request.method == 'PATCH':

            try:
                serializer = self.get_serializer(data=request.data, context={'request': request})
                serializer.is_valid(raise_exception=True)
                verification_code = VerificationCode.objects.get(
                    code=request.data['code'])

                if verification_code.is_used:
                    return Response({'message': 'OTP already used'}, status=status.HTTP_400_BAD_REQUEST)

                if verification_code.is_expired:
                    verification_code.delete()
                    return Response({'message': 'Verification code expired'}, status=status.HTTP_400_BAD_REQUEST)

                user = verification_code.user
                user.set_password(request.data['password'])
                user.save()
                verification_code.delete()
                update_session_auth_hash(request, user)
                return Response({'message': 'Password reset successful'}, status=status.HTTP_200_OK)
            except VerificationCode.DoesNotExist:
                return Response({'message': 'Invalid OTP'}, status=status.HTTP_400_BAD_REQUEST)


    @action(detail=False, methods=['post'], url_path='resend-verfication-code')
    def resend_verification_code(self, request):
        try:
            if not request.data.get('email'):
                return Response({'message': 'Email is required'}, status=status.HTTP_400_BAD_REQUEST)
            user = User.objects.get(email=request.data.get('email'))
            
            # Delete all existing verification code for the user
            VerificationCode.objects.filter(user=user).delete()
            new_opt = VerificationCode.objects.create(
                user=user, email=user.email, code=get_random_code(4))
            send_activation_code_via_email(new_opt.id)

            return Response({'message': 'OTP sent successfully'}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'message': 'Invalid email'}, status=status.HTTP_400_BAD_REQUEST)
        
   

    @action(detail=False, methods=['post'], url_path='edit-profile')
    def edit_profile(self, request):
        serializer = self.get_serializer(
            request.user, data=request.data, partial=True, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    
    @action(detail=False, methods=['post', 'delete', 'get'], url_path='profile-picture')
    def profile_picture(self, request):

        profile_picture_instance, _ = ProfilePicture.objects.get_or_create(user=request.user)

        if request.method == 'GET':
            serializer = self.get_serializer(profile_picture_instance, context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        if request.method == 'POST':
            serializer = self.get_serializer(
                profile_picture_instance, data=request.data, partial=True, context={'request': request})
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        elif request.method == 'DELETE':
            profile_picture_instance.delete()
            default_image = ProfilePicture.objects.create(user=request.user)
            serializer = self.get_serializer(default_image, context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)
