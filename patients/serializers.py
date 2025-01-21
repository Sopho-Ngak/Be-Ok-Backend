# import serializers
from rest_framework import serializers
from patients.models import (
    DependentProfilePicture, Patient, PatientReport, PatientDependentReport, ONLINE, Appointement, CONSULTATION_TYPE,
    PatientPrescriptionForm, DependentsPrescriptionForm, PatientLabTest, AiConsultationPatient,AIConsultationPatientSymptoms,
    AIConsultationPatientPrescription, AiPatientDiagnosis, DependentsLabTest, PatientRecommendationForm, DependentsRecommendation, PatientPayment, DependentsPayment
    ,Dependent)
from accounts.models import User
from accounts.serializers import UserInfoSerializer, UserCreateSerializer
from doctors.models import Doctor, DoctorAvailability
from doctors.serializers import MinimumDoctorInfoSerializer, DoctorAvailabilitySerializer

from utils.payment_module import Payment


class PatientPaymentSerializer(serializers.ModelSerializer):

    class Meta:
        model = PatientPayment
        fields = [
            'id',
            'consultation',
            'amount',
            'transaction_ref',
            'created_at',
        ]


class DependentsPaymentSerializer(serializers.ModelSerializer):
    
        class Meta:
            model = DependentsPayment
            fields = [
                'id',
                'consultation',
                'amount',
                'transaction_ref',
                'created_at',
            ]

class DependentProfilePictureSerializer(serializers.ModelSerializer):
    class Meta:
        model = DependentProfilePicture
        fields = [
            'id',
            'profile_picture',
            'created_at',
        ]

class DependentSerializer(serializers.ModelSerializer):
    profile_picture = serializers.FileField(write_only=True, required=False)
    location_as_mine = serializers.BooleanField(write_only=True, required=False)
    class Meta:
        model = Dependent
        fields = [
            'id',
            # 'patient',
            'full_name',
            'profile_picture',
            'relationship',
            'age',
            'gender',
            'blood_group',
            'alergies',
            'location',
            'location_as_mine',
        ]

    def create(self, validated_data):
        patient = Patient.objects.get(patient_username__username=self.context['request'].user)
        validated_data['patient'] = patient
        location_as_mine = validated_data.pop('location_as_mine', False)
        if location_as_mine:
            validated_data['location'] = patient.location

        profile_picture = validated_data.pop('profile_picture', None)
        dependent = super().create(validated_data)
        
        if profile_picture:
            DependentProfilePicture.objects.create(user=dependent, profile_picture=profile_picture)
        else:
            DependentProfilePicture.objects.create(user=dependent)

        return dependent
            
            

class DependentInfoSerializer(serializers.ModelSerializer):
    profile_picture = DependentProfilePictureSerializer(
        source="dependent_profile_picture", read_only=True)
    class Meta:
        model = Dependent
        fields = [
            'id',
            'profile_picture',
            'full_name',
            'relationship',
            'age',
            'gender',
            'blood_group',
            'alergies',
            # 'chronic_diseases',
            'location',
            'created_at'
        ]

    def update(self, instance, validated_data):
        profile_picture = validated_data.pop('profile_picture', None)
        if profile_picture:
            instance.dependent_profile_picture.profile_picture = profile_picture
            instance.dependent_profile_picture.save()
        return super().update(instance, validated_data)

class PatientRegistrationSerializer(UserCreateSerializer):
    identity_number = serializers.CharField(write_only=True, required=True)
    has_childrens = serializers.BooleanField(write_only=True, required=False)
    has_family_members = serializers.BooleanField(write_only=True, required=False)
    location = serializers.CharField(write_only=True, required=False)

    def validate(self, attrs):
        if attrs.get('gender') == 'male':
            if attrs.get('is_pregnant'):
                raise serializers.ValidationError("Sorry, You can't be pregnant as a man")
        return super().validate(attrs)

    class Meta(UserCreateSerializer.Meta):
        fields = UserCreateSerializer.Meta.fields + [
            'identity_number',
            'has_childrens',
            'has_family_members',
            'location',
        ]

    def create(self, validated_data):
        validated_data['user_type'] = User.PATIENT
        patient_data = {
            'identity_number': validated_data.pop('identity_number'),
            'has_childrens': validated_data.pop('has_childrens', False),
            'has_family_members': validated_data.pop('has_family_members', False),
            'location': validated_data.pop('location', None),
        }
        user = super().create(validated_data)
        try:
            instance = Patient.objects.get(patient_username=user)
        except Patient.DoesNotExist:
            instance = Patient.objects.create(patient_username=user, **patient_data)
        return instance
    

class PatientInfoSerializer(serializers.ModelSerializer):
    personal_information = serializers.SerializerMethodField()
    dependents_profile = DependentInfoSerializer(
        source="dependents", many=True, read_only=True)

    class Meta:
        model = Patient
        fields = [
            'id',
            # 'patient_username',
            "identity_number",
            'blood_group',
            'alergies',
            'chronic_diseases',
            'habits',
            'current_prescription',
            "current_treatment",
            'is_pregnant',
            "has_childrens",
            "has_family_members",
            "location",
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

class AIConsultationPatientSymptomsSerializer(serializers.ModelSerializer):

    class Meta:
        model = AIConsultationPatientSymptoms
        fields = [
            'id',
            'symptoms',
            'created_at'
        ]

class AIConsultationPatientPrescriptionSerializer(serializers.ModelSerializer):
    
        class Meta:
            model = AIConsultationPatientPrescription
            fields = [
                'id',
                'prescription',
                'dosage', # how many pills per dose
                'frequence', # how many times
                'frequence_type', # daily, weekly, monthly, yearly
                'duration', # how many days
                'created_at'
            ]

class AiPatientDiagnosisSerializer(serializers.ModelSerializer):
    class Meta:
        model = AiPatientDiagnosis
        fields = [
            'id',
            'diagnosis',
            'recommended_tests',
            'recommendation',
            'created_at'
        ]

class AiConsultationInfoPatientSerializer(serializers.ModelSerializer):
    symptoms = AIConsultationPatientSymptomsSerializer(
        source="ai_consultation_patient_symptoms", many=True, read_only=True)
    prescription = AIConsultationPatientPrescriptionSerializer(
        source="ai_consultation_patient_prescription", many=True, read_only=True)
    diagnosis = AiPatientDiagnosisSerializer(
        source="ai_patient_diagnosis", read_only=True)
    # user = serializers.UUIDField(read_only=True)

    class Meta:
        model = AiConsultationPatient
        fields = [
            'id',
            'user',
            'pain_area',
            'illness_description',
            'alergies',
            'is_pregnant',
            'pregnancy_days',
            'adiction_habits',
            'pain_duration',
            'family_medical_history',
            'previous_treatment',
            'current_treatment',
            'previous_illness',
            'symptoms',
            'diagnosis',
            'prescription',
            'is_paid',
            'has_consulted_doctor',
            'status',
            'created_at',
        ]
class AiConsultationPatientSerializer(serializers.ModelSerializer):
    symptoms = serializers.ListField(child=serializers.CharField(), write_only=True, required=True)
    prescription = serializers.ListField(child=serializers.DictField(), required=True, write_only=True)
    user = serializers.UUIDField(default=serializers.CurrentUserDefault())
    diagnosis = serializers.CharField(write_only=True, required=True, max_length=None)
    recommended_tests = serializers.CharField(write_only=True, required=True, max_length=None)
    recommendation = serializers.CharField(write_only=True, required=True, max_length=None)

    class Meta:
        model = AiConsultationPatient
        fields = [
            'id',
            'user',
            'pain_area',
            'symptoms',
            'illness_description',
            'alergies',
            'adiction_habits',
            'family_medical_history',
            'pain_duration',
            'is_pregnant',
            'pregnancy_days',
            'current_treatment',
            'previous_treatment',
            'previous_illness',
            'diagnosis',
            'prescription',
            'recommended_tests',
            'recommendation',
            'is_paid',
            'has_consulted_doctor',
            'status',
            'created_at',
        ]

    def create(self, validated_data: dict):

        # replace "None" string with None
        for key, value in validated_data.items():
            if isinstance(value, str) and value.lower() == "none":
                validated_data[key] = None

        if not validated_data.get('symptoms') or not validated_data.get('prescription'):
            raise serializers.ValidationError("Symptoms and prescription are required")
        
        # raise error if symptoms or prescription are not a list of dictionaries
        if not isinstance(validated_data.get('symptoms'), list) \
            or not isinstance(validated_data.get('prescription'), list)\
                or not all(isinstance(item, dict) for item in validated_data.get('prescription')) \
                    or not all(isinstance(item, str) for item in validated_data.get('symptoms')):
            raise serializers.ValidationError("Symptoms and prescription must be a list of dictionaries")
        
        symptoms_date = validated_data.pop('symptoms')
        prescription_data = validated_data.pop('prescription')
        diagnosis = {
            'diagnosis': validated_data.pop('diagnosis'),
            'recommended_tests': validated_data.pop('recommended_tests'),
            'recommendation': validated_data.pop('recommendation'),
        }

        try:
            patient = Patient.objects.get(patient_username__username=self.context['request'].user)
        except Patient.DoesNotExist:
            raise serializers.ValidationError("Patient not found. The current user is not a patient")
        
        validated_data['user'] = patient
        consultation = AiConsultationPatient.objects.create(**validated_data)
    
        # bulk create symptoms
        symptoms = [AIConsultationPatientSymptoms(consultation=consultation, symptoms=item) for item in symptoms_date]
        AIConsultationPatientSymptoms.objects.bulk_create(symptoms)
        prescription = [AIConsultationPatientPrescription(consultation=consultation, **item) for item in prescription_data]
        AIConsultationPatientPrescription.objects.bulk_create(prescription)
        AiPatientDiagnosis.objects.create(consultation=consultation, **diagnosis)

        return consultation


class PatientReportSerializer(serializers.ModelSerializer):
    consulted_by_doctor = serializers.UUIDField(required=False, allow_null=True, read_only=True)
    patient_username = serializers.UUIDField(required=False, allow_null=True, read_only=True)
    personal_information = serializers.SerializerMethodField()

    class Meta:
        model = PatientReport
        fields = [
            'id',
            'user',
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
        ai_consultation = AiConsultationPatient.objects.filter(user=obj, is_paid=True)
        ai_serializer = AiConsultationInfoPatientSerializer(ai_consultation, many=True, context=self.context)
        paid_reports_instance = PatientReport.objects.filter(user=obj, is_paid=True)
        serializer = PatientReportSerializer(paid_reports_instance, many=True, context=self.context)
        data = {
            'ai_consultation': ai_serializer.data,
            'doctor_consultation': serializer.data
        }
        return data
    
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
    payment_details = serializers.SerializerMethodField()

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
            "user_concerned",
            "describe_disease",
            "rejection_reason",
            "payment_details",
        ]

    def get_payment_details(self, obj: Appointement):
        if obj.user_concerned == Appointement.MYSELF:
            payment = PatientPaymentSerializer(obj.payment)
            return payment.data
        
        return DependentsPaymentSerializer(obj.payment).data

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
    payment_details = serializers.SerializerMethodField()

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
            "user_concerned",
            "payment_details",
            "rejection_reason",
            "appointement_happen_in",
            "created_at",
        ]

    def update(self, instance: Appointement, validated_data: dict):
        if validated_data.get('status') != Appointement.CANCELLED:
            raise serializers.ValidationError("Denied: A patient can only cancel an appointment")
        return super().update(instance, validated_data)
    
    def create(self, validated_data: dict):

        try:
            available : DoctorAvailability = validated_data.get('doctor').doctor_availabilities.get(
                id=validated_data.get('doctor_availability').id, is_booked=False)
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
    
    def get_payment_details(self, obj: Appointement):
        if obj.user_concerned == Appointement.MYSELF:
            if obj.payment:
                payment = PatientPaymentSerializer(obj.payment)
                return payment.data
            return 'Pending payment'
        
        return DependentsPaymentSerializer(obj.payment).data
    
    def get_doctor_profile(self, obj: Appointement):
        serializer = MinimumDoctorInfoSerializer(obj.doctor, context=self.context)
        return serializer.data
    
    def get_patient_profile(self, obj: Appointement):
        serializer = MinumumPatientInfoSerializer(obj.patient, context=self.context)
        return serializer.data
    
    def get_doctor_availability_details(self, obj: Appointement):
        serializer = DoctorAvailabilitySerializer(obj.doctor_availability, context=self.context)
        return serializer.data
    
    def get_appointement_happen_in(self, obj: Appointement):
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

    def get_doctor_profile(self, obj: Appointement):
        serializer = MinimumDoctorInfoSerializer(obj.doctor, context=self.context)
        return serializer.data
    
    def getdoctor_availability_details(self, obj: Appointement):
        serializer = DoctorAvailabilitySerializer(obj.doctor_availability, context=self.context)
        return serializer.data
    
    def get_appointement_happen_in(self, obj):
        return obj.happend_in()
    
class DoctorAppointmentInfoSerializer(serializers.ModelSerializer):
    patient = serializers.SerializerMethodField()
    doctor_availability = serializers.SerializerMethodField()
    appointment_happend_in = serializers.SerializerMethodField()
    payment_details = serializers.SerializerMethodField()
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
            'payment_details',
            'pain_area',
            'state',
            'status',
            'created_at', 
            'doctor_availability', 
            'patient', 
            ]
    
    def get_patient(self, obj: Appointement):
        serializer = MinumumPatientInfoSerializer(obj.patient, context=self.context)
        return serializer.data
    
    def get_payment_details(self, obj: Appointement):
        if obj.user_concerned == Appointement.MYSELF:
            if obj.payment:
                payment = PatientPaymentSerializer(obj.payment)
                return payment.data
            return 'Pending payment'
        
        if obj.payment:
            return DependentsPaymentSerializer(obj.payment).data
        return 'Pending payment'

    def get_doctor_availability(self, obj: Appointement):
        serializer = DoctorAvailabilitySerializer(obj.doctor_availability)
        return serializer.data
    
    def get_appointment_happend_in(self, obj: Appointement):
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
        model = PatientRecommendationForm
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