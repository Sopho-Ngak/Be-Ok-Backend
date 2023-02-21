from django.contrib import admin

# Register your models here.
from doctors.models import Doctor

admin.site.register(Doctor)