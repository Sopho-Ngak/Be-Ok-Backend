from django.urls import path, include

from doctors.views import get_disease_groups


urlpatterns = [
    path('get-disease', get_disease_groups, name='disease-groups'),
]