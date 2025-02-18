from django.contrib import admin

from patients.models import (Patient, PatientReport, PatientDependentReport, Appointement, PatientPayment, DependentsPayment,
                             AiConsultationPatient, AIConsultationPatientSymptoms, AIConsultationPatientPrescription, WorkoutRoutine,
                             TreatmentFeedBack)
# Register your models here.

admin.site.register(PatientPayment)
admin.site.register(DependentsPayment)
admin.site.register(AiConsultationPatient)
admin.site.register(AIConsultationPatientSymptoms)
admin.site.register(AIConsultationPatientPrescription)


@admin.register(TreatmentFeedBack)
class TreatmentFeedBackAdmin(admin.ModelAdmin):
    list_display = ('patient', 'feedback', 'created_at')
    list_filter = ('created_at',)

@admin.register(WorkoutRoutine)
class WorkoutRoutineAdmin(admin.ModelAdmin):
    list_display = ('patient', 'routine')
    # list_filter = ( 'is_paid','status','state',)

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
    list_display = ('user', 'consulted_by_doctor', 'consultation_type', 'pain_area','is_paid','status', 'created_at')
    list_filter = ('consultation_type','is_paid','status', 'created_at')
    search_fields = (
        'user__user__username', 
        'user__user__full_name', 
        'user__user__email', 
        'user__user__phone_number', 
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
    list_display = ('patient', 'doctor', 'consultation_type', 'is_paid', 'status', 'state')
    list_filter = ( 'is_paid','status','state',)

