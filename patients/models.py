# Python import
import uuid

# Django imports
from django.db import models

# Local imports
from accounts.models import User
from doctors.models import Doctor

AI_CONSULTATION = 'AI'
IN_PERSON = 'In Person'
ONLINE = 'Online'

CONSULTATION_TYPE = (
    (AI_CONSULTATION, 'AI Consultation'),
    (IN_PERSON, 'In Person'),
    (ONLINE, 'Online'),
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
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    blood_group = models.CharField(choices=BLOOD_GROUP_CHOICES, default=BLOOD_GROUP_CHOICES[0][1],max_length=255, blank=True, null=True)
    alergies = models.TextField( blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.user)

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
    user = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='patient_reports')
    symptoms = models.TextField()
    consultated_by_doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='patient_consultated_by')
    consultation_type = models.CharField(choices=CONSULTATION_TYPE, default=AI_CONSULTATION, max_length=255, blank=True, null=True)
    pain_area = models.CharField(choices=PAIN_AREA_CHOICES, default=PAIN_AREA_CHOICES[11][1], max_length=255, blank=True, null=True)
    results = models.TextField()
    prescription = models.TextField(blank=True, null=True)
    recommended_tests = models.TextField(blank=True, null=True)
    recommendation = models.TextField(blank=True, null=True)
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
    user = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='patient_dependents')
    dependent_names = models.CharField(max_length=255)
    dependent_relationship = models.CharField(choices=RELATIONSHIP_CHOICES ,max_length=255)
    dependent_age = models.IntegerField()
    dependent_blood_group = models.CharField(max_length=255, blank=True, null=True)
    dependent_alergies = models.TextField( blank=True, null=True)
    dependent_symptoms = models.TextField()
    consulted_by_doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='dependent_consultated_by')
    dependent_results = models.TextField()
    phone_number = models.CharField(max_length=255, blank=True, null=True, unique=True)
    email = models.EmailField(verbose_name='email address', max_length=255, unique=True, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.dependent_names)

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


    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='patient_appointements')
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='doctor_appointements')
    service = models.CharField(choices=SERVICE_CHOICES, default=GENERAL_HEALTH, max_length=255)
    consultation_type = models.CharField(choices=CONSULTATION_TYPE, default=ONLINE, max_length=255, blank=True, null=True)
    appointment_date = models.DateField()
    appointment_time = models.TimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.patient)

    class Meta:
        ordering = ['-created_at']
