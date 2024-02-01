from django.urls import path, include

from rest_framework import routers

from doctors.views import DoctorViewSet

router = routers.DefaultRouter()

'''
    Here in this router.register() method, we are registering our viewset with the router.
    We use only one viewset for all the operations on the Doctor model. Bellow are the full urls for all the operations on the Doctor model:
        1. GET /doctor/doctor-profile -> doctor_profile -> get the doctor profile (let doctor get his/her own profile)
        2. GET /doctor/doctor-profile/?id=<doctor_uuid> -> get the doctor profile (let patient get doctor's profile)
        3. PATCH /doctor/doctor-profile  ->  update the doctor profile (let doctor update his/her own profile). NB: Doctor can only update his/her own profile and it's a partial update
        4. GET /doctor/doctor-documents -> doctor_documents -> get the doctor documents (let doctor get his/her own documents)
        5. PATCH /doctor/documents -> doctor_documents -> update the doctor documents (let doctor update his/her own documents). NB: Doctor can only update his/her own documents and it's a partial update
        6. GET /doctor/availabilities -> doctor_availabilities -> get the doctor availabilities (let doctor get his/her own availabilities)
        7. GET /doctor/availabilities/?id=<availabities_uuid> -> get availabilities by id (let patient get doctor's availabilities)
        8. GET /doctor/availabilities/?doctor=<doctor_uuid> -> get availabilities by doctor (let patient get all doctor's availabilities by his/her uuid)
        9. POST /doctor/availabilities -> doctor_availabilities -> create doctor availabilities (let doctor create his/her own availabilities)
        10. PATCH /doctor/availabilities/?id=<availability_uuid> -> doctor_availabilities -> update doctor availabilities (let doctor update his/her own availabilities). NB: Doctor can only update his/her own availabilities and it's a partial update
        11. GET /doctor/appointments -> doctor_appointments -> get all doctor's appointments (let doctor get his/her own appointments)
        12. GET /doctor/appointments/?id=<appointment_uuid> -> get appointment by id (let patient get doctor's appointment)
        13. PATCH /doctor/appointments/?doctor=<doctor_uuid> -> Confirm appointment (let doctor confirm appointment)
'''

router.register('doctor', DoctorViewSet, basename='user')

urlpatterns = [
    # path('get-disease', get_disease_groups, name='disease-groups'),
    path('', include(router.urls)),
]