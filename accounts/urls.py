# Django imports
from django.urls import path, include

# Third party apps
from rest_framework import routers

# Local imports
from accounts.views import (UserViewSet, UserLogin)

router = routers.DefaultRouter()


router.register('user', UserViewSet, basename='user')
router.register('user/login', UserLogin, basename='user-login')

urlpatterns = [
    path('', include(router.urls)),
]