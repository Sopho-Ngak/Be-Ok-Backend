import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from accounts.models import User
# from .consultation_models import PatientReport


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
    identity_number = models.CharField(max_length=50, blank=True, null=True)
    blood_group = models.CharField(choices=BLOOD_GROUP_CHOICES, default=BLOOD_GROUP_CHOICES[0][1],max_length=10, blank=True, null=True)
    alergies = models.TextField( blank=True, null=True)
    chronic_diseases = models.TextField( blank=True, null=True)
    habits = models.TextField( blank=True, null=True)
    current_prescription = models.TextField( blank=True, null=True)
    current_treatment = models.TextField( blank=True, null=True)
    is_pregnant = models.BooleanField(default=False)
    has_childrens = models.BooleanField(default=False)
    has_family_members = models.BooleanField(default=False)
    location = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.patient_username)
    
    def save(self, *args, **kwargs) -> None:
        if self.patient_username.gender == User.MALE and self.is_pregnant:
            raise Exception("This Patient cannot be pregnant")
        return super(Patient, self).save(*args, **kwargs)

    class Meta:
        ordering = ['-created_at']

