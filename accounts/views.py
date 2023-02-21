
# Third party imports
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import action

# Local imports
from accounts.serializers import (
    CustomTokenObtainPairSerializer, UserCreateSerializer, UserInfoSerializer)
from accounts.models import (User, VerificationCode)
from utils.generate_code import get_random_code


class UserLogin(viewsets.ViewSet):
    permission_classes = (AllowAny,)
    serializer_class = CustomTokenObtainPairSerializer

    def create(self, request):
        serializer = CustomTokenObtainPairSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data, status=status.HTTP_200_OK)


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
        return super().get_serializer_class()

    def get_permissions(self):
        if self.action == 'account_activation':
            self.permission_classes = (AllowAny,)
        if self.action == 'create':
            self.permission_classes = (AllowAny,)
        if self.action == 'edit_profile':
            self.permission_classes = (IsAuthenticated,)
        return super().get_permissions()

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'], url_path='account-activation')
    def account_activation(self, request):
        try:
            verification_code = VerificationCode.objects.get(
                code=request.data.get('code'))

            if verification_code.is_used:
                return Response({'message': 'OTP already used'}, status=status.HTTP_400_BAD_REQUEST)

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

    @action(detail=False, methods=['post'], url_path='resend-otp')
    def resend_verification_code(self, request):
        try:
            user = User.objects.get(email=request.data.get('email'))
            code = VerificationCode.objects.create(
                user=user, email=user.email, code=get_random_code(4))

            return Response({'message': 'OTP sent successfully'}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'message': 'Invalid email'}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'], url_path='edit-profile')
    def edit_profile(self, request):
        serializer = self.get_serializer(
            request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
