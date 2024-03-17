from django.urls import path, include
from rest_framework import routers

from hospital.views import HospitalViewSet

router = routers.DefaultRouter()

router.register('hospitals', HospitalViewSet)

urlpatterns = [
    path('', include(router.urls)),
]