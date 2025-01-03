import uuid
from django.utils import timezone

from django.db import models

from .patient_models import Patient
from accounts.models import User
from .utils import CONSULTATION_TYPE, PAIN_AREA_CHOICES
from doctors.models import Doctor, DoctorAvailability
from .consultation_models import PatientReport
from .consultation_models import PatientDependentReport

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
    consultation_type = models.CharField(choices=CONSULTATION_TYPE, default='online', max_length=255, blank=True, null=True)
    describe_disease = models.TextField(blank=True, null=True)
    doctor_availability = models.ForeignKey(DoctorAvailability, on_delete=models.CASCADE, related_name='doctor_availability')
    is_paid = models.BooleanField(default=False)
    pain_area = models.CharField(choices=PAIN_AREA_CHOICES, default=PAIN_AREA_CHOICES[11][1], max_length=255, blank=True, null=True)
    state = models.CharField(choices=APPOINTEMENT_STATE, default=APPOINTEMENT_STATE[0][1], max_length=50, blank=True, null=True)
    status = models.CharField(choices=APPOINTEMENT_STATUS, default=APPOINTEMENT_STATUS[2][0], max_length=50)
    user_concerned = models.CharField(choices=PATIENT_CONCERN_CHOICES, default=MYSELF, max_length=50)
    rejection_reason = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.patient)
    
    @property
    def day(self):
        return  self.doctor_availability.starting_date.day
    
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
        ordering = ['doctor_availability__starting_date']


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

