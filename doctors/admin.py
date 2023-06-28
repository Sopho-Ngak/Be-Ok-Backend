from django.contrib import admin

# Register your models here.
from doctors.models import Doctor, DoctorDocument, DoctorAvailability

@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ('user', 'city', 'physical_consultation', 'online_consultation')
    list_filter = ('physical_consultation', 'online_consultation', 'created_at')

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        if request.user.is_superuser:
            return queryset
        return queryset.filter(user__admin=False)

@admin.register(DoctorDocument)
class DoctorDocumentAdmin(admin.ModelAdmin):
    list_display = ('doctor', 'licence_number', 'is_approved', 'created_at')
    list_filter = ('is_approved', 'created_at')

@admin.register(DoctorAvailability)
class DoctorAvailabilityAdmin(admin.ModelAdmin):
    list_display = ('doctor', 'starting_date', 'ending_date', 'is_booked')
    list_filter = ('is_booked', 'created_at')