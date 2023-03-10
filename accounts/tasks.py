from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.contrib.auth import get_user_model

from accounts.models import VerificationCode

from celery import shared_task

User = get_user_model()

@shared_task
def send_activation_code_via_email(id):
    # try:
    user_code = VerificationCode.objects.get(id=id)

    subject = _('Activate your account')
    from_email = settings.EMAIL_HOST_USER
    to = user_code.user.email
    context = {
        'code': user_code.code,
        'user': user_code.user
    }
    html_content = render_to_string('accounts/activation_email.html', context=context)
    text_content = strip_tags(html_content)

    msg = EmailMultiAlternatives(
        subject, text_content, from_email, [to])
    msg.attach_alternative(html_content, "text/html")
    msg.send()
    # except Exception as e:
    #     print(e)
