from django.urls import path, include

from rest_framework import routers

from chats.views import ChatViewSet

router = routers.DefaultRouter()

router.register('chats', ChatViewSet, basename='chat')

urlpatterns = [
    path('', include(router.urls)),
]