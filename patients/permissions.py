from rest_framework.permissions import BasePermission, SAFE_METHODS
from accounts.models import User
from patients.models import Patient

class IsPatient(BasePermission):
    message = "Only BeOk patient can perform this action"

    def has_permission(self, request, view):
        if request.user.user_type == User.PATIENT:
            return True
        else:
            return False

    def has_object_permission(self, request, view, obj):
        if obj.patient_username == request.user and Patient.objects.filter(patient_username=request.user).exists():
            return True
        return False
    
class IsDoctorOrPatient(BasePermission):
    message = "Only BeOK doctors and patient can perform this action"

    def has_permission(self, request, view):
        if request.user.user_type == User.DOCTOR or request.user.user_type == User.PATIENT:
            return True
        else:
            return False

    def has_object_permission(self, request, view, obj):
        if obj.user == Patient.objects.get(patient_username=request.user):
            return True
        return False
