# import serializers
from rest_framework import serializers
from patients.models import Patient, PatientReport, PatientDependentReport
from accounts.models import User
from accounts.serializers import UserInfoSerializer
from doctors.models import Doctor


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


class PatientReportSerializer(serializers.ModelSerializer):
    user = serializers.CharField(read_only=True)
    consultated_by_doctor = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    
    class Meta:
        model = PatientReport
        fields = [
            'id',
            'user',
            'symptoms',
            'consultated_by_doctor',
            'results',
            'created_at',
        ]
    def create(self, validated_data):
        user = self.context['request'].user
        if not validated_data.get('consultated_by_doctor'):
            dr_emile = Doctor.objects.get(user__username="Dr Emile")
        patient = Patient.objects.get(user=user)
        instance = PatientReport.objects.create(user=patient, consultated_by_doctor=dr_emile, **validated_data)
        return instance


class PatientDependentReportSerializer(serializers.ModelSerializer):
    user = serializers.CharField(read_only=True)
    consulted_by_doctor = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    dependent_relationship = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    class Meta:
        model = PatientDependentReport
        fields = [
            'id',
            'user',
            "dependent_names",
            "dependent_relationship",
            "dependent_age",
            "phone_number",
            "address",
            "email",
            "dependent_blood_group",
            "dependent_alergies",
            'dependent_symptoms',
            'consulted_by_doctor',
            'dependent_results',
            'created_at',
        ]

    def create(self, validated_data):
        user = self.context['request'].user
        if not validated_data.get('consultated_by_doctor'):
            dr_emile = Doctor.objects.get(user__username="Dr Emile")
        patient = Patient.objects.get(user=user)
        instance = PatientDependentReport.objects.create(
            user=patient, consulted_by_doctor=dr_emile, dependent_relationship=self.context['request'].GET.get("choice"), **validated_data)
        return instance


class PatientSerializer(serializers.ModelSerializer):
    patient_previous_reports = PatientReportSerializer(
        source="patient_reports", many=True, read_only=True)
    patient_dependents_repports = PatientDependentReportSerializer(
        source="patient_dependents", many=True, read_only=True)
    patient_personal_information = serializers.SerializerMethodField()

    class Meta:
        model = Patient
        fields = [
            'id',
            'user',
            'blood_group',
            'alergies',
            "patient_personal_information",
            'patient_previous_reports',
            'patient_dependents_repports',
        ]

    def get_patient_personal_information(self, obj):
        serializer = UserInfoSerializer(obj.user)
        return serializer.data
