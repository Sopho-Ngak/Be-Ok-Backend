from pydoc import doc
from django.utils import timezone
# import serializers
from rest_framework import serializers
from accounts.models import User
import patients
# from patients.models import Patient, PatientReport, PatientDependentReport, ONLINE, Appointement
# from accounts.models import User
from accounts.serializers import UserInfoSerializer, UserCreateSerializer
from doctors.models import Doctor, DoctorDocument, DoctorAvailability
import patients.serializers as patient_serializers
# from doctors.models import DiseaseGroup, Disease



class DoctorRegistrationSerializer(UserCreateSerializer):
    identity_number = serializers.CharField(write_only=True, required=False)
    license_number = serializers.CharField(write_only=True, required=True)
    specialities = serializers.CharField(write_only=True, required=True)
    profession = serializers.CharField(write_only=True, required=True)
    physical_consultation = serializers.BooleanField(write_only=True, required=False)
    online_consultation = serializers.BooleanField(write_only=True, required=False)
    document = serializers.FileField(write_only=True, required=True)
    
    # append the fields to the fields list in parent clasee
    class Meta(UserCreateSerializer.Meta):
        fields = UserCreateSerializer.Meta.fields + [
            'identity_number',
            'license_number',
            'specialities',
            'profession',
            'physical_consultation',
            'online_consultation',
            'document',
        ]

    def create(self, validated_data: dict):
        validated_data['user_type'] = User.DOCTOR
        doctor_data = {
            'physical_consultation': validated_data.pop('physical_consultation', False),
            'online_consultation': validated_data.pop('online_consultation', False),
            'specialties': validated_data.pop('specialities'),
            'profession': validated_data.pop('profession'),
        }

        document_date = {
            'licence_number': validated_data.pop('license_number'),
            'document': validated_data.pop('document'),
        }

        user = super().create(validated_data)
        try:
            doctor = Doctor.objects.get(user=user)
        except Doctor.DoesNotExist:
            doctor = Doctor.objects.create(user=user, **doctor_data)
            DoctorDocument.objects.create(doctor=doctor, **document_date)

        return doctor


class DoctorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Doctor
        fields = [
            'id', 
            'city', 
            'state', 
            'specialties', 
            'physical_consultation', 
            'online_consultation', 
            'description', 
            'created_at', 
            ]
class DoctorDocumentSerializer(serializers.ModelSerializer):
    is_approved = serializers.BooleanField(read_only=True)
    approved_by = serializers.CharField(read_only=True)
    approved_at = serializers.DateTimeField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    class Meta:
        model = DoctorDocument
        fields = [
            'id', 
            'licence_number', 
            'document', 
            'is_approved', 
            'approved_by', 
            'approved_at', 
            'created_at', 
            ]

class BookedAppointmentSerializer(serializers.ModelSerializer):
    pass
class DoctorAvailabilitySerializer(serializers.ModelSerializer):
    start_day = serializers.SerializerMethodField(read_only=True)
    start_time = serializers.SerializerMethodField(read_only=True)
    end_day = serializers.SerializerMethodField(read_only=True)
    end_time = serializers.SerializerMethodField(read_only=True)

    def validate(self, data):
        try:
            if data['starting_date'] < timezone.now():
                raise serializers.ValidationError("Starting date should be greater than or egal to current date")
            elif data['starting_date'] >= data['ending_date']:
                raise serializers.ValidationError("Ending date should be greater than starting date")
        except KeyError:
            pass
        return data

    class Meta:
        model = DoctorAvailability
        fields = [
            'id', 
            'starting_date', 
            'ending_date',
            'start_day',
            'start_time',
            'end_day',
            'end_time', 
            'is_booked', 
            'created_at', 
            ]

    def get_start_day(self, obj):
        return obj.starting_date.strftime("%A")
    
    def get_start_time(self, obj):
        return obj.starting_date.strftime("%I:%M:%S %p")
    
    def get_end_day(self, obj):
        return obj.ending_date.strftime("%A")
    
    def get_end_time(self, obj):
        return obj.ending_date.strftime("%I:%M:%S %p")
    
    
class DoctorInfoSerializer(serializers.ModelSerializer):
    personal_information = serializers.SerializerMethodField()
    documents = DoctorDocumentSerializer(source="doctor_documents", read_only=True)
    availabilities = serializers.SerializerMethodField()
    patients_consulted = serializers.SerializerMethodField()
    dependents_consulted = serializers.SerializerMethodField()
    # appointments = serializers.SerializerMethodField()

    class Meta:
        model = Doctor
        fields = [
            'id', 
            'city', 
            'state', 
            'specialties', 
            'physical_consultation', 
            'online_consultation', 
            'description', 
            'created_at', 
            'personal_information', 
            'documents', 
            'availabilities',
            'patients_consulted',
            'dependents_consulted',
            # 'appointments', 
            ]
    def get_personal_information(self, obj):
        serializer = UserInfoSerializer(obj.user, context=self.context)

        return serializer.data
    
    def get_availabilities(self, obj):
        availabilities = DoctorAvailability.objects.filter(doctor=obj, is_booked=False, ending_date__gte=timezone.now())
        serializer = DoctorAvailabilitySerializer(availabilities, many=True)
        return serializer.data
    
    def get_patients_consulted(self, obj):
        serializers = patient_serializers.PatientReportSerializer(obj.patients_consulted, many=True, context=self.context)
        return serializers.data
    
    def get_dependents_consulted(self, obj):
        serializers = patient_serializers.PatientDependentReportSerializer(obj.dependents_consulted, many=True, context=self.context)
        return serializers.data
    
    # def get_appointments(self, obj):
    #     appointments = Appointement.objects.filter(doctor=obj, doctor_availability__ending_date__gte=timezone.now())
    #     serializer = DoctorAppointmentInfoSerializer(appointments, many=True)
    #     return serializer.data

class MinimumDoctorInfoSerializer(DoctorInfoSerializer):

    class Meta:
        model = Doctor
        fields = [
            'id', 
            'city', 
            'state', 
            'specialties', 
            'physical_consultation', 
            'online_consultation', 
            'description',  
            'personal_information',
        ]

# class DiseaseSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Disease
#         fields = [
#             'id', 
#             'name', 
#             'icon', 
#             'created_at'
#             ]


# class DiseaseGroupSerializer(serializers.ModelSerializer):
#     diseases = DiseaseSerializer(
#         source="disease_description", many=True, read_only=True)

#     class Meta:
#         model = DiseaseGroup
#         fields = [
#             'id', 
#             'name',
#             'diseases', 
#             'created_at', 
#             ]