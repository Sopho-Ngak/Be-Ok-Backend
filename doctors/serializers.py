from django.utils import timezone
# import serializers
from rest_framework import serializers
from patients.models import Patient, PatientReport, PatientDependentReport, ONLINE
from accounts.models import User
from accounts.serializers import UserInfoSerializer
from doctors.models import Doctor


from doctors.models import DiseaseGroup, Disease


class DiseaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Disease
        fields = [
            'id', 
            'name', 
            'icon', 
            'created_at'
            ]


class DiseaseGroupSerializer(serializers.ModelSerializer):
    diseases = DiseaseSerializer(
        source="disease_description", many=True, read_only=True)

    class Meta:
        model = DiseaseGroup
        fields = [
            'id', 
            'name',
            'diseases', 
            'created_at', 
            ]