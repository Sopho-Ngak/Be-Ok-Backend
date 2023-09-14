from rest_framework.permissions import BasePermission, SAFE_METHODS
from accounts.models import User
from doctors.models import Doctor

class IsDoctor(BasePermission):
    message = "Only doctors can perform this action"

    def has_permission(self, request, view):
        if request.user.user_type == User.DOCTOR:
            return True
        else:
            return False

    def has_object_permission(self, request, view, obj):
        if obj.user == request.user:
            return True
        return False
    
class IsDoctorAndProfileOwner(BasePermission):
    message = "Only doctors and profile owner can perform this action"

    def has_permission(self, request, view):
        if request.user.user_type == User.DOCTOR:
            return True
        else:
            return False

    def has_object_permission(self, request, view, obj):
        if obj.user == Doctor.objects.get(user=request.user):
            return True
        return False
