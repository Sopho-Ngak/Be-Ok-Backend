from django.conf import settings

from google.oauth2 import id_token
from google.auth.transport import requests as google_requests


from accounts.models import User
from accounts.serializers import CustomTokenObtainPairSerializer


class GoogleAuth:
    def __init__(self):
        self.client_id = settings.GOOGLE_CLIENT_ID
        self.auth_url = "https://www.googleapis.com/oauth2/v2/userinfo"

    def _auth_with_id_token(self, access_token) -> dict | None:
        try:
            id_info = id_token.verify_oauth2_token(
                access_token, google_requests.Request(), self.client_id
            )
            return id_info
        except Exception as e:
            print(e)
            return None

    def _auth_with_access_token(self, access_token) -> dict | None:

        response = google_requests.requests.get(
            self.auth_url, headers={"Authorization": f"Bearer {access_token}"}
        )

        if response.status_code != 200:
            return None
        json_data = response.json()
        # print(json_data)
        return json_data

    def login(self, token: str, auth_type: str, user_type) -> dict | None:
        if auth_type == "id_token":
            user_info = self._auth_with_id_token(token)
        else:
            user_info = self._auth_with_access_token(token)

        if not user_info:
            return None

        email: str = user_info["email"]
        full_name = user_info["name"]
        username = email.split("@")[0]

        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                "username": username,
                "full_name": full_name,
                "user_type": user_type,
            },
        )

        if created:
            user.set_unusable_password()
            user.is_active = True
            user.save()

        jwt_token = CustomTokenObtainPairSerializer().get_token(user)

        data = {
            "refresh": str(jwt_token),
            "access": str(jwt_token.access_token),
            "user_type": user.user_type,
        }

        return data
