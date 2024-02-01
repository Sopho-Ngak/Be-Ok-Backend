from django.urls import path, include
from rest_framework import routers
from .views import get_disease_groups
  
urlpatterns = [
    path('disease-categories/', get_disease_groups, name='disease-categories'),
]