from django.utils import timezone
from django.db.models import Q, Count

# import serializers
from rest_framework import serializers
from patients.models import (
    DependentProfilePicture, Patient, PatientReport, PatientDependentReport, ONLINE, Appointement, CONSULTATION_TYPE,
    PatientPrescriptionForm, DependentsPrescriptionForm, PatientLabTest, AiConsultationPatient,AIConsultationPatientSymptoms,
    AIConsultationPatientPrescription, AiPatientDiagnosis, DependentsLabTest, PatientRecommendationForm, DependentsRecommendation, PatientPayment, DependentsPayment
    ,Dependent, WorkoutRoutine, Treatment, TreatmentTracker, TreatmentFeedBack, TreatmentCalendar, FamilyDisease, PatientAccountHistory)
from accounts.models import User
from accounts.serializers import UserInfoSerializer, UserCreateSerializer
from doctors.models import Doctor, DoctorAvailability
from doctors.serializers import MinimumDoctorInfoSerializer, DoctorAvailabilitySerializer

from utils.payment_module import Payment
from utils import common


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

class FamilyDiseaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = FamilyDisease
        fields = [
            'id',
            'disease',
            'created_at',
        ]

    def create(self, validated_data):
        patient = Patient.objects.get(patient_username__username=self.context['request'].user)
        instance = FamilyDisease.objects.create(patient=patient, disease=validated_data['disease'])
        return instance
    


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
            'patient_username',
            'personal_information',
            'pain_area',
            'symptoms',
            'consulted_by_doctor',
            'consultation_type',
            'results',
            # 'prescription',
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
        medical_serializer = PatientEditProfileSerializer(obj.user, context=self.context)
        data = {
            "profile": profile_serializer.data,
            "medical": medical_serializer.data
        }

        return data
    
class PatientRecommendationSerializer(serializers.ModelSerializer):
    # consultation_details = serializers.SerializerMethodField()
    doctor_details = serializers.SerializerMethodField()

    def validate(self, attrs):
        # accept only pdf files
        pdf_file = self.context['request'].FILES.get('form')
        if pdf_file and pdf_file.content_type != 'application/pdf':
            raise serializers.ValidationError("Only PDF files are accepted")
        return super().validate(attrs)

    class Meta:
        model = PatientRecommendationForm
        fields = [
            'id',
            'consultation',
            # 'consultation_details',
            'form',
            'created_at',
            "doctor_details"
        ]

    def get_doctor_details(self, obj: PatientRecommendationForm):
        serializer = MinimumDoctorInfoSerializer(obj.consultation.consulted_by_doctor, context=self.context)
        return serializer.data

    # def get_consultation_details(self, obj):
    #     serializer = PatientReportSerializer(obj.consultation, context=self.context)
    #     return serializer.data
    

class WorkoutRoutineSerializer(serializers.ModelSerializer):
    routine_overview = serializers.SerializerMethodField()
    reminder_dates = serializers.JSONField(required=False)

    def validate(self, attrs: dict):
        if attrs['end_date'] < attrs.get('start_date'):
            raise serializers.ValidationError("End date can't be less than start date")
        # validate if reminder_dates is a list of dates in format "YYYY-MM-DD"
        if attrs.get('reminder_dates'):
            if not isinstance(attrs.get('reminder_dates'), list):
                raise serializers.ValidationError("Reminder dates must be a list of dates")
            
            if not all(isinstance(item, str) for item in attrs['reminder_dates']):
                raise serializers.ValidationError("Reminder dates must be a list of dates")
            
            if not all(common.is_valid_date(item) for item in attrs['reminder_dates']):
                raise serializers.ValidationError("Reminder dates must be a list of valid dates in format YYYY-MM-DD")
        return super().validate(attrs)

    class Meta:
        model = WorkoutRoutine
        fields = [
            'id',
            'icon',
            'routine',
            'start_date',
            'end_date',
            'reminder_dates',
            'has_reminder',
            'created_at',
            'routine_overview',
        ]

    def get_routine_overview(self, obj: WorkoutRoutine):
        if obj.total_days >=7 :
            total_days = f"{obj.total_days //7} weeks"
        else:
            total_days = f"{obj.total_days} days"

        return {
            "ongoing": obj.on_going,
            "days_used": obj.days_used_till_today,
            "total_days_number": obj.total_days,
            "total_days": total_days,
            "days_remaining_to_start": obj.days_remaining_to_start if obj.days_remaining_to_start > 0 else 0,
            "days_remaining_to_end": obj.total_days - obj.days_used_till_today if obj.total_days - obj.days_used_till_today > 0 else 0,
            # "status": "completed" if obj.start_date < timezone.now().date() else "ongoing"
        }
    
    def create(self, validated_data: dict):
        instance: WorkoutRoutine = super().create(validated_data)
        if validated_data.get("reminder_dates"):
            instance.has_reminder = True
            instance.save()
        return instance

class TreatmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Treatment
        fields = [
            'id',
            'medication',
            'is_active',
            'write_datetime',
            'created_at',
        ]

class TreatmentTrackerSerializer(serializers.ModelSerializer):
    medications = serializers.SerializerMethodField()
    # taking an array of medications
    medication = serializers.ListField(
        child=serializers.CharField(), write_only=True, required=False)
    patient = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = TreatmentTracker
        fields = [
            'id',
            'patient',
            'medications',
            'medication',
            'created_at',
        ]

    def get_medications(self, obj: TreatmentTracker):
        serializer = TreatmentSerializer(obj.medications.filter(is_active=True), many=True)
        return serializer.data

    def create(self, validated_data: dict):
        try:
            patient = Patient.objects.get(patient_username__username=self.context['request'].user)
        except Patient.DoesNotExist:
            raise serializers.ValidationError("Current user is not not a patient")

        instance, _ = TreatmentTracker.objects.get_or_create(patient=patient)

        medications = [Treatment(medication=item) for item in validated_data['medication']]
        Treatment.objects.bulk_create(medications)
        new_medications_instance = [
            Treatment.objects.get(medication=item, created_at__gte=(timezone.now() - timezone.timedelta(seconds=10))) for item in validated_data['medication']
        ]

        instance.medications.add(*new_medications_instance)

        return instance
    

class TreatmentCalendarSerializer(serializers.ModelSerializer):
    patient = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = TreatmentCalendar
        fields = [
            'id',
            'patient',
            'date',
            'has_taken',
            'created_at',
        ]
    
    def create(self, validated_data: dict):
        try:
            patient = Patient.objects.get(patient_username__username=self.context['request'].user)
        except Patient.DoesNotExist:
            raise serializers.ValidationError("Current user is not not a patient")
        
        # get all active medications of patient

        medication = TreatmentTracker.objects.get(
            patient=patient).medications.filter(is_active=True)
        
        calendar_instance, created = TreatmentCalendar.objects.get_or_create(
            patient=patient, date=validated_data['date'])
        
        # if created and date is current date then has taken is True
        if created and validated_data['date'] <= timezone.now().date():
            calendar_instance.has_taken = True
            calendar_instance.save()

        elif validated_data['date'] <= timezone.now().date():
            calendar_instance.has_taken = not calendar_instance.has_taken
            calendar_instance.save()
        
        calendar_instance.treatment.set(medication)

        return calendar_instance

class TreatmentFeedBackSerializer(serializers.ModelSerializer):
    patient = serializers.HiddenField(default=serializers.CurrentUserDefault())
    medications = serializers.SerializerMethodField()

    class Meta:
        model = TreatmentFeedBack
        fields = [
            'id',
            'patient',
            'feedback',
            'medications',
            'created_at',
        ]

    def get_medications(self, obj: TreatmentFeedBack):
        serializer = TreatmentSerializer(obj.medications.all(), many=True)
        return serializer.data
    
    def create(self, validated_data):
        try:
            patient = Patient.objects.get(patient_username__username=self.context['request'].user)
        except Patient.DoesNotExist:
            raise serializers.ValidationError("Current user is not not a patient")
        
        # get all active medications of patient

        medication = TreatmentTracker.objects.get(
            patient=patient).medications.filter(is_active=True)
        
        feadback_instance = TreatmentFeedBack.objects.create(
            patient=patient, feedback=validated_data.get('feedback'))
        
        feadback_instance.medications.set(medication)

        return feadback_instance

class ConsultationCountSerializer(PatientReportSerializer):
    consultation_count = serializers.IntegerField()
    doctor_details = serializers.SerializerMethodField()

    class Meta(PatientReportSerializer.Meta):
        fields = [
            'consultation_count',
            'doctor_details',
            
        ]

    def get_doctor_details(self, obj):
        doctor = Doctor.objects.get(id=obj['consulted_by_doctor'])
        serializer = MinimumDoctorInfoSerializer(doctor, context=self.context)
        return serializer.data
    

class PatientLabTestSerializer(serializers.ModelSerializer):
    # consultation_details = serializers.SerializerMethodField()
    doctor_details = serializers.SerializerMethodField()

    def validate(self, attrs):
        # accept only pdf files
        pdf_file = self.context['request'].FILES.get('file')
        if pdf_file and pdf_file.content_type != 'application/pdf':
            raise serializers.ValidationError("Only PDF files are accepted")
        return super().validate(attrs)

    class Meta:
        model = PatientLabTest
        fields = [
            'id',
            'consultation',
            # 'consultation_details',
            'name',
            'description',
            'result',
            'test_date',
            'file',
            'created_at',
            'doctor_details',
        ]

    # def get_consultation_details(self, obj):
    #     serializer = PatientReportSerializer(obj.consultation, context=self.context)
    #     return serializer.data

    def get_doctor_details(self, obj: PatientLabTest):
        serializer = MinimumDoctorInfoSerializer(obj.consultation.consulted_by_doctor, context=self.context)
        return serializer.data

class LabTestCountSerializer(PatientLabTestSerializer):
    labtest_count = serializers.IntegerField()
    doctor_details = serializers.SerializerMethodField()

    class Meta(PatientLabTestSerializer.Meta):
        fields = [
            'labtest_count',
            'doctor_details',
            
        ]

    def get_doctor_details(self, obj):
        doctor = Doctor.objects.get(id=obj['consultation__consulted_by_doctor'])
        serializer = MinimumDoctorInfoSerializer(doctor, context=self.context)
        return serializer.data


class RecommandationCountSerializer(PatientRecommendationSerializer):
    recommandation_count = serializers.IntegerField()
    doctor_details = serializers.SerializerMethodField()

    class Meta(PatientRecommendationSerializer.Meta):
        fields = [
            'recommandation_count',
            'doctor_details',
            
        ]

    def get_doctor_details(self, obj):
        doctor = Doctor.objects.get(id=obj['consultation__consulted_by_doctor'])
        serializer = MinimumDoctorInfoSerializer(doctor, context=self.context)
        return serializer.data

class RecommandationViewsSectionSerializer(serializers.ModelSerializer):
    recommandation_count_by_doctors = serializers.SerializerMethodField()
    recommandation_overview = serializers.SerializerMethodField()
    recommandation_forms = serializers.SerializerMethodField()


    class Meta:
        model = Patient
        fields = [
            'id',
            'recommandation_overview',
            'recommandation_count_by_doctors',
            'recommandation_forms'
        ]

    def get_recommandation_count_by_doctors(self, obj: Patient):
        # user = self.context['request'].user
        patient_reports = PatientRecommendationForm.objects.filter(consultation__user=obj, form__isnull=False, form__gt='')\
            .values('consultation__consulted_by_doctor')\
                .annotate(recommandation_count=Count('id'))
        
        serializer = RecommandationCountSerializer(patient_reports, many=True, context=self.context)
        return serializer.data
    
    def get_recommandation_forms(self, obj: Patient):
        recommandation = PatientRecommendationForm.objects.filter(
            consultation__user=obj, form__isnull=False, form__gt='')
        serializer = PatientRecommendationSerializer(recommandation, many=True, context=self.context)

        return serializer.data
    
    def get_recommandation_overview(self, obj: Patient):
        

        # Daily reports (created today)
        daily_reports = PatientRecommendationForm.objects.filter(
            consultation__user=obj, created_at__gte=common.start_of_day, form__isnull=False, form__gt='').count()

        # Weekly reports (created this week)
        weekly_reports = PatientRecommendationForm.objects.filter(
            consultation__user=obj, created_at__gte=common.start_of_week, form__isnull=False, form__gt='').count()

        # Monthly reports (created this month)
        monthly_reports = PatientRecommendationForm.objects.filter(
            consultation__user=obj, created_at__gte=common.start_of_month, form__isnull=False, form__gt='').count()

        # Yearly reports (created this year)
        yearly_reports = PatientRecommendationForm.objects.filter(
            consultation__user=obj, created_at__gte=common.start_of_year, form__isnull=False, form__gt='').count()

        return {
            'daily': daily_reports,
            'weekly': weekly_reports,
            'monthly': monthly_reports,
            'yearly': yearly_reports,
        }
    
    


class LabTestsViewsSectionSerializer(serializers.ModelSerializer):
    labtest_count_by_doctors = serializers.SerializerMethodField()
    labtest_overview = serializers.SerializerMethodField()
    medical_results_form = serializers.SerializerMethodField()
    

    class Meta:
        model = Patient
        fields = [
            'id',
            'labtest_overview',
            'labtest_count_by_doctors',
            'medical_results_form'
        ]

    def get_labtest_count_by_doctors(self, obj: Patient):
        # user = self.context['request'].user
        patient_reports = PatientLabTest.objects.filter(consultation__user=obj, file__isnull=False, file__gt='')\
            .values('consultation__consulted_by_doctor')\
                .annotate(labtest_count=Count('id'))
        
        serializer = LabTestCountSerializer(patient_reports,many=True, context=self.context)
        return serializer.data
    
    def get_medical_results_form(self, obj: Patient):
        labtest = PatientLabTest.objects.filter(
            consultation__user=obj, file__isnull=False, file__gt='')
        serializer = PatientLabTestSerializer(labtest, many=True, context=self.context)

        return serializer.data
    
    def get_labtest_overview(self, obj: Patient):
        

        # Daily reports (created today)
        daily_reports = PatientLabTest.objects.filter(
            consultation__user=obj, created_at__gte=common.start_of_day, file__isnull=False, file__gt='').count()

        # Weekly reports (created this week)
        weekly_reports = PatientLabTest.objects.filter(
            consultation__user=obj, created_at__gte=common.start_of_week, file__isnull=False, file__gt='').count()

        # Monthly reports (created this month)
        monthly_reports = PatientLabTest.objects.filter(
            consultation__user=obj, created_at__gte=common.start_of_month, file__isnull=False, file__gt='').count()

        # Yearly reports (created this year)
        yearly_reports = PatientLabTest.objects.filter(
            consultation__user=obj, created_at__gte=common.start_of_year, file__isnull=False, file__gt='').count()

        return {
            'daily': daily_reports,
            'weekly': weekly_reports,
            'monthly': monthly_reports,
            'yearly': yearly_reports,
        }

class PrescriptionViewsSectionSerializer(serializers.ModelSerializer):
    counsultation_count_by_doctors = serializers.SerializerMethodField()
    consultation_overview = serializers.SerializerMethodField()
    medical_results_form = serializers.SerializerMethodField()
    

    class Meta:
        model = Patient
        fields = [
            'id',
            'consultation_overview',
            'counsultation_count_by_doctors',
            'medical_results_form',

        ]

    def get_counsultation_count_by_doctors(self, obj: Patient):
        # user = self.context['request'].user
        patient_reports = PatientReport.objects.filter(user=obj)\
            .values('consulted_by_doctor')\
                .annotate(consultation_count=Count('id'))
        
        # TODO: add AI reports in the future to count the consultation by AI
        # ai_reports = AiConsultationPatient.objects.filter(user=obj)\
        #     .values('consulted_by_doctor')\
        #         .annotate(consultation_count=Count('consulted_by_doctor'))
        # consultation_count = list(patient_reports) + list(ai_reports)
        serializer = ConsultationCountSerializer(patient_reports, many=True, context=self.context)
        return serializer.data
    
    def get_medical_results_form(self, obj: Patient):
        # user = self.context['request'].user
        medical_forms = PatientPrescriptionForm.objects.filter(
            consultation__user=obj)
        
        serializer = PatientPrescriptionFormSerializer(medical_forms, many=True, context=self.context)
        return serializer.data
    
    def get_consultation_overview(self, obj: Patient):
        

        # Daily reports (created today)
        daily_reports = PatientReport.objects.filter(user=obj, created_at__gte=common.start_of_day).count()

        # Weekly reports (created this week)
        weekly_reports = PatientReport.objects.filter(user=obj, created_at__gte=common.start_of_week).count()

        # Monthly reports (created this month)
        monthly_reports = PatientReport.objects.filter(user=obj, created_at__gte=common.start_of_month).count()

        # Yearly reports (created this year)
        yearly_reports = PatientReport.objects.filter(user=obj, created_at__gte=common.start_of_year).count()

        return {
            'daily': daily_reports,
            'weekly': weekly_reports,
            'monthly': monthly_reports,
            'yearly': yearly_reports,
        }

class GeneralHealgthViewSerialize(serializers.ModelSerializer):
    workout_routines = WorkoutRoutineSerializer(
        source="workout_routine", many=True, read_only=True)
    treatments = TreatmentTrackerSerializer(
        source="treatment_tracker", read_only=True)
    my_doctors = serializers.SerializerMethodField()
    treatments_calendar = TreatmentCalendarSerializer(
        source="patient_treatment_calendar", many=True, read_only=True)
    weight_details = serializers.SerializerMethodField()
    family_diseases = serializers.SerializerMethodField()
    
    class Meta:
        model = Patient
        fields = [
            'id',
            'chronic_diseases',
            'habits',
            'weight_details',
            'family_diseases',
            'current_prescription',
            'blood_group',
            # 'has_childrens',
            # 'has_family_members',
            # 'location',
            'created_at',
            'treatments',
            'treatments_calendar',
            'workout_routines',
            'my_doctors',
        ]

    def get_my_doctors(self, obj: Patient):
        user = self.context['request'].user

        doctors = Doctor.objects.filter(
            doctor_documents__is_approved=True
        ).filter(
            Q(patient_consultated_by__user__patient_username=user) |
            Q(dependent_consultated_by__patient_username__patient_username=user)
        ).distinct()
        serializer = MinimumDoctorInfoSerializer(doctors, many=True, context=self.context)
        return serializer.data

    def get_weight_details(self, obj: Patient):
        most_recent_weight_history = PatientAccountHistory.objects.filter(
            patient=obj, field='weight').order_by('-created_at').first()
        if most_recent_weight_history:
            most_recent_weight_history = float(most_recent_weight_history.value)
        else:
            most_recent_weight_history = 0.0
        return {
            "weight": obj.weight,
            "variation": obj.weight - most_recent_weight_history if obj.weight and most_recent_weight_history > 0.0 else 0
        }
    
    def get_family_diseases(self, obj: Patient):
        family_diseases = FamilyDisease.objects.filter(patient=obj, is_active=True)
        serializer = FamilyDiseaseSerializer(family_diseases, many=True, context=self.context)
        return serializer.data




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
            'weight',
            'alergies',
            'chronic_diseases',
            'habits',
            'current_prescription',
            'is_pregnant',
        ]

    def update(self, instance: Patient, validated_data: dict):
        # List of fields to track in PatientAccountHistory
        TRACKED_FIELDS = [
            'weight',
            'blood_group',
            'alergies',
            'chronic_diseases',
            'habits',
            'current_prescription',
            'is_pregnant',
        ]

        # Create a list to store history records for batch creation
        history_records = []

        # Check which tracked fields are being updated
        for field in TRACKED_FIELDS:
            if field in validated_data and getattr(instance, field) != validated_data[field]:
                # Create a history record for the field
                history_records.append(
                    PatientAccountHistory(
                        patient=instance,
                        field=field,
                        value=getattr(instance, field)  # Old value
                    )
                )

        # Bulk create history records (if any)
        if history_records:
            PatientAccountHistory.objects.bulk_create(history_records)

        # Update the instance with the validated data
        return super().update(instance, validated_data)
    
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
    # consultation_details = serializers.SerializerMethodField()
    doctor_details = serializers.SerializerMethodField()

    def validate(self, attrs):
        # accept only pdf files
        pdf_file = self.context['request'].FILES.get('form')
        if pdf_file and pdf_file.content_type != 'application/pdf':
            raise serializers.ValidationError("Only PDF files are accepted")
        return super().validate(attrs)

    class Meta:
        model = PatientPrescriptionForm
        fields = [
            'id',
            'consultation',
            'form',
            'created_at',
            'doctor_details',
            # 'consultation_details',
        ]

    # def get_consultation_details(self, obj):
    #     serializer = PatientReportSerializer(obj.consultation, context=self.context)
    #     return serializer.data

    def get_doctor_details(self, obj: PatientPrescriptionForm):
        serializer = MinimumDoctorInfoSerializer(obj.consultation.consulted_by_doctor, context=self.context)
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