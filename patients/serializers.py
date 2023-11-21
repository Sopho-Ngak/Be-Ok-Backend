from django.utils import timezone
# import serializers
from rest_framework import serializers
from patients.models import Patient, PatientReport, PatientDependentReport, ONLINE, Appointement
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
    consultated_by_doctor = serializers.UUIDField(required=False, allow_null=True, read_only=True)
    patient_username = serializers.UUIDField(required=False, allow_null=True)
    personal_information = serializers.SerializerMethodField()

    class Meta:
        model = PatientReport
        fields = [
            'id',
            'patient_username',
            'personal_information',
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

    def get_personal_information(self, obj):
        user = User.objects.get(username=obj)
        profile_serializer = UserInfoSerializer(user, context=self.context)
        medical_serializer = PatientEditProfileSerializer(obj.patient_username, context=self.context)
        data = {
            "profile": profile_serializer.data,
            "medical": medical_serializer.data
        }

        return data
    # def create(self, validated_data):
    #     patient_id = validated_data.pop('patient_username', None)
    #     doctor = validated_data.pop('consultated_by_doctor', None)
        
    #     if not patient_id:
    #         try:
    #             user_id = self.context['request'].user.id
    #             patient = Patient.objects.get(patient_username__id=str(user_id))
    #         except Patient.DoesNotExist:
    #             raise serializers.ValidationError("Patient not found")
            
    #     elif patient_id and not doctor:
    #         doctor = self.context['request'].user.id
    #         patient = Patient.objects.get(id=str(patient_id))
    #     else:
    #         # AI consultation
    #         try:
    #             patient = Patient.objects.get(id=str(patient_id))
    #         except User.DoesNotExist:
    #             raise serializers.ValidationError("Patient not found")
            

    #     if not doctor:
    #         doctor, created = User.objects.get_or_create(username="Dr Emile", user_type=User.DOCTOR)
    #         consultated_by = Doctor.objects.get(user=doctor)
    #     else:
    #         # consultated_by = validated_data.get('consultated_by_doctor')
    #         try:
    #             consultated_by = Doctor.objects.get(user__id=str(doctor))
    #             if not validated_data.get('consultation_type'):
    #                 validated_data['consultation_type'] = ONLINE
    #         except Doctor.DoesNotExist:
    #             raise serializers.ValidationError("Only doctors can consult patients")

    #     if consultated_by.user == patient.patient_username:
    #         raise serializers.ValidationError("You can't consult yourself.")

    #     instance = PatientReport.objects.create(patient_username=patient, consultated_by_doctor=consultated_by, **validated_data)
    #     return instance


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
            'created_at',
        ]
    
    def get_account_holder(self, obj):
        user = User.objects.get(username=obj)
        serializer = UserInfoSerializer(user, context=self.context)

        return serializer.data

    # def create(self, validated_data):
    #     user_id = self.context['request'].user.id
    #     account_holder = validated_data.pop('patient_username', None)

    #     if not account_holder:
    #         # AI consultation
    #         doctor, created = User.objects.get_or_create(username="Dr Emile", user_type=User.DOCTOR)
    #         consultated_by = Doctor.objects.get(user=doctor)

    #         patient = Patient.objects.get(patient_username__id=user_id)

    #     elif account_holder:
    #         consultated_by = self.context['request'].user.id
    #         try:
    #             consultated_by = Doctor.objects.get(user__id=str(consultated_by))
    #             patient = Patient.objects.get(id=str(account_holder))
    #             if not validated_data.get('consultation_type'):
    #                 validated_data['consultation_type'] = ONLINE
    #         except Patient.DoesNotExist:
    #             raise serializers.ValidationError("Patient not found")
    #         except Doctor.DoesNotExist:
    #             raise serializers.ValidationError("Only doctors can consult patients")
    #     else:
    #         raise serializers.ValidationError("A dependee should have dependents who is the account holder")            
        
    #     # if not validated_data.get('consultated_by_doctor'):
    #     #     doctor, created = User.objects.get_or_create(username="Dr Emile", user_type=User.DOCTOR)
    #     #     consultated_by = Doctor.objects.get(user=doctor)
    #     # else:
    #     #     consultated_by = validated_data.get('consultated_by_doctor')

    #     # patient = Patient.objects.get(patient_username=user)
    #     instance = PatientDependentReport.objects.create(
    #         patient_username=patient, consulted_by_doctor=consultated_by, dependent_relationship=self.context['request'].GET.get("choice"), **validated_data)
    #     return instance


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
        serializer = PatientInfoSerializer(obj.patient_username, context=self.context)
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

class AppointmentSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Appointement
        fields = [
            "id",
            "patient",
            "doctor",
            "service",
            "consultation_type",
            "consultation_note",
            "doctor_availability",
            "is_confirmed",
            "created_at",
        ]

    
    def create(self, validated_data):
        patient = validated_data.get('patient')
        doctor = validated_data.get('doctor')

        try:
            doctor = Doctor.objects.get(user=doctor)
            available = doctor.doctor_availabilities.get(id=validated_data.get('doctor_availability'))
        except Doctor.DoesNotExist:
            raise serializers.ValidationError("Doctor not found")
        except DoctorAvailability.DoesNotExist:
            raise serializers.ValidationError("Doctor availability not found")
        
        available.is_booked = True
        available.save()

        appointment = Appointement.objects.create(**validated_data)
        
        return appointment
    
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
            'consultation_note',
            "appointment_happend_in",
            'is_confirmed',
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

