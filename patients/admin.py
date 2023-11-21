from django.contrib import admin

from patients.models import Patient, PatientReport, PatientDependentReport, Appointement
# Register your models here.

@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ('patient_username', 'blood_group', 'created_at')
    list_filter = ('blood_group', 'created_at')

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        if request.user.is_superuser:
            return queryset
        return queryset.filter(patient_username__admin=False)

@admin.register(PatientReport)
class PatientReportAdmin(admin.ModelAdmin):
    list_display = ('patient_username', 'consulted_by_doctor', 'consultation_type', 'pain_area', )
    list_filter = ('consultation_type', 'created_at')
    search_fields = (
        'patient_username__user__username', 
        'patient_username__user__full_name', 
        'patient_username__user__email', 
        'patient_username__user__phone_number', 
        'consulted_by_doctor__user__username', 
        'consulted_by_doctor__user__full_name', 
        'consulted_by_doctor__user__email', 
        'consulted_by_doctor__user__phone_number',
        )
    
@admin.register(PatientDependentReport)
class PatientDependentReportAdmin(admin.ModelAdmin):
    list_display = ('patient_username', 'dependent_names', 'dependent_relationship', 'consulted_by_doctor',)
    list_filter = ('dependent_blood_group', 'created_at')
    search_fields = (
        'consulted_by_doctor__user__username', 
        'consulted_by_doctor__user__full_name', 
        'consulted_by_doctor__user__email', 
        'consulted_by_doctor__user__phone_number',
        )

@admin.register(Appointement)
class AppointementAdmin(admin.ModelAdmin):
    list_display = ('patient', 'doctor', 'consultation_type', 'start_date', 'end_date', )
    list_filter = ( 'is_confirmed','created_at',)

