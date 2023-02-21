#import serializers
from rest_framework import serializers
from patients.models import Patient
from accounts.models import User
from accounts.serializers import UserInfoSerializer

class PatientInfoSerializer(serializers.ModelSerializer):
    personal_information = serializers.SerializerMethodField()
    class Meta:
        model = Patient
        fields = [
            'personal_information', 
            'blood_group', 
            'alergies', 
            'created_at'
            ]

    def get_personal_information(self, obj):
        user = User.objects.get(id=obj.user.id)
        serializer = UserInfoSerializer(user)
        return serializer.data

class PatientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = ('name', 'symptoms', 'results', 'created_at')