from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend


class EmailBackend(ModelBackend):
    '''
    this is used as the authentication backend which allows username, phone, or email as medium of recognising a user
    it extends the existing ModelBackend
    '''
    def authenticate(self, request, **kwargs):
        UserModel = get_user_model()
        try:

            # user_recognition stores the username, email or phone
            user_recognition = kwargs.get('email', None)

            if user_recognition is None:
                user_recognition = kwargs.get('username', None)

                if user_recognition is None:
                    user_recognition = kwargs.get('phone', None)

                    # checks for the existence of the specific email, phone, or username
                try:
                    user = UserModel.objects.get(email=user_recognition)
                except UserModel.DoesNotExist:
                    try:
                        user = UserModel.objects.get(username=user_recognition)

                    except UserModel.DoesNotExist:
                        try:
                            user = UserModel.objects.get(phone_number=user_recognition)
                            
                        except UserModel.DoesNotExist:
                            return None

            # cheks for the entered password 
            if user.check_password(kwargs.get('password', None)):
                return user

        except UserModel.DoesNotExist:
            return None
            
        return None