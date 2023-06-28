# Python import
import uuid
import datetime

# Django imports
from django.db import models
from django.utils import timezone

# Local imports
from accounts.models import User

# Create your models here.

class Doctor(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='doctor')
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    specialties = models.CharField(max_length=450, blank=True, null=True)
    physical_consultation = models.BooleanField(default=False)
    online_consultation = models.BooleanField(default=False)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.user)
    
class DoctorDocument(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    doctor = models.OneToOneField(Doctor, on_delete=models.CASCADE, related_name='doctor_documents')
    licence_number = models.CharField(max_length=100, blank=True, null=True)
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
    starting_date = models.DateTimeField(blank=True, null=True)
    ending_date = models.DateTimeField(blank=True, null=True)
    is_booked = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.doctor)
    
    def save(self, *args, **kwargs):
        if self.starting_date and self.ending_date:
            if self.starting_date >= self.ending_date:
                raise ValueError("Ending date should be greater than starting date")
            
            elif self.starting_date < timezone.now():
                raise ValueError("Starting date should be greater than or egal to current date")
            
        if not self.starting_date or not self.ending_date:
            raise ValueError("Please provide starting date and ending date")
            
        super(DoctorAvailability, self).save(*args, **kwargs)


