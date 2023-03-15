# Python import
import uuid

# Django imports
from django.db import models

# Local imports
from accounts.models import User
from doctors.models import Doctor


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
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='patient_reports')
    symptoms = models.TextField()
    consultated_by_doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='patient_consultated_by')
    results = models.TextField()
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
