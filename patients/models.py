# Python import
from typing import Iterable, Optional
import uuid
import datetime
# Django imports
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

# Local imports
from accounts.models import User
from doctors.models import Doctor, DoctorAvailability


def medical_form_upload_path(instance, filename):
    return '/'.join(['medical_forms', str(instance.patient_username.patient_username), filename])

def prescribtion_form_upload_path(instance, filename):
    return '/'.join(['prescriptions', str(instance.consultation.patient_username), filename])

def lab_test_upload_path(instance, filename):
    return '/'.join(['lab_tests', str(instance.consultation.patient_username.patient_username), filename])


AI_CONSULTATION = 'ai'
IN_PERSON = 'inperson'
ONLINE = 'online'

CONSULTATION_TYPE = (
    (AI_CONSULTATION, 'AI Consultation'),
    (IN_PERSON, 'In Person'),
    (ONLINE, 'Online'),
    )

CONSULTATION_STATUS = (
    ('pending', 'Pending'),
    ('completed', 'Completed'),
    ('cancelled', 'Cancelled'),
    ('rescheduled', 'Rescheduled'),
    ('inprogress', 'In Progress'),
    )

class Patient(models.Model):
    BLOOD_GROUP_CHOICES = (
        ('--', '--'),
        ('A+', 'A+'),
        ('A-', 'A-'),
        ('B+', 'B+'),
        ('B-', 'B-'),
        ('AB+', 'AB+'),
        ('AB-', 'AB-'),
        ('O+', 'O+'),
        ('O-', 'O-'),
    )
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient_username = models.OneToOneField(User, on_delete=models.CASCADE)
    blood_group = models.CharField(choices=BLOOD_GROUP_CHOICES, default=BLOOD_GROUP_CHOICES[0][1],max_length=255, blank=True, null=True)
    alergies = models.TextField( blank=True, null=True)
    chronic_diseases = models.TextField( blank=True, null=True)
    habits = models.TextField( blank=True, null=True)
    current_prescription = models.TextField( blank=True, null=True)
    is_pregnant = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.patient_username)
    
    def save(self, *args, **kwargs) -> None:
        if self.patient_username.gender == User.MALE and self.is_pregnant:
            raise Exception("This Patient cannot be pregnant")
        return super(Patient, self).save(*args, **kwargs)

    class Meta:
        ordering = ['-created_at']



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

    FOCUS_AREA_CHOICES = (
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
    )

    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient_username = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='patient_reports')
    symptoms = models.TextField()
    consulted_by_doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='patient_consultated_by')
    consultation_type = models.CharField(choices=CONSULTATION_TYPE, default=AI_CONSULTATION, max_length=255, blank=True, null=True)
    pain_area = models.CharField(choices=PAIN_AREA_CHOICES, default=PAIN_AREA_CHOICES[11][1], max_length=255, blank=True, null=True)
    results = models.TextField()
    prescription = models.TextField(blank=True, null=True)
    recommended_tests = models.TextField(blank=True, null=True)
    recommendation = models.TextField(blank=True, null=True)
    medical_form = models.FileField(upload_to=medical_form_upload_path, blank=True, null=True)
    is_paid = models.BooleanField(default=False)
    status = models.CharField(choices=CONSULTATION_STATUS, default=CONSULTATION_STATUS[0][0], max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.patient_username)
    
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


class Appointement(models.Model):
    MENTAAL_HEALTH = 'Mental Health'
    FERTILITY = 'Fertility'
    STI = 'STI Sexually Transmitted Infection'
    GENERAL_HEALTH = 'General Health'
    PEDRIATRICS = 'Pedriatrics'
    GYNECOLOGY = 'Gynecology'
    INTERNAL_MEDICINE = 'Internal Medicine'
    CHRONIC_DISEASE = 'Chronic Disease'

    MYSELF = 'me'
    DEPENDENT = 'dependent'

    PATIENT_CONCERN_CHOICES = (
        (MYSELF, 'me'),
        (DEPENDENT, 'Dependent'),
    )

    SERVICE_CHOICES = (
        (MENTAAL_HEALTH, 'Mental Health'),
        (FERTILITY, 'Fertility'),
        (STI, 'STI Sexually Transmitted Infection'),
        (GENERAL_HEALTH, 'General Health'),
        (PEDRIATRICS, 'Pedriatrics'),
        (GYNECOLOGY, 'Gynecology'),
        (INTERNAL_MEDICINE, 'Internal Medicine'),
        (CHRONIC_DISEASE, 'Chronic Disease'),
    )
    ACCEPTED = 'accepted'
    REJECTED = 'rejected'
    PENDING = 'pending'
    CANCELLED = 'cancelled'

    INPROGRESS = 'inprogress'
    COMPLETED = 'completed'

    APPOINTEMENT_STATE = (
        (PENDING, 'Pending'),
        (INPROGRESS, 'In Progress'),
        (COMPLETED, 'Completed'),
    )

    APPOINTEMENT_STATUS = (
    (ACCEPTED, 'Accepted'),
    (REJECTED, 'Rejected'),
    (PENDING, 'Pending'),
    (CANCELLED, 'Cancelled'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='patient_appointements')
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='doctor_appointements')
    service = models.CharField(choices=SERVICE_CHOICES, default=GENERAL_HEALTH, max_length=255)
    consultation_type = models.CharField(choices=CONSULTATION_TYPE, default=ONLINE, max_length=255, blank=True, null=True)
    describe_disease = models.TextField(blank=True, null=True)
    doctor_availability = models.ForeignKey(DoctorAvailability, on_delete=models.CASCADE, related_name='doctor_availability')
    is_paid = models.BooleanField(default=False)
    pain_area = models.CharField(choices=PatientReport.PAIN_AREA_CHOICES, default=PatientReport.PAIN_AREA_CHOICES[11][1], max_length=255, blank=True, null=True)
    state = models.CharField(choices=APPOINTEMENT_STATE, default=APPOINTEMENT_STATE[0][1], max_length=50, blank=True, null=True)
    status = models.CharField(choices=APPOINTEMENT_STATUS, default=APPOINTEMENT_STATUS[2][0], max_length=50)
    user_concerned = models.CharField(choices=PATIENT_CONCERN_CHOICES, default=MYSELF, max_length=50)
    rejection_reason = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.patient)
    
    @property
    def day(self):
        return  self.doctor_availability.day 
    
    @property
    def payment(self):
        if self.user_concerned == 'me':
            try:
                return PatientPayment.objects.get(appointments=self)
            except PatientPayment.DoesNotExist:
                return None
        else:
            try:
                return DependentsPayment.objects.get(appointments=self)
            except DependentsPayment.DoesNotExist:
                return None
    @property
    def start_date(self):
        return self.doctor_availability.starting_date
    
    @property
    def end_date(self):
        return self.doctor_availability.ending_date
    
    def happend_in(self):
        time_remaining = self.start_date - timezone.now()

        data = {
            'days': time_remaining.days,
            'hours': time_remaining.seconds // 3600,
            'minutes': (time_remaining.seconds // 60) % 60,
            'seconds': time_remaining.seconds % 60
        }
        return data

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

class PatientRecommendation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    consultation = models.ForeignKey(PatientReport, on_delete=models.CASCADE, related_name='patient_recommendations')
    form = models.FileField(upload_to='recommendations', blank=True, null=True)
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

class PatientPayment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    consultation = models.OneToOneField(PatientReport, on_delete=models.CASCADE, related_name='patient_payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_ref = models.CharField(max_length=255)
    appointments = models.OneToOneField(Appointement, on_delete=models.CASCADE, related_name='appointement_payments')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.id)
    
    class Meta:
        ordering = ['-created_at']

class DependentsPayment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    consultation = models.OneToOneField(PatientDependentReport, on_delete=models.CASCADE, related_name='dependent_payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_ref = models.CharField(max_length=255)
    appointments = models.OneToOneField(Appointement, on_delete=models.CASCADE, related_name='dependent_appointement_payments')
    created_at = models.DateTimeField(auto_now_add=True)
