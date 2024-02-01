from django.contrib import admin
from django.utils.html import format_html

# Register your models here.

from settings.models import DiseaseCategorie

@admin.register(DiseaseCategorie)
class DiseaseCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'disease_icon', 'created_at')
    search_fields = ('name',)
    readonly_fields = ('disease_icon',)

    def disease_icon(self, obj):
        if obj.icon:
            return format_html('<img src="{}" max-width="100%" height="30px" style="border:3px double #93BD68; padding:2px; margin:5px; border-radius:10px" />'.format(obj.icon.url))
        else:
            return format_html('<img src="{}" max-width="100%" height="30px" style="border:2px double #93BD68; padding:2px; margin:5px; border-radius:20px" />'.format("https://www.freeiconspng.com/uploads/no-image-icon-15.png"))