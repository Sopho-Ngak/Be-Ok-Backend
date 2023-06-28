from django.utils import timezone
from django.db.models import Q
from accounts.models import User
from doctors.models import DoctorDocument



def add_variable_to_context(request):

    if request.user.is_anonymous:
        return {}

    else:
        labels = ['Total Doctors', 'Total Patient', 'Unverified Doctore', 'Verified Doctors']
        doctors = User.objects.filter(user_type=User.DOCTOR).count()
        patients = User.objects.filter(user_type=User.PATIENT, admin=False).count()
        unverified_doctors = DoctorDocument.objects.filter(is_approved=False).count()
        approved_doctors = DoctorDocument.objects.filter(is_approved=True).count()
        admins = User.objects.filter(admin=True, is_superuser=False).count()
        # owners = User.objects.filter(restaurant_owner__isnull=False).distinct().count()
        # total_restaurants_owned = Restaurant.objects.filter(owner__isnull=False).count()
        # total_restaurants_not_owned = Restaurant.objects.filter(owner__isnull=True).count()
        # restaurants_chart_data = Restaurant.objects.all().count()
        # musicians = User.objects.filter(user_type=User.ENTERTAINER).count()
        data = [doctors, patients, unverified_doctors, approved_doctors,]
        return {
            'chart_labels': labels,
            'chart_data': data,
            'doctor_chart_data':doctors,
            'patient_chart_data':patients,
            'restaurants_chart_data':unverified_doctors,
            'owners_chart_data':approved_doctors,
            'admins_chart_data':admins,
            }
        