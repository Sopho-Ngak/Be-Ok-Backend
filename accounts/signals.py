import sys

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.utils.translation import gettext_lazy as _


from doctors.models import Doctor, DoctorDocument
from patients.models import Patient
from accounts.models import User, VerificationCode, ProfilePicture
from accounts.tasks import send_activation_code_via_email
from utils.generate_code import get_random_code



@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):

    if 'loaddata' in sys.argv:
            return
    
    if created:
        user_type = instance.user_type
        ProfilePicture.objects.get_or_create(user=instance)

        if user_type == User.DOCTOR:
            doctor_instance = Doctor.objects.create(user=instance)
            DoctorDocument.objects.create(doctor=doctor_instance)
        elif user_type == User.PATIENT:
            Patient.objects.create(patient_username=instance)
        user_code = VerificationCode.objects.create(user=instance, email=instance.email, code=get_random_code(4))
        return send_activation_code_via_email(user_code.id)
    
    if instance.user_type == User.DOCTOR:
        return Doctor.objects.get_or_create(user=instance)
    elif instance.user_type == User.PATIENT:
        return Patient.objects.get_or_create(patient_username=instance)

        # send email
        # try:
        #     subject = _('Activate your account')
        #     from_email = settings.EMAIL_HOST_USER
        #     to = user_code.user.email
        #     context = {
        #         'code': user_code.code,
        #         'user': user_code.user.full_name,
        #     }
        #     html_content = render_to_string('accounts/activation_email.html', context=context)
        #     text_content = strip_tags(html_content)

        #     msg = EmailMultiAlternatives(
        #         subject, text_content, from_email, [to])
        #     msg.attach_alternative(html_content, "text/html")
        #     msg.send()
        # except Exception as e:
        #     print(e)
        
