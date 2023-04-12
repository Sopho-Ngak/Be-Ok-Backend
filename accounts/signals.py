from django.db.models.signals import post_save
from django.dispatch import receiver
from doctors.models import Doctor
from patients.models import Patient
from accounts.models import User, VerificationCode
from accounts.tasks import send_activation_code_via_email
from utils.generate_code import get_random_code


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        user_type = instance.user_type

        if user_type == User.DOCTOR:
            Doctor.objects.create(user=instance)
        elif user_type == User.PATIENT:
            Patient.objects.create(user=instance)
        user_code = VerificationCode.objects.create(user=instance, email=instance.email, code=get_random_code(4))
        #return send_activation_code_via_email.delay(user_code.id)
        
