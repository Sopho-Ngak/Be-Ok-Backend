from django.contrib import admin
from django.utils.html import format_html

from hospital.models import Hospital, OpeningHours, Galery, Service
# Register your models here.

class OpeningHoursInline(admin.TabularInline):
    model = OpeningHours
    extra = 0
    readonly_fields = ('created_at', 'updated_at')

class ServiceInLine(admin.TabularInline):
    model = Service
    extra = 0
    readonly_fields = ('created_at', 'updated_at')
    search_fields = ('name')

class GaleryInline(admin.TabularInline):
    model = Galery
    extra = 0
    readonly_fields = ('image_shown','created_at', 'updated_at')
    fields = ('image','image_shown', 'created_at', 'updated_at')

    def image_shown(self, obj):
        if obj.image:
            return format_html('<img src="{}" max-width="100%" height="50%" style="border:3px double #93BD68; padding:2px; margin:5px; border-radius:10px" />'.format(obj.image.url))
        else:
            return format_html('<img src="{}" max-width="100%" height="50%" style="border:2px double #93BD68; padding:2px; margin:5px; border-radius:20px" />'.format("https://www.freeiconspng.com/uploads/no-image-icon-15.png"))




@admin.register(Hospital)
class HospitalAdmin(admin.ModelAdmin):
    list_display = ('name', 'address', 'city', 'state', 'country', 'phone', 'email', 'created_at', 'updated_at')
    list_filter = ('city', 'state', 'country', 'created_at', 'updated_at')
    search_fields = ('name', 'address', 'city', 'state', 'country', 'phone', 'email', 'website')
    inlines = [ServiceInLine, OpeningHoursInline, GaleryInline,]
    fieldsets = (
        ('Information about the hospital/clinic', {
            'fields': (
                'name',
                'address',
                'city',
                'state',
                'country',
                'phone',
                'email',
                'website',
            )
        }),
        (
            'Date Information',
            {
                'fields': (
                    'created_at',
                    'updated_at',
                )
            }
        ),
    )
    readonly_fields = ('created_at', 'updated_at')
