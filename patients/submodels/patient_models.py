import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from accounts.models import User
# from .consultation_models import PatientReport


def workout_upload_path(instance, filename):
    return '/'.join(['chats', f"sender-{instance.sender.username}/receiver-{instance.receiver.username}", filename])


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
    weight = models.FloatField(blank=True, null=True)
    current_prescription = models.TextField( blank=True, null=True)
    current_treatment = models.TextField( blank=True, null=True)
    is_pregnant = models.BooleanField(default=False)
    has_childrens = models.BooleanField(default=False)
    has_family_members = models.BooleanField(default=False)
    location = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.patient_username)
    
    # def save(self, *args, **kwargs) -> None:
    #     if self.patient_username.gender == User.MALE and self.is_pregnant:
    #         raise Exception("This Patient cannot be pregnant")
    #     return super(Patient, self).save(*args, **kwargs)
    
    # @property
    # def doctors(self):
    #     return self.patient_username.doctor.all()

    class Meta:
        ordering = ['-created_at']


class WorkoutRoutine(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='workout_routine')
    icon = models.ImageField(upload_to=workout_upload_path, default='default/workout-default.png')
    routine = models.CharField(max_length=255)
    start_date = models.DateField()
    end_date = models.DateField()
    has_quited = models.BooleanField(default=False)
    # reminder_dates = models.JSONField(blank=True, null=True)
    # has_reminder = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def on_going(self):
        return self.start_date <= timezone.now().date() and self.end_date >= timezone.now().date()
    
    @property
    def is_completed(self):
        return self.end_date < timezone.now().date()
    
    @property
    def days_used_till_today(self):
        return  0 if not self.on_going else (timezone.now().date() - self.start_date).days
    
    
    
    @property
    def total_days(self):
        return (self.end_date - self.start_date).days
    
    @property
    def days_remaining_to_start(self):
        return (self.start_date - timezone.now().date()).days
    
    def __str__(self):
        return f"{self.patient} - {self.routine}"
    
    class Meta:
        ordering = ['-start_date']


class WorkoutRoutineReminder(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    routine = models.ForeignKey(WorkoutRoutine, on_delete=models.CASCADE, related_name='workout_routine_reminder')
    day = models.CharField(max_length=255)
    start_hour = models.TimeField()
    end_hour = models.TimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.routine)
    
    class Meta:
        ordering = ['-start_hour']


class DailyWorkoutRoutineTracker(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    routine =  models.ForeignKey(WorkoutRoutine, on_delete=models.CASCADE ,related_name='workout_routine_tracker')
    is_completed = models.BooleanField(default=False)
    date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.routine)
    
    class Meta:
        ordering = ['-created_at']
        


class Treatment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    medication = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    write_datetime = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.medication}"
    
    class Meta:
        ordering = ['-write_datetime']

class TreatmentTracker(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient = models.OneToOneField(Patient, on_delete=models.CASCADE, related_name='treatment_tracker')
    medications = models.ManyToManyField(Treatment, related_name='treatment_tracker_medication')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.patient)
    
class TreatmentFeedBack(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    feedback = models.TextField()
    medications = models.ManyToManyField(Treatment, related_name='treatment_feedback')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return str(self.patient)

class TreatmentCalendar(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='patient_treatment_calendar')
    treatment = models.ManyToManyField(Treatment, related_name='treatment_calendar')
    date = models.DateField()
    has_taken = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.patient}"
    
    class Meta:
        ordering = ['-date']


class PatientAccountHistory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='patient_account_history', db_index=True)
    field = models.CharField(max_length=255)
    value = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.patient)
    
    class Meta:
        ordering = ['-created_at']

class FamilyDisease(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='family_disease', db_index=True)
    disease = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.patient} - {self.disease}"
    
    class Meta:
        ordering = ['-created_at']
    
    



