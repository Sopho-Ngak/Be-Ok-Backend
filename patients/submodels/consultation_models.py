# Python Imports
import uuid

# Django Imports
from django.db import models
from .utils import (PAIN_AREA_CHOICES, CONSULTATION_STATUS, CONSULTATION_TYPE, AI_CONSULTATION,
                    medical_form_upload_path, prescribtion_form_upload_path, lab_test_upload_path)
# from patients.models import Patient, Dependent
from accounts.models import User
from .patient_models import Patient
from doctors.models import Doctor



class AiConsultationPatient(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='ai_consultations')
    pain_area = models.CharField(max_length=255)
    illness_description = models.TextField()
    alergies = models.TextField(blank=True, null=True)
    is_pregnant = models.BooleanField(default=False)
    pregnancy_days = models.IntegerField(blank=True, null=True)
    adiction_habits = models.TextField(blank=True, null=True)
    pain_duration = models.CharField(max_length=255, blank=True, null=True)
    family_medical_history = models.TextField(blank=True, null=True)
    previous_treatment = models.TextField(blank=True, null=True)
    current_treatment = models.TextField(blank=True, null=True)
    previous_illness = models.TextField(blank=True, null=True)
    is_paid = models.BooleanField(default=False)
    has_consulted_doctor = models.BooleanField(default=False)
    status = models.CharField(choices=CONSULTATION_STATUS, default=CONSULTATION_STATUS[1][0], max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.user)
    
    class Meta:
        ordering = ['-created_at']

class AiPatientDiagnosis(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    consultation = models.OneToOneField(AiConsultationPatient, on_delete=models.CASCADE, related_name='ai_patient_diagnosis')
    diagnosis = models.TextField()
    recommended_tests = models.TextField(blank=True, null=True)
    recommendation = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.consultation)
    
    class Meta:
        ordering = ['-created_at']

class AIConsultationPatientSymptoms(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    consultation = models.ForeignKey(AiConsultationPatient, on_delete=models.CASCADE, related_name='ai_consultation_patient_symptoms')
    symptoms = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.consultation)
    
    class Meta:
        ordering = ['-created_at']

class AIConsultationPatientPrescription(models.Model):
    TYPE_CHOICE = (
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly'),
    )
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    consultation = models.ForeignKey(AiConsultationPatient, on_delete=models.CASCADE, related_name='ai_consultation_patient_prescription')
    prescription = models.CharField(max_length=255)
    dosage = models.IntegerField()
    duration = models.IntegerField()
    frequence = models.IntegerField()
    frequence_type = models.CharField(max_length=8, choices=TYPE_CHOICE, default=TYPE_CHOICE[0][0])
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.consultation)
    
    class Meta:
        ordering = ['-created_at']


# class AiConsultationDependent(models.Model):
#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     user = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='ai_consultations_dependent')
#     dependent = models.ForeignKey(Dependent, on_delete=models.CASCADE, related_name='ai_consultations_dependent_user')
#     pain_area = models.CharField(choices=PAIN_AREA_CHOICES, default=PAIN_AREA_CHOICES[11][1], max_length=255, blank=True, null=True)
#     symptoms = models.TextField()
#     illness_description = models.TextField()
#     results = models.TextField()
#     prescription = models.TextField(blank=True, null=True)
#     recommended_tests = models.TextField(blank=True, null=True)
#     recommendation = models.TextField(blank=True, null=True)
#     # medical_form = models.FileField(upload_to=medical_form_upload_path, blank=True, null=True)
#     is_paid = models.BooleanField(default=False)
#     status = models.CharField(choices=CONSULTATION_STATUS, default=CONSULTATION_STATUS[0][0], max_length=255)
#     created_at = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return str(self.user)
    
#     class Meta:
#         ordering = ['-created_at']

# class DependentAIConsultationSymptoms(models.Model):
#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     consultation = models.ForeignKey(AiConsultationDependent, on_delete=models.CASCADE, related_name='ai_consultation_symptoms_dependent')
#     symptoms = models.CharField(max_length=255)
#     created_at = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return str(self.consultation)
    
#     class Meta:
#         ordering = ['-created_at']

class PatientReport(models.Model):
    PAIN_AREA_CHOICES = (
        ('Abdomen', 'Abdomen'),
        ('Back', 'Back'),
        ('Chest', 'Chest'),
        ('Head', 'Head'),
        ('Joint', 'Joint'),
        ('Muscle', 'Muscle'),
        ('Neck', 'Neck'),
        ('Pelvis', 'Pelvis'),
        ('Shoulder', 'Shoulder'),
        ('Throat', 'Throat'),
        ('Respiratory', 'Respiratory'),
        ('Unknown', 'Other'),
    )

    SERVICE_CHOICES = (
        ('Cardiology', 'Cardiology'),
        ('Dermatology', 'Dermatology'),
        ('Endocrinology', 'Endocrinology'),
        ('Gastroenterology', 'Gastroenterology'),
        ('Hematology', 'Hematology'),
        ('Infectious Disease', 'Infectious Disease'),
        ('Nephrology', 'Nephrology'),
        ('Neurology', 'Neurology'),
        ('Oncology', 'Oncology'),
        ('Pulmonology', 'Pulmonology'),
        ('Rheumatology', 'Rheumatology'),
        ('Urology', 'Urology'),
        ('General Health', 'General Health'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='patient_reports')
    symptoms = models.TextField()
    illness_description = models.TextField()
    consulted_by_doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='patient_consultated_by')
    consultation_type = models.CharField(choices=CONSULTATION_TYPE, default=CONSULTATION_TYPE[0][0], max_length=255, blank=True, null=True)
    pain_area = models.CharField(max_length=255)
    results = models.TextField()
    # prescription = models.TextField(blank=True, null=True)
    recommended_tests = models.TextField(blank=True, null=True)
    recommendation = models.TextField(blank=True, null=True)
    # medical_form = models.FileField(upload_to=medical_form_upload_path, blank=True, null=True)
    is_paid = models.BooleanField(default=False)
    status = models.CharField(choices=CONSULTATION_STATUS, default=CONSULTATION_STATUS[0][0], max_length=255)
    service = models.CharField(choices=SERVICE_CHOICES, default=SERVICE_CHOICES[12][1], max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.user)
    
    class Meta:
        ordering = ['-created_at']

class PatientDependentReport(models.Model):
    FRIEND = 'friend'
    FAMILY = 'family'
    CHILD = 'child'
    SPOUSE = 'spouse'
    OTHER = 'other'
    RELATIONSHIP_CHOICES = (
        (FRIEND, 'Friend'),
        (FAMILY, 'Family'),
        (CHILD, 'Child'),
        (SPOUSE, 'Spouse'),
        (OTHER, 'Other'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient_username = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='patient_dependents')
    dependent_names = models.CharField(max_length=255)
    dependent_relationship = models.CharField(choices=RELATIONSHIP_CHOICES ,max_length=255)
    # dependent_age = models.IntegerField()
    dependent_bithdate = models.DateField(blank=True, null=True)
    dependent_blood_group = models.CharField(max_length=255, blank=True, null=True)
    dependent_alergies = models.TextField( blank=True, null=True)
    dependent_symptoms = models.TextField()
    consulted_by_doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='dependent_consultated_by')
    consultation_type = models.CharField(choices=CONSULTATION_TYPE, default=AI_CONSULTATION, max_length=255, blank=True, null=True)
    dependent_results = models.TextField()
    dependent_prescription = models.TextField(blank=True, null=True)
    dependent_recommended_tests = models.TextField(blank=True, null=True)
    dependent_recommendation = models.TextField(blank=True, null=True)
    phone_number = models.CharField(max_length=255, blank=True, null=True, unique=True)
    email = models.EmailField(verbose_name='email address', max_length=255, unique=True, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    gender = models.CharField(max_length=10, choices=User.GENDER_CHOICES, default=User.OTHER)
    medical_form = models.FileField(upload_to=medical_form_upload_path, blank=True, null=True)
    is_paid = models.BooleanField(default=False)
    status = models.CharField(choices=CONSULTATION_STATUS, default=CONSULTATION_STATUS[0][0], max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.patient_username)

    class Meta:
        ordering = ['-created_at']

class PatientReportSymptoms(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    consultation = models.ForeignKey(PatientReport, on_delete=models.CASCADE, related_name='patient_report_symptoms')
    symptoms = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.consultation)
    
    class Meta:
        ordering = ['-created_at']

class PatientPrescription(models.Model):
    TYPE_CHOICE = (
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly'),
    )
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    consultation = models.ForeignKey(PatientReport, on_delete=models.CASCADE, related_name='patient_prescriptions')
    prescription = models.CharField(max_length=255)
    frequence = models.IntegerField()
    type = models.CharField(max_length=8, choices=TYPE_CHOICE, default=TYPE_CHOICE[0][0])
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.consultation)
    
    class Meta:
        ordering = ['-created_at']

class PatientRecommendationForm(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    consultation = models.ForeignKey(PatientReport, on_delete=models.CASCADE, related_name='patient_recommendations_form')
    form = models.FileField(upload_to='recommendations', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.id)
    
    class Meta:
        ordering = ['-created_at']

class PatientLabTest(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    consultation = models.ForeignKey(PatientReport, on_delete=models.CASCADE, related_name='patient_lab_tests')
    name = models.CharField(max_length=255)
    description = models.TextField()
    result = models.TextField(blank=True, null=True)
    test_date = models.DateField(blank=True, null=True)
    file = models.FileField(upload_to='lab_tests', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.id)
    
    class Meta:
        ordering = ['-created_at']

class PatientPrescriptionForm(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    consultation = models.ForeignKey(PatientReport, on_delete=models.CASCADE, related_name='consultation_prescription')
    form = models.FileField(upload_to=prescribtion_form_upload_path, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.id)
    
    class Meta:
        ordering = ['-created_at']

class DependentsPrescriptionForm(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    consultation = models.ForeignKey(PatientDependentReport, on_delete=models.CASCADE, related_name='dependent_consultation_prescription')
    form = models.FileField(upload_to=prescribtion_form_upload_path, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.id)
    
    class Meta:
        ordering = ['-created_at']



class DependentsLabTest(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    consultation = models.ForeignKey(PatientDependentReport, on_delete=models.CASCADE, related_name='dependent_lab_tests')
    name = models.CharField(max_length=255)
    description = models.TextField()
    result = models.TextField(blank=True, null=True)
    test_date = models.DateField(blank=True, null=True)
    file = models.FileField(upload_to=lab_test_upload_path, blank=True, null=True)
    form = models.FileField(upload_to=lab_test_upload_path, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.id)
    
    class Meta:
        ordering = ['-created_at']


class DependentsRecommendation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    consultation = models.ForeignKey(PatientDependentReport, on_delete=models.CASCADE, related_name='dependent_recommendations')
    form = models.FileField(upload_to='recommendations', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.id)
    
    class Meta:
        ordering = ['-created_at']


# class PatientPayment(models.Model):
#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     consultation = models.OneToOneField(PatientReport, on_delete=models.CASCADE, related_name='patient_payments')
#     amount = models.DecimalField(max_digits=10, decimal_places=2)
#     transaction_ref = models.CharField(max_length=255)
#     appointments = models.OneToOneField(Appointement, on_delete=models.CASCADE, related_name='appointement_payments')
#     created_at = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return str(self.id)
    
#     class Meta:
#         ordering = ['-created_at']

# class DependentsPayment(models.Model):
#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     consultation = models.OneToOneField(PatientDependentReport, on_delete=models.CASCADE, related_name='dependent_payments')
#     amount = models.DecimalField(max_digits=10, decimal_places=2)
#     transaction_ref = models.CharField(max_length=255)
#     appointments = models.OneToOneField(Appointement, on_delete=models.CASCADE, related_name='dependent_appointement_payments')
#     created_at = models.DateTimeField(auto_now_add=True)