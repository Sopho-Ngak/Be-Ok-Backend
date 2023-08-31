from django.contrib import admin
from django.utils.html import format_html

# Register your models here.
from doctors.models import Doctor, DoctorDocument, DoctorAvailability, DiseaseGroup, Disease

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



class Diseases(admin.TabularInline):
    model = Disease
    extra = 1
    fields = ('name', 'icon', 'disease_icon')
    readonly_fields = ('disease_icon',)

    # def disease_icon(self, obj):
    #     return format_html(f'<img src="{obj.icon.url}" max-width="100%" height="80px" style="border:5px double #93BD68; padding:2px; margin:5px; border-radius:20px"/>')
    



@admin.register(DiseaseGroup)
class DiseaseGroupAdmin(admin.ModelAdmin):
    list_display = ('name',"created_at")
    inlines = [Diseases]
    search_fields = ('name',)
