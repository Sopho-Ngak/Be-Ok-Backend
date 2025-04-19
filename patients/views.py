# Python imports

# Django imports
from django.conf import settings
from django.db.models import Q
from django.utils import timezone

# Third party imports
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny


# Local imports
import patients
from patients.models import (Patient, PatientReport, PatientDependentReport, Appointement, PatientPrescriptionForm, DependentsPrescriptionForm, PatientLabTest, 
                             DependentsLabTest, PatientRecommendationForm, DependentsRecommendation, PatientPayment, DependentsPayment, ONLINE, Dependent,
                             DependentProfilePicture, WorkoutRoutine, TreatmentTracker, TreatmentCalendar, Treatment, FamilyDisease)
from doctors.models import Doctor, DoctorAvailability
from accounts.models import User
from accounts.serializers import UserInfoSerializer
from patients.permissions import IsPatient, IsDoctorOrPatient
from patients.serializers import (PatientSerializer,AiConsultationPatientSerializer, PatientInfoSerializer, PatientEditProfileSerializer, PatientReportSerializer, PatientDependentReportSerializer,
                                  PatientPaymentStatusSerializer, PatientCashInSerializer, AppointmentSerializer, PatientPrescriptionFormSerializer,
                                  DependentsPrescriptionFormSerializer, PatientLabTestSerializer, DependentsLabTestSerializer, PatientRecommendationSerializer,
                                  DependentsRecommendationSerializer, TreatmentTrackerSerializer, UpdateAppointmentSerializer, PatientRegistrationSerializer, DependentInfoSerializer, DependentSerializer, AiConsultationInfoPatientSerializer,
                                  GeneralHealgthViewSerialize, WorkoutRoutineSerializer, TreatmentFeedBackSerializer, TreatmentCalendarSerializer, PrescriptionViewsSectionSerializer, LabTestsViewsSectionSerializer, RecommandationViewsSectionSerializer,
                                  TreatmentSerializer, FamilyDiseaseSerializer, DailyWorkoutRoutineTrackerSerializer)
from doctors.serializers import (
    DoctorInfoSerializer)
from doctors.permissions import IsDoctor
from patients.submodels.consultation_models import AiConsultationPatient
from utils.ai_call import get_patient_result_from_ai
from utils.payment_module import Payment
from settings.models import BlackListedTransaction
# from utils.check_mispelled_word import check_and_autocorrect_mispelled_word


class PatientViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Patient.objects.all().order_by('patient_username__username')
    serializer_class = PatientSerializer

    # def get_queryset(self):
    #     if self.request.GET.get('name'):
    #         return Patient.objects.filter(name__icontains=self.request.Get.get('name'))
    #     return self.queryset

    # def get_permissions(self):
    #     return [AllowAny()]

    def get_serializer_class(self):
        if self.action == 'ai_consultation':
            return AiConsultationPatientSerializer
        elif self.action == 'get_patient_record':
            return PatientSerializer

        elif self.action == 'patient_profile':
            if self.request.method == 'PATCH':
                return PatientEditProfileSerializer
            elif self.request.method == 'GET':
                return PatientInfoSerializer

        elif self.action == 'patient_payment':
            if self.request.method == 'PUT':
                return PatientPaymentStatusSerializer
            elif self.request.method == 'POST':
                return PatientCashInSerializer

        elif self.action == 'patient_appointment':
            return AppointmentSerializer
        elif self.action == 'patient_prescription_form':
            return PatientPrescriptionFormSerializer
        elif self.action == 'dependents_prescription_form':
            return DependentsPrescriptionFormSerializer
        elif self.action == 'patient_lab_test':
            return PatientLabTestSerializer
        elif self.action == 'dependents_lab_test':
            return DependentsLabTestSerializer
        elif self.action == 'patient_recommendation':
            return PatientRecommendationSerializer
        elif self.action == 'dependents_recommendation':
            return DependentsRecommendationSerializer
        elif self.action == 'appointment_actions':
            return UpdateAppointmentSerializer
        elif self.action == 'register':
            return PatientRegistrationSerializer

        return super().get_serializer_class()

    def get_permissions(self):
        if self.action in [
            'ai_consultation', 'workout_routine', 'treatment_tracker', 'treatment_calendar',
            'general_health_views']:
            self.permission_classes = [IsAuthenticated, IsPatient]
        elif self.action == 'get_patient_record':
            self.permission_classes = [IsAuthenticated, IsDoctorOrPatient]
        elif self.action == 'patient_appointment':
            self.permission_classes = [IsAuthenticated, IsPatient]
        elif self.action == 'appointment_actions':
            if self.request.method == 'PUT':
                self.permission_classes += [IsPatient]
            elif self.request.method == 'PATCH':
                self.permission_classes += [IsDoctor]
        elif self.action == 'register':
            self.permission_classes = [AllowAny]
        elif self.action == 'patient_profile':
            if self.request.method == 'PATCH':
                self.permission_classes = [IsAuthenticated, IsPatient]
            # elif self.request.method == 'GET':
            #     self.permission_classes = [IsAuthenticated, IsPatient]
        # elif self.action == 'get_paid_result':
        #     self.permission_classes = [IsAuthenticated, IsPatient]
        return super().get_permissions()
    
    @action(detail=False, methods=['post'], url_path='registration')
    def register(self, request):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            serializer.instance.patient_username.set_password(serializer.validated_data.get('password'))
            serializer.instance.patient_username.save()

            patient_serializer = PatientInfoSerializer(serializer.instance, context={'request': request})
            
            return Response({
                "successMessage": "Account created successfully",
                "status_code": status.HTTP_201_CREATED,
                "data": patient_serializer.data
                }, status=status.HTTP_201_CREATED)
        
        error_data = ''
        if serializer.errors.get('email'):
            error_data += 'Email already exists. '
        if serializer.errors.get('phone_number'):
            error_data += 'Phone number already exists. '
        if serializer.errors.get('gender'):
            error_data += "Invalid gender. "
        if serializer.errors.get('marital_status'):
            error_data += "Invalid marital status. "
        if serializer.errors.get('date_of_birth'):
            error_data += "Invalid date of birth. "

        return Response({"errorMessage": error_data}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post', 'get', 'patch'], url_path='dependent')
    def patient_dependent(self, request):
        if request.method == 'POST':
            serializer = DependentSerializer(data=request.data, context={'request': request})
            if serializer.is_valid():
                serializer.save()
                return Response({
                    "successMessage": "Dependent created successfully",
                    "status_code": status.HTTP_201_CREATED,
                    "data": serializer.data}, status=status.HTTP_201_CREATED)
            
            error_data = ''
            serializer_errors: dict = serializer.errors
            if serializer_errors.get('full_name'):
                error_data += "Full name is required. "
            if serializer_errors.get('relationship'):
                error_data += "Relationship is required. "
            if serializer_errors.get('age'):
                if not isinstance(request.data.get('age'), int):
                    error_data += "Age should be an integer. "
                elif 'required' in serializer_errors['age'][0]:
                    error_data += "Age is required. "

                else:
                    error_data += f"{serializer_errors['age'][0]}. "
            if serializer_errors.get('gender') :
                if 'required' in serializer_errors['gender'][0]:
                    error_data += "gender is required. "
                else:
                    error_data += f"gender {serializer_errors['gender'][0]}. "
            if serializer_errors.get('profile_picture'):
                error_data += f"{serializer_errors['profile_picture'][0]}. "

            
            return Response({
                "errorMessage": error_data,
                "status_code": status.HTTP_400_BAD_REQUEST
                }, status=status.HTTP_400_BAD_REQUEST)

        
        elif request.method == 'GET':
            if request.query_params.get('id'):
                try:
                    dependent = Dependent.objects.get(id=request.query_params.get('id'), patient__patient_username=request.user)
                    serializer = DependentInfoSerializer(dependent, context={'request': request})
                    return Response(serializer.data, status=status.HTTP_200_OK)
                except Patient.DoesNotExist:
                    return Response({"message": "No dependent found with this id provided"}, status=status.HTTP_404_NOT_FOUND)
            
            dependents = Dependent.objects.filter(patient__patient_username=request.user)
            serializer = DependentInfoSerializer(dependents, many=True, context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        elif request.method == 'PATCH':
            if not request.query_params.get('id'):
                return Response({"error": "Depend ID is required"}, status=status.HTTP_400_BAD_REQUEST)
            try:
                dependent = Dependent.objects.get(id=request.query_params.get('id'), patient__patient_username=request.user)
                serializer = DependentInfoSerializer(dependent, data=request.data, partial=True, context={'request': request})
                serializer.is_valid(raise_exception=True)
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            except Patient.DoesNotExist:
                return Response({"message": "No dependent found with this id provided"}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['get'])
    def search(self, request):
        queryset = self.get_queryset()
        serializer = PatientSerializer(
            queryset, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path='doctors')
    def get_all_doctors(self, request):
        if request.method == 'GET':
            choice: str = request.query_params.get('choice')
            doctor_id = request.query_params.get('doctor_id')
            if choice and choice.lower() == 'my_doctors' and not doctor_id:
                doctors = Doctor.objects.filter(
                    Q(doctor_documents__is_approved=True,
                    patient_consultated_by__user__patient_username=request.user) |
                    Q(doctor_documents__is_approved=True,
                      dependent_consultated_by__patient_username__patient_username=request.user)
                )
            elif doctor_id and choice and choice.lower() == 'my_doctors':
                patient_reports = PatientReport.objects.filter(consulted_by_doctor__id=doctor_id)
                dependent_reports = PatientDependentReport.objects.filter(consulted_by_doctor__id=doctor_id)
                data = {
                    'patient_reports': PatientReportSerializer(patient_reports, many=True, context={'request': request}).data,
                    'dependent_reports': PatientDependentReportSerializer(dependent_reports, many=True, context={'request': request}).data
                }
                return Response(data, status=status.HTTP_200_OK)
            else:
                doctors = Doctor.objects.filter(doctor_documents__is_approved=True)

            serializer = DoctorInfoSerializer(
                doctors, many=True, context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get', 'patch'], url_path='profile')
    def patient_profile(self, request):
        if request.method == "GET":
            try:
                instance = Patient.objects.get(patient_username=request.user)
                serializer = self.get_serializer(
                    instance, context={'request': request})
                return Response(serializer.data, status=status.HTTP_200_OK)
            except Patient.DoesNotExist:
                return Response({"message": "No patient found"}, status=status.HTTP_200_OK)

        elif request.method == "PATCH":
            try:
                instance = Patient.objects.get(patient_username=request.user)
                serializer = self.get_serializer(
                    instance, data=request.data, partial=True, context={'request': request})
                if serializer.is_valid():
                    serializer.save()
                    return Response({
                        "successMessage":"Profile updated successfully",
                        "status_code": status.HTTP_200_OK,
                        "data": serializer.data
                        }, status=status.HTTP_200_OK)
                                
                error_data = ''
                if serializer.errors.get('blood_group'):
                    error_data += "Invalid blood group. "
                if serializer.errors.get("weight"):
                    error_data += "Invalid weight number. "
                if serializer.errors.get("gender"):
                    error_data +="Invalid gender. "
                if serializer.errors.get("marital_status"):
                    error_data += "Invalid marital status. "
                if serializer.errors.get("date_of_birth"):
                    error_data += "Invalid date of birth format. "
                if serializer.errors.get("phone_number"):
                    error_data += serializer.errors["phone_number"][0]
                if serializer.errors.get("is_pregnant"):
                    error_data += "You cannot be pregnant as you are a male. "
                if serializer.errors.get("profile_image"):
                    error_data += "Invalid profile image. "
                if serializer.errors.get("height"):
                    error_data += "Invalid height number. "

                

                return Response({
                    "errorMessage": error_data,
                    "status_code":status.HTTP_400_BAD_REQUEST
                    }, status=status.HTTP_400_BAD_REQUEST)


            except Patient.DoesNotExist:
                return Response(
                    {"errorMessage": settings.PATIENT_CONSTANTS.messages.PATIENT_DOES_NOT_EXIST},
                    status=status.HTTP_404_NOT_FOUND
                )
            
    @action(detail=False, methods=['get', 'post', 'patch'], url_path='workout-routine')
    def workout_routine(self, request):
        if request.method == 'POST':
            if request.query_params.get('set'):
                if request.query_params.get('set').lower() not in ['tracker']:
                    return Response({"message": "Invalid query param value"}, status=status.HTTP_400_BAD_REQUEST)
                
                serializer = DailyWorkoutRoutineTrackerSerializer(
                    data=request.data, context={'request': request})
                serializer.is_valid(raise_exception=True)
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            
            serializer = WorkoutRoutineSerializer(
                data=request.data, context={'request': request})
            serializer.is_valid(raise_exception=True)
            serializer.save(patient=Patient.objects.get(patient_username=request.user))
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        elif request.method == 'GET':
            if request.query_params.get('routine_id'):
                try:
                    workout = WorkoutRoutine.objects.get(id=request.query_params.get('routine_id'))
                    serializer = WorkoutRoutineSerializer(
                        workout, context={'request': request})
                    return Response(serializer.data, status=status.HTTP_200_OK)
                except WorkoutRoutine.DoesNotExist:
                    return Response({"message": "No workout routine found with this id provided"}, status=status.HTTP_404_NOT_FOUND)

            workouts = WorkoutRoutine.objects.filter(patient__patient_username=request.user)
            serializer = WorkoutRoutineSerializer(
                workouts, many=True, context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)

        elif request.method == 'PATCH':
            if not request.query_params.get('routine_id'):
                return Response({"message": "Please provide an id"}, status=status.HTTP_400_BAD_REQUEST)
            try:
                workout = WorkoutRoutine.objects.get(id=request.query_params.get('routine_id'))
                serializer = WorkoutRoutineSerializer(
                    workout, data=request.data, partial=True, context={'request': request})
                serializer.is_valid(raise_exception=True)
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            except WorkoutRoutine.DoesNotExist:
                return Response({"message": "No workout routine found with this id provided"}, status=status.HTTP_404_NOT_FOUND)
            
    @action(detail=False, methods=['get', 'post', 'patch', 'delete'], url_path='treament-tracker')
    def treatment_tracker(self, request):
        action_choice: str = request.query_params.get('action_choice')

        if action_choice and action_choice.lower() not in ['feedback', 'create']:
                return Response({"message": "Invalid action choice"}, status=status.HTTP_400_BAD_REQUEST)
        
        if request.method == 'POST':
            if action_choice and  action_choice.lower() == 'feedback':
                serializer = TreatmentFeedBackSerializer(
                    data=request.data, context={'request': request})
                serializer.is_valid(raise_exception=True)
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            
            serializer = TreatmentTrackerSerializer(
                data=request.data, context={'request': request})
            serializer.is_valid(raise_exception=True)
            serializer.save()

            # serializer = TreatmentTrackerSerializer(
            #     serializer.instance, context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        elif request.method == 'GET':
            try:
                treatments = TreatmentTracker.objects.get(
                    patient__patient_username=request.user)
                serializer = TreatmentTrackerSerializer(
                    treatments, context={'request': request})
                return Response(serializer.data, status=status.HTTP_200_OK)
            except TreatmentTracker.DoesNotExist:
                return Response({"message": "No treatment tracker found"}, status=status.HTTP_200_OK)

        elif request.method == 'PATCH':
            if not request.query_params.get('medication_id'):
                return Response({"message": "Please provide  medication_id"}, status=status.HTTP_400_BAD_REQUEST)
            try:
                treatment = Treatment.objects.get(
                    id=request.query_params.get('medication_id'))
                serializer = TreatmentSerializer(
                    treatment, data=request.data, partial=True, context={'request': request})
                serializer.is_valid(raise_exception=True)
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            except Treatment.DoesNotExist:
                return Response({"message": "No medication found with this id provided"}, status=status.HTTP_404_NOT_FOUND)
            
        elif request.method == 'DELETE':
            if not request.query_params.get('medication_id'):
                return Response({"message": "Please provide  medication_id"}, status=status.HTTP_400_BAD_REQUEST)
            try:
                treatment = Treatment.objects.get(
                    id=request.query_params.get('medication_id'))
                treatment.is_active = False
                treatment.save()
                return Response({"message": "Medication deleted successfully"}, status=status.HTTP_200_OK)
            except Treatment.DoesNotExist:
                return Response({"message": "No medication found with this id provided"}, status=status.HTTP_404_NOT_FOUND)
            

    @action(detail=False, methods=['get', 'post', 'patch'], url_path='treatment-calendar')
    def treatment_calendar(self, request):
        if request.method == 'POST':
            serializer = TreatmentCalendarSerializer(
                data=request.data, context={'request': request})
            serializer.is_valid(raise_exception=True)
            serializer.save(patient=Patient.objects.get(patient_username=request.user))
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        elif request.method == 'GET':
            if request.query_params.get('day_id'):
                try:
                    calendar = TreatmentCalendar.objects.get(id=request.query_params.get('day_id'))
                    serializer = TreatmentCalendarSerializer(
                        calendar, context={'request': request})
                    return Response(serializer.data, status=status.HTTP_200_OK)
                except TreatmentTracker.DoesNotExist:
                    return Response({"message": "No treatment calendar found with this id provided"}, status=status.HTTP_404_NOT_FOUND)

            calendars = TreatmentCalendar.objects.filter(patient__patient_username=request.user)
            serializer = TreatmentCalendarSerializer(
                calendars, many=True, context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)

        elif request.method == 'PATCH':
            if not request.query_params.get('day_id'):
                return Response({"message": "Please provide an day id"}, status=status.HTTP_400_BAD_REQUEST)
            try:
                calendar = TreatmentCalendar.objects.get(id=request.query_params.get('day_id'))

                # not allow to take medication in a future date
                if calendar.date > timezone.now().date():
                    return Response({"message": "You can't take medication in a future date"}, status=status.HTTP_400_BAD_REQUEST)
                
                calendar.has_taken = not calendar.has_taken
                calendar.save()
                serializer = TreatmentCalendarSerializer(
                    calendar, context={'request': request})
                return Response(serializer.data, status=status.HTTP_200_OK)
            except TreatmentTracker.DoesNotExist:
                return Response({"message": "No treatment calendar found with this id provided"}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['get', 'post', 'patch', 'delete'], url_path='family-disease')
    def family_disease(self, request):
        if request.method == 'POST':
            serializer = FamilyDiseaseSerializer(
                data=request.data, context={'request': request})
            serializer.is_valid(raise_exception=True)
            serializer.save(patient=Patient.objects.get(patient_username=request.user))
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        elif request.method == 'GET':
            if request.query_params.get('disease_id'):
                try:
                    disease = FamilyDisease.objects.get(id=request.query_params.get('disease_id'))
                    serializer = FamilyDiseaseSerializer(
                        disease, context={'request': request})
                    return Response(serializer.data, status=status.HTTP_200_OK)
                except FamilyDisease.DoesNotExist:
                    return Response({"message": "No family disease found with this id provided"}, status=status.HTTP_404_NOT_FOUND)

            diseases = FamilyDisease.objects.filter(patient__patient_username=request.user)
            serializer = FamilyDiseaseSerializer(
                diseases, many=True, context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        elif request.method == 'PATCH':
            if not request.query_params.get('disease_id'):
                return Response({"message": "Please provide an disease id"}, status=status.HTTP_400_BAD_REQUEST)
            try:
                disease = FamilyDisease.objects.get(id=request.query_params.get('disease_id'))
                serializer = FamilyDiseaseSerializer(
                    disease, data=request.data, partial=True, context={'request': request})
                serializer.is_valid(raise_exception=True)
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            except FamilyDisease.DoesNotExist:
                return Response({"message": "No family disease found with this id provided"}, status=status.HTTP_404_NOT_FOUND)

        elif request.method == 'DELETE':
            if not request.query_params.get('disease_id'):
                return Response({"message": "Please provide an disease id"}, status=status.HTTP_400_BAD_REQUEST)
            try:
                disease = FamilyDisease.objects.get(id=request.query_params.get('disease_id'))
                disease.is_active = False
                disease.save()
                return Response({"message": "disease deleted successfully"}, status=status.HTTP_200_OK)
            except FamilyDisease.DoesNotExist:
                return Response({"message": "No disease found with this id provided"}, status=status.HTTP_404_NOT_FOUND)
            
    @action(detail=False, methods=['get'], url_path='general-views')
    def general_health_views(self, request):
        page_views_list: list = ['general_health', 'prescription', 'lab_test', 'recommendation', 'tips']
        choice: str = request.query_params.get('views')

        if not choice:
            return Response({"message": "Please provide a views page name"}, status=status.HTTP_400_BAD_REQUEST)
        elif choice.lower() not in page_views_list:
            return Response({"message": f"Invalid page name. Choose from {page_views_list}"}, status=status.HTTP_400_BAD_REQUEST)

        choice = choice.lower()
        if request.method == 'GET':
            try:
                    patient = Patient.objects.get(patient_username=request.user)
                    
            except Patient.DoesNotExist:
                return Response({"message": "Current user is not a patient"}, status=status.HTTP_200_OK)
                
            if choice == 'general_health':
                
                general_health = GeneralHealgthViewSerialize(
                        patient, context={'request': request})
                return Response(general_health.data, status=status.HTTP_200_OK)
            elif choice == 'prescription':
                prescription_views = PrescriptionViewsSectionSerializer(
                    patient, context={'request': request})
                return Response(prescription_views.data, status=status.HTTP_200_OK)
            
            elif choice == 'lab_test':
                lab_test_views = LabTestsViewsSectionSerializer(
                    patient, context={'request': request})
                return Response(lab_test_views.data, status=status.HTTP_200_OK)
            
            elif choice == 'recommendation':
                recommendation_views = RecommandationViewsSectionSerializer(
                    patient, context={'request': request})
                return Response(recommendation_views.data, status=status.HTTP_200_OK)

            else:
                return Response({"message": "No data found"}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path='get-patient-records')
    def get_patient_records(self, request):
        patient = Patient.objects.get(patient_username=request.user)
        serializer = PatientSerializer(patient, context={'request': request})
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='get-patient-record')
    def get_patient_record(self, request):
        id = request.query_params.get('id')
        try:
            report = PatientReport.objects.get(id=id, is_paid=True)
            serializer = PatientReportSerializer(
                report, context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)
        except PatientReport.DoesNotExist:
            return Response({"message": "No patient report found with this id provided"}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['patch'], url_path='update-report')
    def partial_update_report(self, request):
        id = request.query_params.get('id')
        try:
            report = PatientReport.objects.get(id=id, is_paid=True)
            serializer = PatientReportSerializer(
                report, data=request.data, partial=True, context={'request': request})
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        except PatientReport.DoesNotExist:
            return Response({"message": "No patient report found with this id provided"}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['patch'], url_path='update-dependent-report')
    def partial_update_dependent_report(self, request):
        id = request.query_params.get('id')
        try:
            report = PatientDependentReport.objects.get(id=id, is_paid=True)
            serializer = PatientDependentReportSerializer(
                report, data=request.data, partial=True, context={'request': request})
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        except PatientDependentReport.DoesNotExist:
            return Response({"message": "No patient report found with this id provided"}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['patch', 'put'], url_path='appointment-actions')
    def appointment_actions(self, request):

        if request.method == 'PATCH':
            if not request.query_params.get('appointment_id'):
                return Response({"message": "Please provide an id"}, status=status.HTTP_400_BAD_REQUEST)
            
            if request.data.get('state') and request.data.get('state') not in [Appointement.INPROGRESS, Appointement.COMPLETED]:
                return Response({"message": "appointment can only be in progress or completed state"}, status=status.HTTP_400_BAD_REQUEST)
            try:
                appointment = Appointement.objects.get(
                    id=request.query_params.get('appointment_id'))
                
                if request.data.get('state') == Appointement.INPROGRESS:
                    if appointment.status != Appointement.ACCEPTED:
                        return Response({"message": "appointment should be accepted before consultation starts"}, status=status.HTTP_400_BAD_REQUEST)
                    
                    if not appointment.is_paid:
                        return Response({"message": "appointment should be paid before consultation start"}, status=status.HTTP_400_BAD_REQUEST)                
                
                serializer = UpdateAppointmentSerializer(
                    appointment, data=request.data, context={'request': request}, partial=True)
                
                serializer.is_valid(raise_exception=True)
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            except Appointement.DoesNotExist:
                return Response({"message": "No appointment found with this id provided rr"}, status=status.HTTP_404_NOT_FOUND)

        elif request.method == 'PUT':
            transaction_ref = request.query_params.get('transaction_ref')
            appointment_id = request.query_params.get('appointment_id')
            if not transaction_ref or not appointment_id:
                return Response({"message": "'transaction_ref', 'appointment_id' and 'choice' is required"}, status=status.HTTP_400_BAD_REQUEST)

            # Check if transaction is blacklisted
            blacklisted_transaction = BlackListedTransaction.objects.filter(
                reference_key=transaction_ref)
            
            if blacklisted_transaction.exists():
                return Response({"message": "Invalid Transaction"}, status=status.HTTP_400_BAD_REQUEST)
            
            try:
                appointment: Appointement = Appointement.objects.get(
                        id=appointment_id)
            except Appointement.DoesNotExist:
                return Response({"message": "No appointment found with this id provided"}, status=status.HTTP_404_NOT_FOUND)
            
            if appointment.status != Appointement.ACCEPTED:
                return Response({"message": "appointment should be accepted by doctor before payment"}, status=status.HTTP_400_BAD_REQUEST)

            if appointment.user_concerned == 'me':
                appointment_already_paid = PatientPayment.objects.filter(appointments__id=appointment_id)
            else:
                appointment_already_paid = DependentsPayment.objects.filter(appointments__id=appointment_id)
            if appointment_already_paid.exists():
                return Response({"error": "Invalid Appointment ID or This aapointment has been recorded as paid already"}, status=status.HTTP_400_BAD_REQUEST)

            payment: Payment = Payment()
            response: dict = payment.find_transaction(transaction_ref)

            if response.get("status_code") == status.HTTP_200_OK:
                if response['amount'] <= 0:
                    return Response({"message": "Invalid amount"}, status=status.HTTP_400_BAD_REQUEST)

                if appointment.user_concerned == 'me':

                    consultation = PatientReport.objects.create(
                        patient_username=appointment.patient,
                        consulted_by_doctor=appointment.doctor,
                        consultation_type=appointment.consultation_type,
                        pain_area=appointment.pain_area,
                        is_paid=True,)

                    PatientPayment.objects.get_or_create(
                        consultation=consultation,
                        amount=response['amount'],
                        transaction_ref=transaction_ref,
                        appointments=appointment,
                    )
                else:
                    consultation = PatientDependentReport.objects.create(
                        patient_username=appointment.patient,
                        consulted_by_doctor=appointment.doctor,
                        consultation_type=appointment.consultation_type,
                        pain_area=appointment.pain_area,
                        is_paid=True,)
                    DependentsPayment.objects.create(
                        consultation=consultation,
                        amount=response['amount'],
                        transaction_ref=transaction_ref,
                        appointments=appointment,
                    )
                serializer = AppointmentSerializer(
                    appointment, context={'request': request})
                
                appointment.is_paid = True
                appointment.save()

                # Blacklist transaction to be able to use it only once
                payment.blacklist_transaction(transaction_ref, **response)
                return Response(serializer.data, status=status.HTTP_200_OK)          
            return Response({"message": "No transaction found with this reference provided"}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['post', 'get', 'patch'], url_path='appointment')
    def patient_appointment(self, request):

        if request.method == 'POST':
            serializer = self.get_serializer(
                data=request.data, context={'request': request})
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        elif request.method == 'GET':
            if request.query_params.get('id'):
                try:
                    appointment = Appointement.objects.get(
                        id=request.query_params.get('id'))
                    serializer = self.get_serializer(
                        appointment, context={'request': request})
                    return Response(serializer.data, status=status.HTTP_200_OK)
                except Appointement.DoesNotExist:
                    return Response({"message": "No appointment found with this id provided"}, status=status.HTTP_404_NOT_FOUND)

            patient = Patient.objects.get(patient_username=request.user)
            appointments = Appointement.objects.filter(patient=patient)
            serializer = self.get_serializer(
                appointments, many=True, context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)

        elif request.method == 'PATCH':
            if not request.query_params.get('id'):
                return Response({"message": "Please provide an id"}, status=status.HTTP_400_BAD_REQUEST)
            try:
                appointment = Appointement.objects.get(
                    id=request.query_params.get('id'))
                serializer = self.get_serializer(
                    appointment, data=request.data, partial=True)
                serializer.is_valid(raise_exception=True)
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            except Appointement.DoesNotExist:
                return Response({"message": "No appointment found with this id provided bb"}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['post', 'patch'], url_path='ai-consultation')
    def ai_consultation(self, request):
        choice: str = request.query_params.get('choice')

        dianostic_text = settings.PATIENT_CONSTANTS.messages.DIANOSTIC_TEXT
        prescription_text = settings.PATIENT_CONSTANTS.messages.PRESCRIPTION_TEXT
        recommendation_text = settings.PATIENT_CONSTANTS.messages.RECOMMENDATION_TEXT
        recommended_tests_text = settings.PATIENT_CONSTANTS.messages.RECOMMENDED_TESTS_TEXT
        doctor_ai = settings.PATIENT_CONSTANTS.messages.DOCTOR_AI_NAME

        pain_area = request.data.get('pain_area', 'Unknown')
        dianostic_text += f"Patient's pain area is {pain_area}. \n" if pain_area != 'Unknown' else ''

        patient = Patient.objects.get(patient_username=request.user)
        user, created = User.objects.get_or_create(
            username=doctor_ai, user_type=User.DOCTOR)
        doctor_ai = Doctor.objects.get(user=user)

        if request.method == 'PATCH':
            transaction_ref = request.query_params.get('transaction_ref')
            consultation_id = request.query_params.get('consultation_id')

            if not transaction_ref or not consultation_id:
                return Response({"message": "'transaction_ref', 'consultation_id' is required"}, status=status.HTTP_400_BAD_REQUEST)
            
            # Check if transaction is blacklisted
            blacklisted_transaction = BlackListedTransaction.objects.filter(
                reference_key=transaction_ref)
            
            if blacklisted_transaction.exists():
                return Response({"message": "Invalid Transaction"}, status=status.HTTP_400_BAD_REQUEST)
            
            payment: Payment = Payment()
            response: dict = payment.find_transaction(transaction_ref)
            
            if response.get("status_code") == status.HTTP_200_OK:
                try:
                    consultation = AiConsultationPatient.objects.get(id=consultation_id)
                    consultation.is_paid = True
                    consultation.save()
                    payment.blacklist_transaction(transaction_ref, **response)
                    serializer = AiConsultationPatientSerializer(
                        consultation, context={'request': request})
                    return Response(serializer.data, status=status.HTTP_200_OK)
                except AiConsultationPatient.DoesNotExist:
                    return Response({"message": "No consultation found with this id provided"}, status=status.HTTP_404_NOT_FOUND)

            return Response({"message": "No transaction found with this reference provided"}, status=status.HTTP_404_NOT_FOUND)
        
        elif request.method == 'POST':

            if choice.lower() == 'me':

                if not patient.blood_group == '--':
                    dianostic_text += f"Patient's blood group is {patient.blood_group}. \n"
                if patient.alergies:
                    prescription_text += f"Patient's alergies are {patient.alergies}. \n"

                # patient_result = get_patient_result_from_ai(
                #     dianostic_text+request.data.get('symptoms'))
                # prescription_result = get_patient_result_from_ai(
                #     prescription_text+request.data.get('symptoms'))
                # recommendation_result = get_patient_result_from_ai(
                #     recommendation_text+request.data.get('symptoms'))
                # recommended_tests_result = get_patient_result_from_ai(
                #     recommended_tests_text+request.data.get('symptoms'))

                patient_result = "Test 1, Test 2, Test 3"
                prescription_result = [
                    {'prescription': 'Paracetamol 500mg', 'frequence': 3, 'frequence_type': 'daily', 'duration': 5, 'dosage': 2},
                    {'prescription': 'Omeprazole 20mg', 'frequence': 1, 'frequence_type': 'daily', 'duration': 10, 'dosage': 1},
                    {'prescription': 'Ibuprofen 400mg', 'frequence': 2, 'frequence_type': 'daily', 'duration': 7, 'dosage': 1},
                    {'prescription': 'Oral Rehydration Solution (ORS)', 'frequence': 2, 'frequence_type': 'daily', 'duration': 3, 'dosage': 1},
                ]
                recommendation_result = "Test 1, Test 2, Test 3"
                recommended_tests_result = "Test 1, Test 2, Test 3"

                if patient_result:
                    request.data['diagnosis'] = patient_result
                    request.data['prescription'] = prescription_result
                    request.data['recommendation'] = recommendation_result
                    request.data['recommended_tests'] = recommended_tests_result

                serializer = self.get_serializer(
                    data=request.data, context={'request': request})
                serializer.is_valid(raise_exception=True)
                serializer.save()
                serializer = AiConsultationInfoPatientSerializer(
                    serializer.instance, context={'request': request})
                return Response(serializer.data, status=status.HTTP_201_CREATED)

            elif choice:
                if request.data.get("dependent_blood_group") and request.data.get("dependent_alergies"):
                    dianostic_text += f"Patient's blood group is {request.data.get('dependent_blood_group')} and alergies are {request.data.get('dependent_alergies')}. \n"
                elif request.data.get("dependent_blood_group"):
                    dianostic_text += f"Patient's blood group is {request.data.get('dependent_blood_group')}. \n"
                elif request.data.get("dependent_alergies"):
                    prescription_text += f"Patient's alergies are {request.data.get('dependent_alergies')}. \n"
                if request.data.get("dependent_age"):
                    prescription_text += f"Patient's age is {request.data.get('dependent_age')} years old. \n"

                dependent_result = get_patient_result_from_ai(
                    dianostic_text+request.data.get('dependent_symptoms'))
                dependent_prescription_result = get_patient_result_from_ai(
                    prescription_text+request.data.get('dependent_symptoms'))
                dependent_recommendation_result = get_patient_result_from_ai(
                    recommendation_text+request.data.get('dependent_symptoms'))
                dependent_recommended_tests_result = get_patient_result_from_ai(
                    recommended_tests_text+request.data.get('dependent_symptoms'))

                # dependent_result = "get_patient_result_from_ai(dianostic_text+request.data.get('dependent_symptoms'))"
                # dependent_prescription_result = "et_patient_result_from_ai(prescription_text+request.data.get('dependent_symptoms'))"
                # dependent_recommendation_result = "get_patient_result_from_ai(recommendation_text+request.data.get('dependent_symptoms'))"
                # dependent_recommended_tests_result = "get_patient_result_from_ai(recommended_tests_text+request.data.get('dependent_symptoms'))"

                if dependent_result:
                    request.data['dependent_results'] = dependent_result
                    request.data['dependent_prescription'] = dependent_prescription_result
                    request.data['dependent_recommendation'] = dependent_recommendation_result
                    request.data['dependent_recommended_tests'] = dependent_recommended_tests_result
                else:
                    return Response({'message': settings.PATIENT_CONSTANTS.messages.AI_ERROR_MESSAGE}, status=status.HTTP_400_BAD_REQUEST)
                serializer = PatientDependentReportSerializer(
                    data=request.data, context={'request': request})
                serializer.is_valid(raise_exception=True)
                serializer.save(
                    consulted_by_doctor=doctor_ai,
                    patient_username=Patient.objects.get(patient_username=request.user))
                return Response(
                    {'id': serializer.data['id']}, status=status.HTTP_201_CREATED)

            else:
                return Response({'message': 'Please select a choice'}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'], url_path='paid-result')
    def get_paid_result(self, request):
        id = request.query_params.get('id')
        choice = request.query_params.get('choice')

        if request.method == 'GET':
            if not id or not choice:
                return Response({'message': 'Please provide an id and choice'}, status=status.HTTP_400_BAD_REQUEST)
            try:
                if choice == 'myself':
                    report = PatientReport.objects.get(id=id)
                    report.is_paid = True
                    report.save()
                    serializer = PatientReportSerializer(
                        report, context={'request': request})
                    return Response(serializer.data, status=status.HTTP_200_OK)

                dependent_report = PatientDependentReport.objects.get(id=id)
                dependent_report.is_paid = True
                dependent_report.save()
                serializer = PatientDependentReportSerializer(
                    dependent_report, context={'request': request})
                return Response(serializer.data, status=status.HTTP_200_OK)
            except PatientReport.DoesNotExist:
                return Response({"message": "No patient report found with this id provided"}, status=status.HTTP_404_NOT_FOUND)
            except PatientDependentReport.DoesNotExist:
                return Response({"message": "No patient dependent report found with this id provided"}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['post', 'get', 'patch'], url_path='p-prescription-form')
    def patient_prescription_form(self, request):
        if request.method == 'POST':
            serializer = self.get_serializer(
                data=request.data, context={'request': request})
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        elif request.method == 'GET':
            if request.query_params.get('consultation_id'):

                prescriptions = PatientPrescriptionForm.objects.filter(
                    consultation__id=request.query_params.get('consultation_id'))
                serializer = self.get_serializer(
                    prescriptions, many=True, context={'request': request})
                return Response(serializer.data, status=status.HTTP_200_OK)

            prescriptions = PatientPrescriptionForm.objects.filter(
                consultation__user__patient_username=request.user)
            serializer = self.get_serializer(
                prescriptions, many=True, context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)

        elif request.method == 'PATCH':
            if not request.query_params.get('prescription_id'):
                return Response({"message": "Please provide prescription id: prescription_id"}, status=status.HTTP_400_BAD_REQUEST)
            try:
                prescription = PatientPrescriptionForm.objects.get(
                    id=request.query_params.get('prescription_id'))
                serializer = self.get_serializer(
                    prescription, data=request.data, partial=True)
                serializer.is_valid(raise_exception=True)
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            except PatientPrescriptionForm.DoesNotExist:
                return Response({"message": "No prescription found with this id provided"}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['post', 'get', 'patch'], url_path='d-prescription-form')
    def dependents_prescription_form(self, request):
        if request.method == 'POST':
            serializer = self.get_serializer(
                data=request.data, context={'request': request})
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        elif request.method == 'GET':
            if request.query_params.get('id'):
                try:
                    prescriptions = DependentsPrescriptionForm.objects.get(
                        consultation__id=request.query_params.get('id'))
                    serializer = self.get_serializer(
                        prescriptions, context={'request': request})
                    return Response(serializer.data, status=status.HTTP_200_OK)
                except PatientReport.DoesNotExist:
                    return Response({"message": "No prescription found with this id provided"}, status=status.HTTP_404_NOT_FOUND)

            prescriptions = DependentsPrescriptionForm.objects.filter(
                consultation__patient_username__patient_username=request.user)
            serializer = self.get_serializer(
                prescriptions, many=True, context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)

        elif request.method == 'PATCH':
            if not request.query_params.get('id'):
                return Response({"message": "Please provide prescription id"}, status=status.HTTP_400_BAD_REQUEST)
            try:
                prescription = DependentsPrescriptionForm.objects.get(
                    id=request.query_params.get('id'))
                serializer = self.get_serializer(
                    prescription, data=request.data, partial=True)
                serializer.is_valid(raise_exception=True)
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            except DependentsPrescriptionForm.DoesNotExist:
                return Response({"message": "No prescription found with this id provided"}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['post', 'get', 'patch'], url_path='p-lab-test')
    def patient_lab_test(self, request):
        if request.method == 'POST':
            serializer = self.get_serializer(
                data=request.data, context={'request': request})
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        elif request.method == 'GET':
            if request.query_params.get('consultation_id'):
                lab_tests = PatientLabTest.objects.filter(
                    consultation__id=request.query_params.get('consultation_id'))
                serializer = self.get_serializer(
                    lab_tests, many=True, context={'request': request})
                return Response(serializer.data, status=status.HTTP_200_OK)

            lab_tests = PatientLabTest.objects.filter(
                consultation__user__patient_username__username=request.user)
            serializer = self.get_serializer(
                lab_tests, many=True, context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)

        elif request.method == 'PATCH':
            if not request.query_params.get('lab_test_id'):
                return Response({"message": "Please provide lab test id"}, status=status.HTTP_400_BAD_REQUEST)
            try:
                lab_test = PatientLabTest.objects.get(
                    id=request.query_params.get('lab_test_id'))
                serializer = self.get_serializer(
                    lab_test, data=request.data, partial=True)
                serializer.is_valid(raise_exception=True)
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            except PatientLabTest.DoesNotExist:
                return Response({"message": "No lab test found with this id provided"}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['post', 'get', 'patch'], url_path='d-lab-test')
    def dependents_lab_test(self, request):
        if request.method == 'POST':
            serializer = self.get_serializer(
                data=request.data, context={'request': request})
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        elif request.method == 'GET':
            if request.query_params.get('id'):
                try:
                    lab_tests = DependentsLabTest.objects.get(
                        consultation__id=request.query_params.get('id'))
                    serializer = self.get_serializer(
                        lab_tests, context={'request': request})
                    return Response(serializer.data, status=status.HTTP_200_OK)
                except PatientReport.DoesNotExist:
                    return Response({"message": "No lab test found with this id provided"}, status=status.HTTP_404_NOT_FOUND)

            lab_tests = DependentsLabTest.objects.filter(
                consultation__patient_username__patient_username=request.user)
            serializer = self.get_serializer(
                lab_tests, many=True, context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)

        elif request.method == 'PATCH':
            if not request.query_params.get('id'):
                return Response({"message": "Please provide lab test id"}, status=status.HTTP_400_BAD_REQUEST)
            try:
                lab_test = DependentsLabTest.objects.get(
                    id=request.query_params.get('id'))
                serializer = self.get_serializer(
                    lab_test, data=request.data, partial=True)
                serializer.is_valid(raise_exception=True)
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            except DependentsLabTest.DoesNotExist:
                return Response({"message": "No lab test found with this id provided"}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['post', 'get', 'patch'], url_path='p-recommendation')
    def patient_recommendation(self, request):
        if request.method == 'POST':
            serializer = self.get_serializer(
                data=request.data, context={'request': request})
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        elif request.method == 'GET':
            if request.query_params.get('consultation_id'):
                try:
                    recommendations = PatientRecommendationForm.objects.filter(
                        consultation__id=request.query_params.get('consultation_id'))
                    serializer = self.get_serializer(
                        recommendations, many=True, context={'request': request})
                    return Response(serializer.data, status=status.HTTP_200_OK)
                except PatientReport.DoesNotExist:
                    return Response({"message": "No recommendation found with this id provided"}, status=status.HTTP_404_NOT_FOUND)

            recommendations = PatientRecommendationForm.objects.filter(
                consultation__user__patient_username=request.user)
            serializer = self.get_serializer(
                recommendations, many=True, context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)

        elif request.method == 'PATCH':
            if not request.query_params.get('recommendation_id'):
                return Response({"message": "Please provide recommendation id"}, status=status.HTTP_400_BAD_REQUEST)
            try:
                recommendation = PatientRecommendationForm.objects.get(
                    id=request.query_params.get('recommendation_id'))
                serializer = self.get_serializer(
                    recommendation, data=request.data, partial=True)
                serializer.is_valid(raise_exception=True)
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            except PatientRecommendationForm.DoesNotExist:
                return Response({"message": "No recommendation found with this id provided"}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['post', 'get', 'patch'], url_path='d-recommendation')
    def dependents_recommendation(self, request):
        if request.method == 'POST':
            serializer = self.get_serializer(
                data=request.data, context={'request': request})
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        elif request.method == 'GET':
            if request.query_params.get('id'):
                try:
                    recommendations = DependentsRecommendation.objects.get(
                        consultation__id=request.query_params.get('id'))
                    serializer = self.get_serializer(
                        recommendations, context={'request': request})
                    return Response(serializer.data, status=status.HTTP_200_OK)
                except PatientReport.DoesNotExist:
                    return Response({"message": "No recommendation found with this id provided"}, status=status.HTTP_404_NOT_FOUND)

            recommendations = DependentsRecommendation.objects.filter(
                consultation__patient_username__patient_username=request.user)
            serializer = self.get_serializer(
                recommendations, many=True, context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)

        elif request.method == 'PATCH':
            if not request.query_params.get('id'):
                return Response({"message": "Please provide recommendation id"}, status=status.HTTP_400_BAD_REQUEST)
            try:
                recommendation = DependentsRecommendation.objects.get(
                    id=request.query_params.get('id'))
                serializer = self.get_serializer(
                    recommendation, data=request.data, partial=True)
                serializer.is_valid(raise_exception=True)
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            except DependentsRecommendation.DoesNotExist:
                return Response({"message": "No recommendation found with this id provided"}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['put', 'post'], url_path='payment')
    def patient_payment(self, request):

        if request.method == 'PUT':
            '''
            Check the status of the ongoing transaction
            '''
            # print(request.data)
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            payment_instance = Payment(
                phone_number=serializer.data['phone_number'],
                reference_key=serializer.data['reference_key'],
                kind=serializer.data['kind']
            )
            transaction = payment_instance.check_status()
            # print(len(transaction['transactions']))

            if len(transaction["transactions"]) > 0:
                transaction_status = transaction['transactions'][0]['data']['status']
                # print(transaction_status)
                if transaction_status == 'successful':
                    return Response({
                        'message': 'Payment Successful',
                        'payment_status': transaction_status}, status=status.HTTP_200_OK)
                elif transaction_status == 'failed':
                    return Response({
                        'message': settings.PATIENT_CONSTANTS.messages.PAYMENT_FAILED,
                        'payment_status': transaction_status}, status=status.HTTP_424_FAILED_DEPENDENCY)
                elif transaction_status == 'pending':
                    return Response({
                        'message': 'Payment Pending',
                        'payment_status': transaction_status}, status=status.HTTP_200_OK)
                else:
                    return Response({'message': transaction}, status=status.HTTP_404_NOT_FOUND)

            return Response({'message': transaction}, status=status.HTTP_404_NOT_FOUND)

        if request.method == 'POST':
            '''
            Make payment
            '''
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            payment_instance = Payment(
                phone_number=serializer.data['phone_number'],
                amount=serializer.data['amount']
            )

            payment = payment_instance.pay()

            return Response(payment, status=status.HTTP_200_OK)

    # @action(detail=False, methods=['post'], url_path='correct-symptoms')
    # def correct_symptoms_word(self, request):
    #     word =  request.data.get('word')
    #     if word:
    #         data = check_and_autocorrect_mispelled_word(word)
    #         return Response(data, status=status.HTTP_200_OK)
    #     return Response({'message': 'Please enter a word'}, status=status.HTTP_400_BAD_REQUEST)
