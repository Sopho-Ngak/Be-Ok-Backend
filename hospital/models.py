from email.policy import default
from enum import unique
from random import choices
import uuid

from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html


# Create your models here.
def upload_path(instance, filename):
    return '/'.join(['hospital', str(instance.hospital.name), filename])

days_choice = (
    ('Monday', 'Monday'),
    ('Tuesday', 'Tuesday'),
    ('Wednesday', 'Wednesday'),
    ('Thursday', 'Thursday'),
    ('Friday', 'Friday'),
    ('Saturday', 'Saturday'),
    ('Sunday', 'Sunday'),
)

class Hospital(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100)
    phone = models.CharField(max_length=100, unique=True, blank=True, null=True)
    email = models.EmailField(_("Email Address"),max_length=100, unique=True)
    website = models.URLField(max_length=1000, blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Hospital")
        verbose_name_plural = _("Hospitals")

    def __str__(self):
        return self.name
    
    @property
    def opening_hours(self):
        return self.hospital_opening_hour.all()
    

class Service(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    hostpital = models.ForeignKey(Hospital, on_delete=models.CASCADE, related_name='hospital_services')
    name = models.CharField(_("Service Name"), max_length=100)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

class Galery(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE, related_name='hospital_galery')
    image = models.ImageField(upload_to=upload_path)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Galery")
        verbose_name_plural = _("Galeries")
    
    @property
    def hospital_image(self):
        if self.image:
            return format_html('<img src="{}" max-width="100%" height="50px" style="border:5px double #93BD68; padding:2px; margin:5px; border-radius:20px" />'.format(self.image.url))

    def __str__(self):
        return self.hospital.name
    
class OpeningHours(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    hostpital = models.ForeignKey(Hospital, on_delete=models.CASCADE, related_name='hospital_opening_hour')
    day = models.CharField(max_length=20, choices=days_choice, default=days_choice[0][0])
    open_time = models.TimeField()
    close_time = models.TimeField()
    closed = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Opening Hour")
        verbose_name_plural = _("Opening Hours")

    def __str__(self):
        return self.day
