from django.utils import timezone
# import serializers
from rest_framework import serializers
from patients.models import (
    Patient, PatientReport, PatientDependentReport, ONLINE, Appointement, CONSULTATION_TYPE,
    PatientPrescriptionForm, DependentsPrescriptionForm, PatientLabTest,
    DependentsLabTest, PatientRecommendation, DependentsRecommendation)
from accounts.models import User
from accounts.serializers import UserInfoSerializer
from doctors.models import Doctor, DoctorAvailability
from doctors.serializers import MinimumDoctorInfoSerializer, DoctorAvailabilitySerializer

from utils.payment_module import Payment


class DependeeInfoSerializer(serializers.ModelSerializer):
    age = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = PatientDependentReport
        fields = [
            'id',
            'dependent_names',
            'dependent_relationship',
            'dependent_bithdate',
            'age',
            'gender',
            'dependent_blood_group',
            # 'chronic_diseases',
            'dependent_alergies',
            'phone_number',
            'email',
            'address',
            'created_at',
        ]

    def get_age(self, obj):
        if obj.dependent_bithdate:
            return  timezone.now().year - obj.dependent_bithdate.year
        return None


class PatientInfoSerializer(serializers.ModelSerializer):
    personal_information = serializers.SerializerMethodField()
    dependents_profile = DependeeInfoSerializer(
        source="patient_dependents", many=True, read_only=True)

    class Meta:
        model = Patient
        fields = [
            'id',
            # 'patient_username',
            'blood_group',
            'alergies',
            'chronic_diseases',
            'habits',
            'current_prescription',
            'is_pregnant',
            'created_at',
            'personal_information',
            'dependents_profile',
        ]

    def get_personal_information(self, obj):
        user = User.objects.get(username=obj)
        serializer = UserInfoSerializer(user, context=self.context)

        return serializer.data
    

class MinumumPatientInfoSerializer(PatientInfoSerializer):

    class Meta:
        model = Patient
        fields = [
            'id',
            'blood_group',
            'alergies',
            'chronic_diseases',
            'habits',
            'current_prescription',
            'is_pregnant',
            'personal_information',
            'created_at',
        ]



class PatientReportSerializer(serializers.ModelSerializer):
    consulted_by_doctor = serializers.UUIDField(required=False, allow_null=True, read_only=True)
    patient_username = serializers.UUIDField(required=False, allow_null=True, read_only=True)
    personal_information = serializers.SerializerMethodField()

    class Meta:
        model = PatientReport
        fields = [
            'id',
            'patient_username',
            'personal_information',
            'pain_area',
            'symptoms',
            'consulted_by_doctor',
            'consultation_type',
            'results',
            'prescription',
            'recommended_tests',
            'recommendation',
            'medical_form',
            'is_paid',
            'status',
            'created_at',
        ]

    def get_personal_information(self, obj):
        user = User.objects.get(username=obj)
        profile_serializer = UserInfoSerializer(user, context=self.context)
        medical_serializer = PatientEditProfileSerializer(obj.patient_username, context=self.context)
        data = {
            "profile": profile_serializer.data,
            "medical": medical_serializer.data
        }

        return data



class PatientDependentReportSerializer(serializers.ModelSerializer):
    # user = serializers.CharField(read_only=True)
    consulted_by_doctor = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    dependent_relationship = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    patient_username = serializers.UUIDField(required=False, allow_null=True, read_only=True)
    account_holder = serializers.SerializerMethodField()
    
    class Meta:
        model = PatientDependentReport
        fields = [
            'id',
            'patient_username',
            'account_holder',
            "dependent_names",
            "dependent_relationship",
            "dependent_bithdate",
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
            'medical_form',
            'is_paid',
            'status',
            'created_at',
        ]
    
    def get_account_holder(self, obj):
        user = User.objects.get(username=obj)
        serializer = UserInfoSerializer(user, context=self.context)

        return serializer.data

class PatientSerializer(serializers.ModelSerializer):
    patient_previous_reports = serializers.SerializerMethodField()
    patient_dependents_repports = serializers.SerializerMethodField()
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
        serializer = PatientInfoSerializer(obj.patient_username, context=self.context)
        return serializer.data
    
    def get_patient_previous_reports(self, obj):
        paid_reports_instance = PatientReport.objects.filter(patient_username=obj, is_paid=True)
        serializer = PatientReportSerializer(paid_reports_instance, many=True, context=self.context)
        return serializer.data
    
    def get_patient_dependents_repports(self, obj):
        paid_reports_instance = PatientDependentReport.objects.filter(patient_username=obj, is_paid=True)
        serializer = PatientDependentReportSerializer(paid_reports_instance, many=True, context=self.context)
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

class UpdateAppointmentSerializer(serializers.ModelSerializer):
    status = serializers.ChoiceField(choices=Appointement.APPOINTEMENT_STATUS)
    rejection_reason = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    pain_area = serializers.CharField(read_only=True)
    describe_disease = serializers.CharField(read_only=True)
    is_paid = serializers.CharField(read_only=True)

    def validate(self, attrs):
        if attrs.get('status') == Appointement.REJECTED and not attrs.get('rejection_reason'):
            raise serializers.ValidationError("Kindly provide the reason of your rejection to notify the patient")
        
        if attrs.get('status') and attrs.get('status') not in [Appointement.ACCEPTED, Appointement.REJECTED]:
            raise serializers.ValidationError("Doctor can only accept or reject an appointmentbb")
        
        # if attrs.get('state') and attrs.get('state') not in [Appointement.INPROGRESS, Appointement.COMPLETED]:
        #     raise serializers.ValidationError("appointment can only be in progress or completed state")
        # appoint_instance = Appointement.objects.get(id=attrs.get('id'))
        
        # if request.data.get('state') and appointment.status != Appointement.ACCEPTED:
        #     raise serializers.ValidationError("Denied: Appointment is not accepted yet")
        return super().validate(attrs)
    

    class Meta:
        model = Appointement
        fields = [
            "id",
            "status",
            "state",
            "is_paid",
            "pain_area",
            "describe_disease",
            "rejection_reason",
        ]

    # def update(self, instance, validated_data):
    #     status = validated_data.get('status')
    #     rejection_reason = validated_data.get('rejection_reason')
    #     if status == Appointement.REJECTED and not rejection_reason:
    #         raise serializers.ValidationError("Kindly provide the reason of your rejection to notify the patient")
    #     instance.status = status
    #     instance.rejection_reason = rejection_reason
    #     instance.save()
    #     return instance

class AppointmentSerializer(serializers.ModelSerializer):
    is_paid = serializers.BooleanField(read_only=True)
    # status = serializers.CharField(read_only=True)
    rejection_reason = serializers.CharField(read_only=True)
    service = serializers.ChoiceField(choices=Appointement.SERVICE_CHOICES)
    consultation_type = serializers.ChoiceField(choices=CONSULTATION_TYPE)
    patient = serializers.UUIDField(default=serializers.CurrentUserDefault())
    patient_profile = serializers.SerializerMethodField()
    doctor_profile = serializers.SerializerMethodField()
    doctor_availability_details = serializers.SerializerMethodField()
    appointement_happen_in = serializers.SerializerMethodField()

    def validate(self, attrs):
        if attrs.get('status') != Appointement.CANCELLED:
            raise serializers.ValidationError("Denied: A patient can only cancel an appointment")
        return super().validate(attrs)
    
    class Meta:
        model = Appointement
        fields = [
            "id",
            "patient",
            "patient_profile",
            "doctor",
            "doctor_profile",
            "doctor_availability_details",
            "service",
            "consultation_type",
            "describe_disease",
            "doctor_availability",
            "is_paid",
            "pain_area",
            "status",
            "state",
            "rejection_reason",
            "appointement_happen_in",
            "created_at",
        ]

    
    def create(self, validated_data):

        try:
            available = validated_data.get('doctor').doctor_availabilities.get(id=validated_data.get('doctor_availability').id, is_booked=False)
            patient = Patient.objects.get(patient_username__id=validated_data.get('patient').id)
        except DoctorAvailability.DoesNotExist:
            raise serializers.ValidationError("Doctor availability not found or already booked")
        except Patient.DoesNotExist:
            raise serializers.ValidationError("Patient not found")
        
        appointment = Appointement.objects.create(
            doctor=validated_data.get('doctor'),
            patient=patient,
            doctor_availability=available,
            service=validated_data.get('service'),
            consultation_type=validated_data.get('consultation_type'),
            describe_disease=validated_data.get('describe_disease'),
        )
        available.is_booked = True
        available.save()
        
        return appointment
    
    def get_doctor_profile(self, obj):
        serializer = MinimumDoctorInfoSerializer(obj.doctor, context=self.context)
        return serializer.data
    
    def get_patient_profile(self, obj):
        serializer = MinumumPatientInfoSerializer(obj.patient, context=self.context)
        return serializer.data
    
    def get_doctor_availability_details(self, obj):
        serializer = DoctorAvailabilitySerializer(obj.doctor_availability, context=self.context)
        return serializer.data
    
    def get_appointement_happen_in(self, obj):
        if obj.status == Appointement.ACCEPTED:
            return obj.happend_in()
        return "Appointment not confirmed by doctor yet"
    
class PatientAppointmentInfoSerializer(serializers.ModelSerializer):
    doctor_profile = serializers.SerializerMethodField()
    doctor_availability_details = serializers.SerializerMethodField()
    appointement_happen_in = serializers.SerializerMethodField()
    

    class Meta:
        model = Appointement
        fields = [
            "id",
            "service",
            "consultation_type",
            "consultation_note",
            "is_confirmed",
            "created_at",
            "doctor_profile",
            "doctor_availability"
            

        ]

    def get_doctor_profile(self, obj):
        serializer = MinimumDoctorInfoSerializer(obj.doctor, context=self.context)
        return serializer.data
    
    def getdoctor_availability_details(self, obj):
        serializer = DoctorAvailabilitySerializer(obj.doctor_availability, context=self.context)
        return serializer.data
    
    def get_appointement_happen_in(self, obj):
        return obj.happend_in()
    
class DoctorAppointmentInfoSerializer(serializers.ModelSerializer):
    patient = serializers.SerializerMethodField()
    doctor_availability = serializers.SerializerMethodField()
    appointment_happend_in = serializers.SerializerMethodField()
    class Meta:
        model = Appointement
        fields = [
            'id',  
            'doctor', 
            'service', 
            'consultation_type', 
            'describe_disease',
            "appointment_happend_in",
            'is_paid',
            'pain_area',
            'state',
            'status',
            'created_at', 
            'doctor_availability', 
            'patient', 
            ]
    
    def get_patient(self, obj):
        serializer = MinumumPatientInfoSerializer(obj.patient, context=self.context)
        return serializer.data
    

    
    def get_doctor_availability(self, obj):
        serializer = DoctorAvailabilitySerializer(obj.doctor_availability)
        return serializer.data
    
    def get_appointment_happend_in(self, obj):
        return obj.happend_in()


class PatientPrescriptionFormSerializer(serializers.ModelSerializer):
    consultation_details = serializers.SerializerMethodField()

    class Meta:
        model = PatientPrescriptionForm
        fields = [
            'id',
            'consultation',
            'consultation_details',
            'form',
            'created_at',
        ]

    def get_consultation_details(self, obj):
        serializer = PatientReportSerializer(obj.consultation, context=self.context)
        return serializer.data
    
class DependentsPrescriptionFormSerializer(serializers.ModelSerializer):
    consultation_details = serializers.SerializerMethodField()

    class Meta:
        model = DependentsPrescriptionForm
        fields = [
            'id',
            'consultation',
            'consultation_details',
            'form',
            'created_at',
        ]

    def get_consultation_details(self, obj):
        serializer = PatientDependentReportSerializer(obj.consultation, context=self.context)
        return serializer.data
    
class PatientLabTestSerializer(serializers.ModelSerializer):
    consultation_details = serializers.SerializerMethodField()

    class Meta:
        model = PatientLabTest
        fields = [
            'id',
            'consultation',
            'consultation_details',
            'name',
            'description',
            'result',
            'test_date',
            'file',
            'created_at',
        ]

    def get_consultation_details(self, obj):
        serializer = PatientReportSerializer(obj.consultation, context=self.context)
        return serializer.data
    

class DependentsLabTestSerializer(serializers.ModelSerializer):
    consultation_details = serializers.SerializerMethodField()

    class Meta:
        model = DependentsLabTest
        fields = [
            'id',
            'consultation',
            'consultation_details',
            'name',
            'description',
            'result',
            'test_date',
            'file',
            'created_at',
        ]

    def get_consultation_details(self, obj):
        serializer = PatientDependentReportSerializer(obj.consultation, context=self.context)
        return serializer.data
    
class PatientRecommendationSerializer(serializers.ModelSerializer):
    consultation_details = serializers.SerializerMethodField()

    class Meta:
        model = PatientRecommendation
        fields = [
            'id',
            'consultation',
            'consultation_details',
            'form',
            'created_at',
        ]

    def get_consultation_details(self, obj):
        serializer = PatientReportSerializer(obj.consultation, context=self.context)
        return serializer.data
    

class DependentsRecommendationSerializer(serializers.ModelSerializer):
    consultation_details = serializers.SerializerMethodField()

    class Meta:
        model = DependentsRecommendation
        fields = [
            'id',
            'consultation',
            'consultation_details',
            'form',
            'created_at',
        ]

    def get_consultation_details(self, obj):
        serializer = PatientDependentReportSerializer(obj.consultation, context=self.context)
        return serializer.data