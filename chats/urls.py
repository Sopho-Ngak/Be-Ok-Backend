from django.urls import path, include

from rest_framework.routers import DefaultRouter

from chats.views import ChatViewSet

router = DefaultRouter()

router.register('chats', ChatViewSet)

urlpatterns = [
    path('', include(router.urls)),
]