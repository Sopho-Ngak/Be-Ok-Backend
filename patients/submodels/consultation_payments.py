import uuid
from django.db import models
from .patient_models import Patient
from .consultation_models import AiConsultationPatient

class PatientAiPayment(models.Model):
    status_choice = (
        ('pending', 'Pending'),
        ('successful', 'Successful'),
        ('failed', 'Failed')
    )
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    consultation = models.ForeignKey(AiConsultationPatient, on_delete=models.CASCADE, related_name='ai_consultation_payment')
    transaction_ref = models.CharField(max_length=255, unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    proceed = models.BooleanField(default=False)
    status = models.CharField(max_length=10, choices=status_choice, default=status_choice[0][0])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Patient AI Payment'
        verbose_name_plural = 'Patient AI Payments'
        ordering = ('-updated_at',)
    
    def __str__(self) -> str:
        return str(self.consultation)