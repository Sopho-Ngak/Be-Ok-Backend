from typing import Any
from django.contrib import admin
from accounts.models import User, VerificationCode
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from accounts.forms import UserAdminChangeForm, UserAdminCreationForm, UserCreationForm


class UserAdmin(BaseUserAdmin):
    form = UserAdminChangeForm
    add_form = UserAdminCreationForm

    list_display = ('username', 'email', 'admin', )
    list_filter = ('admin',)
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
                )
            }
        ),
    )

    add_fieldsets = ((None, {
        'classes': ('wide',),
        'fields': (
            'username',
            'email',
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

    def save_model(self, request: Any, obj, form: Any, change: Any) -> None:
        if change:
            if obj.user_type == User.ADMIN:
                obj.staff = True        
        return super().save_model(request, obj, form, change)


admin.site.register(User, UserAdmin)
admin.site.register(VerificationCode)
