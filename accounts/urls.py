# Django imports
from django.urls import path, include

# Third party apps
from rest_framework import routers

# Local imports
from accounts.views import (UserViewSet, UserLogin)

router = routers.DefaultRouter()


router.register('users', UserViewSet, basename='user')
router.register('login', UserLogin, basename='user-login')

urlpatterns = [
    path('', include(router.urls)),
]