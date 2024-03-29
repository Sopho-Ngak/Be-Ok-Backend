from django.urls import path, include
from rest_framework import routers
from .views import get_disease_groups, RatingViewSets

router = routers.DefaultRouter()
router.register('rating', RatingViewSets)
  
urlpatterns = [
    path('disease', get_disease_groups, name='disease'),
    path('', include(router.urls)),
]