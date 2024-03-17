from django.db import models
from django.utils.translation import gettext_lazy as _
import uuid
from django.utils.html import format_html
# Create your models here.

from patients.models import Patient, CONSULTATION_TYPE
from doctors.models import Doctor


class DiseaseCategorie(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, blank=True, null=True)
    icon = models.ImageField(upload_to='disease_categories/', default='disease_categories/coronavirus_ihfs4i.png')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.name)
    
    @property
    def disease_icon(self):
        if self.icon:
            return format_html('<img src="{}" max-width="100%" height="50px" style="border:5px double #93BD68; padding:2px; margin:5px; border-radius:20px" />'.format(self.icon.url))

    class Meta:
        ordering = ['name']


class ServiceRates(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    rate = models.IntegerField(choices=((1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5')))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Service Rate")
        verbose_name_plural = _("Service Rates")
    
    def __str__(self):
        return str(self.rate)

class RatingService(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    service = models.CharField(_("Service"), max_length=100, choices=CONSULTATION_TYPE)
    rates = models.ManyToManyField(ServiceRates, related_name='service_rating')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Rating Service")
        verbose_name_plural = _("Rating Services")
    
    def __str__(self):
        return str(self.rating) 
    

class DoctorRate(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='patient_rate')
    rate = models.IntegerField(choices=((1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5')))
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def doctor(self):
        return self.patient_rating.all()
    
    class Meta:
        verbose_name = _("Doctor Rate")
        verbose_name_plural = _("Doctor Rates")
        ordering = ['-created_at']

class RatingDoctor(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    doctor = models.OneToOneField(Doctor, on_delete=models.CASCADE, related_name='doctor_rating')
    rates = models.ManyToManyField(DoctorRate, related_name='patient_rating')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Rating Doctor")
        verbose_name_plural = _("Rating Doctors")
    
    def __str__(self):
        return str(self.rating)
    
    @property
    def rates_average(self):
        return f"{self.rates.aggregate(models.Avg('rate'))['rate__avg']:.2f}"
    
    @property
    def doctor_rate_count(self):
        return self.rates.count()
    
    @property
    def get_all_rates(self):
        return self.rates.all()
