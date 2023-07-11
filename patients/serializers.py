# import serializers
from rest_framework import serializers
from patients.models import Patient, PatientReport, PatientDependentReport, ONLINE
from accounts.models import User
from accounts.serializers import UserInfoSerializer
from doctors.models import Doctor

from utils.payment_module import Payment


class PatientInfoSerializer(serializers.ModelSerializer):
    personal_information = serializers.SerializerMethodField()

    class Meta:
        model = Patient
        fields = [
            # 'id',
            # 'patient_username',
            'blood_group',
            'alergies',
            'chronic_diseases',
            'habits',
            'current_prescription',
            'is_pregnant',
            'created_at',
            'personal_information',
        ]
    def get_personal_information(self, obj):
        user = User.objects.get(username=obj)
        serializer = UserInfoSerializer(user)

        return serializer.data

import uuid
class PatientReportSerializer(serializers.ModelSerializer):
    consultated_by_doctor = serializers.UUIDField(required=False, allow_null=True)
    patient_username = serializers.UUIDField(required=False, allow_null=True)

    class Meta:
        model = PatientReport
        fields = [
            'id',
            'patient_username',
            'pain_area',
            'symptoms',
            'consultated_by_doctor',
            'consultation_type',
            'results',
            'prescription',
            'recommended_tests',
            'recommendation',
            'created_at',
        ]
    def create(self, validated_data):
        patient_id = validated_data.pop('patient_username', None)
        doctor = validated_data.pop('consultated_by_doctor', None)
        
        if not patient_id:
            try:
                user_id = self.context['request'].user.id
                patient = Patient.objects.get(patient_username__id=str(user_id))
            except Patient.DoesNotExist:
                raise serializers.ValidationError("Patient not found")
            
        elif patient_id and not doctor:
            doctor = self.context['request'].user.id
            patient = Patient.objects.get(id=str(patient_id))
        else:
            # AI consultation
            try:
                patient = Patient.objects.get(id=str(patient_id))
            except User.DoesNotExist:
                raise serializers.ValidationError("Patient not found")
            

        if not doctor:
            doctor, created = User.objects.get_or_create(username="Dr Emile", user_type=User.DOCTOR)
            consultated_by = Doctor.objects.get(user=doctor)
        else:
            # consultated_by = validated_data.get('consultated_by_doctor')
            try:
                consultated_by = Doctor.objects.get(user__id=str(doctor))
                if not validated_data.get('consultation_type'):
                    validated_data['consultation_type'] = ONLINE
            except Doctor.DoesNotExist:
                raise serializers.ValidationError("Only doctors can consult patients")

        if consultated_by.user == patient.patient_username:
            raise serializers.ValidationError("You can't consult yourself.")

        instance = PatientReport.objects.create(patient_username=patient, consultated_by_doctor=consultated_by, **validated_data)
        return instance


class PatientDependentReportSerializer(serializers.ModelSerializer):
    # user = serializers.CharField(read_only=True)
    consulted_by_doctor = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    dependent_relationship = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    patient_username = serializers.UUIDField(required=False, allow_null=True)
    
    class Meta:
        model = PatientDependentReport
        fields = [
            'id',
            'patient_username',
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
            'consultation_type',
            'dependent_results',
            'dependent_prescription',
            'dependent_recommended_tests',
            'dependent_recommendation',
            'created_at',
        ]

    def create(self, validated_data):
        user_id = self.context['request'].user.id
        account_holder = validated_data.pop('patient_username', None)

        if not account_holder:
            # AI consultation
            doctor, created = User.objects.get_or_create(username="Dr Emile", user_type=User.DOCTOR)
            consultated_by = Doctor.objects.get(user=doctor)

            patient = Patient.objects.get(patient_username__id=user_id)

        elif account_holder:
            consultated_by = self.context['request'].user.id
            try:
                consultated_by = Doctor.objects.get(user__id=str(consultated_by))
                patient = Patient.objects.get(id=str(account_holder))
                if not validated_data.get('consultation_type'):
                    validated_data['consultation_type'] = ONLINE
            except Patient.DoesNotExist:
                raise serializers.ValidationError("Patient not found")
            except Doctor.DoesNotExist:
                raise serializers.ValidationError("Only doctors can consult patients")
        else:
            raise serializers.ValidationError("A dependee should have dependents who is the account holder")            
        
        # if not validated_data.get('consultated_by_doctor'):
        #     doctor, created = User.objects.get_or_create(username="Dr Emile", user_type=User.DOCTOR)
        #     consultated_by = Doctor.objects.get(user=doctor)
        # else:
        #     consultated_by = validated_data.get('consultated_by_doctor')

        # patient = Patient.objects.get(patient_username=user)
        instance = PatientDependentReport.objects.create(
            patient_username=patient, consulted_by_doctor=consultated_by, dependent_relationship=self.context['request'].GET.get("choice"), **validated_data)
        return instance


class PatientSerializer(serializers.ModelSerializer):
    patient_previous_reports = PatientReportSerializer(
        source="patient_reports", many=True, read_only=True)
    patient_dependents_repports = PatientDependentReportSerializer(
        source="patient_dependents", many=True, read_only=True)
    # patient_personal_information = serializers.SerializerMethodField()
    patient_profile = serializers.SerializerMethodField()

    class Meta:
        model = Patient
        fields = [
            'id',
            # "patient_personal_information",
            "patient_profile",
            'patient_previous_reports',
            'patient_dependents_repports',
        ]

    # def get_patient_personal_information(self, obj):
    #     serializer = UserInfoSerializer(obj.patient_username)
    #     return serializer.data
    
    def get_patient_profile(self, obj):
        serializer = PatientInfoSerializer(obj.patient_username)
        return serializer.data

class PatientEditProfileSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)

    def validate(self, attrs):
        if self.context['request'].user.gender == User.MALE:
            if attrs.get('is_pregnant'):
                raise serializers.ValidationError("You can't be pregnant")
        return super().validate(attrs)
    
    class Meta:
        model = Patient
        fields = [
            'id',
            'patient_username',
            'blood_group',
            'alergies',
            'chronic_diseases',
            'habits',
            'current_prescription',
            'is_pregnant',
        ]
    
class PatientPaymentStatusSerializer(serializers.Serializer):
    reference_key = serializers.CharField(required=True)
    kind = serializers.CharField(required=True)
    phone_number = serializers.CharField(required=True, max_length=10)

    def validate(self, data):
        if data.get('kind').upper() not in ['CASHIN', 'CASHOUT']:
            raise serializers.ValidationError("Invalid kind")
        return data

class PatientCashInSerializer(serializers.Serializer):
    phone_number = serializers.CharField(required=True, max_length=10)
    amount = serializers.IntegerField(required=True)

    def validate(self, data):
        if not data.get('phone_number').isdigit() :
            raise serializers.ValidationError("Enter a valid phone number please")
        return data

    