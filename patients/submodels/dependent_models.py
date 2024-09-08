import uuid

from django.db import models

from .patient_models import Patient
from accounts.models import User
from .utils import upload_path, medical_form_upload_path,lab_test_upload_path, CONSULTATION_TYPE, AI_CONSULTATION, CONSULTATION_STATUS
from doctors.models import Doctor



class Dependent(models.Model):
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
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='dependents')
    full_name = models.CharField(max_length=255)
    relationship = models.CharField(choices=RELATIONSHIP_CHOICES, max_length=10)
    # dependent_bithdate = models.DateField(blank=True, null=True)
    age = models.IntegerField()
    gender = models.CharField(choices=User.GENDER_CHOICES,max_length=10)
    blood_group = models.CharField(choices=Patient.BLOOD_GROUP_CHOICES, default=Patient.BLOOD_GROUP_CHOICES[0][1],max_length=10, blank=True, null=True)
    alergies = models.TextField( blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return str(self.id)
    
    class Meta:
        ordering = ['-created_at']

class DependentProfilePicture(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(Dependent, on_delete=models.CASCADE, related_name='dependent_profile_picture')
    profile_picture = models.ImageField(upload_to=upload_path, default='default/default_profile_picture.png')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.user)
    
    class Meta:
        ordering = ['-created_at']



# class DependentsPayment(models.Model):
#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     consultation = models.OneToOneField(PatientDependentReport, on_delete=models.CASCADE, related_name='dependent_payments')
#     amount = models.DecimalField(max_digits=10, decimal_places=2)
#     transaction_ref = models.CharField(max_length=255)
#     appointments = models.OneToOneField(Appointement, on_delete=models.CASCADE, related_name='dependent_appointement_payments')
#     created_at = models.DateTimeField(auto_now_add=True)

