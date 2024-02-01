from django.db import models
from django.utils.translation import gettext_lazy as _
import uuid
from django.utils.html import format_html
# Create your models here.


class BodyPart(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, blank=True, null=True)
    icon = models.ImageField(upload_to='body_parts/', blank=True, null=True)

    def __str__(self):
        return str(self.name)

    class Meta:
        ordering = ['name']

class DiseaseCategorie(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, blank=True, null=True)
    icon = models.ImageField(upload_to='disease_categories/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.name)
    
    @property
    def disease_icon(self):
        if self.icon:
            return format_html('<img src="{}" max-width="100%" height="50px" style="border:5px double #93BD68; padding:2px; margin:5px; border-radius:20px" />'.format(self.icon.url))

    class Meta:
        ordering = ['name']


class Hospital(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    opening_time = models.TimeField(blank=True, null=True)
    closing_time = models.TimeField(blank=True, null=True)