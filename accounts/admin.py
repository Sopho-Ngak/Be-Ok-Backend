from typing import Any
from django.contrib import admin
from accounts.models import User, VerificationCode
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from accounts.forms import UserAdminChangeForm, UserAdminCreationForm
# groups
from django.contrib.auth.models import Group
from django.utils.translation import gettext_lazy as _


class UserAdmin(BaseUserAdmin):
    form = UserAdminChangeForm
    add_form = UserAdminCreationForm

    list_display = ('username','full_name', 'email', 'user_type','admin', )
    list_filter = ('admin','user_type', 'is_active',)
    fieldsets = (
        (None, {'fields': (
            'username',
            'email',
            'password'
        )}),
        (
            'Personal info',
            {
                'fields': (
                    'full_name',
                    'phone_number',
                    'address',
                    'user_type',
                )
            }
        ),

        (
            'Permissions',
            {
                'fields': (
                    'is_active',
                    'admin',
                    'staff',
                )
            }
        ),
    )

    add_fieldsets = ((None, {
        'classes': ('wide',),
        'fields': (
            'email',
            'full_name',
            'user_type',
            'password1',
            'password2',
        )}),)

    search_fields = (
        'username',
        'email',
        'full_name',
        'phone_number',
    )

    ordering = ('username',)
    filter_horizontal = ()
    actions = ['disable_user', 'enable_user']

    def disable_user(self, request, queryset):
        queryset.update(is_active=False)

    def enable_user(self, request, queryset):
        queryset.update(is_active=True)

    disable_user.short_description = "Disable selected users"
    enable_user.short_description = "Enable selected users"

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(is_superuser=False)

    def save_model(self, request: Any, obj, form: Any, change: Any) -> None:
        if change:
            if obj.user_type == User.ADMIN:
                obj.staff = True
                obj.admin = True        
        return super().save_model(request, obj, form, change)


admin.site.register(User, UserAdmin)
admin.site.register(VerificationCode)
admin.site.unregister(Group)

admin.site.site_header = "Be OK Admin"
admin.site.site_title = "Admin Portal"
admin.site.index_title = "Welcome to Be-Ok Admin Portal"
class MajorAdminPortal(admin.AdminSite):
    admin.site.index_title = _("")
    admin.site.site_title = _("Be-Ok")  
    admin.site.index_template = 'admin/custom_index.html'
    
    def has_permission(self, request) -> bool:
        return False
