from typing import Any
from django.contrib import admin
from django.http import HttpRequest
from django.utils.html import format_html
from django.forms import TypedChoiceField

from hospital.models import Hospital, OpeningHours, Galery, Service, days_choice
# Register your models here.

class OpeningHoursInline(admin.TabularInline):
    model = OpeningHours
    extra = 0
    readonly_fields = ('created_at', 'updated_at')

    # def changeform_view(self, request: HttpRequest, object_id: str | None = ..., form_url: str = ..., extra_context: dict[str, bool] | None = ...) -> Any:
    #     extra_context = extra_context or {}
    #     query = OpeningHours.objects.values_list('day', flat=True).distinct()
    #     list_days: list[tuple] = [(i,j) for i,j in days_choice if i not in query]
    #     if len(list_days) == 1:
    #         extra_context['show_save_and_add_another'] = False
    #     return super().changeform_view(request, object_id, form_url, extra_context)
    
    # def has_add_permission(self, request: HttpRequest, obj=None) -> bool:
    #     query = OpeningHours.objects.values_list('day', flat=True).distinct()
    #     list_days: list[tuple] = [(i,j) for i,j in days_choice if i not in query]
    #     if len(list_days) == 0:
    #         return False
    #     return True

    # def formfield_for_choice_field(self, db_field, request, **kwargs) -> TypedChoiceField:
    #     if db_field.name == 'day':
    #         if object_id := request.resolver_match.kwargs.get('object_id'):
    #             query = OpeningHours.objects.all().exclude(id=object_id)
    #             kwargs['choices'] = [
    #                 (i,j) for i, j in days_choice if i not in [k.day for k in query]
    #             ]
    #         else:
    #             query = OpeningHours.objects.values_list('day', flat=True)
    #             kwargs['choices'] = [
    #                 (i,j) for i, j in days_choice if i not in query
    #             ]
    #     return super().formfield_for_choice_field(db_field, request, **kwargs)
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
            return format_html('<img src="{}" max-width="200px" height="20%" style="border:3px double #93BD68; padding:2px; margin:5px; border-radius:10px" />'.format(obj.image.url))
        else:
            return format_html('<img src="{}" max-width="200px" height="20%" style="border:2px double #93BD68; padding:2px; margin:5px; border-radius:20px" />'.format("https://www.freeiconspng.com/uploads/no-image-icon-15.png"))




@admin.register(Hospital)
class HospitalAdmin(admin.ModelAdmin):
    list_display = ('name', 'address', 'city', 'state', 'country', 'phone', 'email', 'created_at', 'updated_at', 'main_photo_shown')
    list_filter = ('city', 'state', 'country', 'created_at', 'updated_at')
    search_fields = ('name', 'address', 'city', 'state', 'country', 'phone', 'email', 'website')
    inlines = [ServiceInLine, OpeningHoursInline, GaleryInline,]
    fieldsets = (
        ('Information about the hospital/clinics', {
            'fields': (
                'type',
                'main_photo',
                'name',
                'address',
                'city',
                'state',
                'country',
                'phone',
                'email',
                'website',
                'main_photo_shown'
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
    readonly_fields = ('created_at', 'updated_at', 'main_photo_shown')

    def main_photo_shown(self, obj):
        if obj.main_photo:
            return format_html('<img src="{}" max-width="100px" height="50" style="border:3px double #93BD68; padding:2px; margin:5px; border-radius:10px" />'.format(obj.image.url))
        else:
            return format_html('<img src="{}" max-width="100px" height="50" style="border:2px double #93BD68; padding:2px; margin:5px; border-radius:20px" />'.format("https://www.freeiconspng.com/uploads/no-image-icon-15.png"))

