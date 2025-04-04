# Python import
import uuid
import datetime

# Django imports
from django.db import models
from django.utils import timezone
from django.utils.html import format_html
from django.utils.translation import gettext as _


# Local imports
from accounts.models import User

# Create your models here.

class Doctor(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='doctor')
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    specialties = models.CharField(max_length=450, blank=True, null=True)
    profession = models.CharField(max_length=100, blank=True, null=True)
    physical_consultation = models.BooleanField(default=False)
    online_consultation = models.BooleanField(default=False)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.user)
    
    @property
    def is_approved(self):
        return self.doctor_documents.is_approved
    
    @property
    def patients_consulted(self):
        return self.patient_consultated_by.all()
    
    @property
    def dependents_consulted(self):
        return self.dependent_consultated_by.all()
    
class DoctorDocument(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    doctor = models.OneToOneField(Doctor, on_delete=models.CASCADE, related_name='doctor_documents')
    licence_number = models.CharField(max_length=100, blank=True, null=True)
    identity_number = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text=_("This is optional but recommended for better verification of doctor identity.")
    )
    document = models.FileField(upload_to='Doctor/documents/')
    is_approved = models.BooleanField(default=False)
    approved_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='approved_doctor_documents', blank=True, null=True)
    approved_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.doctor)
    
class DoctorAvailability(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='doctor_availabilities')
    starting_date = models.DateTimeField()
    ending_date = models.DateTimeField()
    is_booked = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.doctor)
    
    # def save(self, *args, **kwargs):
    #     if self.starting_date and self.ending_date:
    #         if self.starting_date >= self.ending_date:
    #             raise ValueError("Ending date should be greater than starting date")
            
    #         elif self.starting_date < timezone.now():
    #             raise ValueError("Starting date should be greater than or egal to current date")

    #     super(DoctorAvailability, self).save(*args, **kwargs)

# class DiseaseGroup(models.Model):
#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     name = models.CharField(max_length=255, unique=True)
#     created_at = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return self.name
    
# class Disease(models.Model):
#     id = models.UUIDField(
#         primary_key=True, default=uuid.uuid4, editable=False)
#     group = models.ForeignKey(
#         DiseaseGroup, on_delete=models.CASCADE, related_name='disease_description')
#     name = models.CharField(max_length=255, unique=True)
#     icon = models.ImageField(
#         _("Add disease icon here"), upload_to='diseases_icons', blank=True, null=True)
#     created_at = models.DateTimeField(auto_now_add=True)

#     @property
#     def disease_icon(self):
#         if self.icon:
#             return format_html('<img src="{}" max-width="100%" height="50px" style="border:5px double #93BD68; padding:2px; margin:5px; border-radius:20px" />'.format(self.icon.url))

#     def __str__(self):
#         return self.name


