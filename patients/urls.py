# import path
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from patients.views import PatientViewSet

router = DefaultRouter()
router.register('patients', PatientViewSet)

urlpatterns = [
    path('', include(router.urls)),
]