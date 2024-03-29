# Python imports

# Django imports
from django.conf import settings

# Third party imports
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny


# Local imports
from patients.models import Patient, PatientReport, PatientDependentReport, Appointement
from doctors.models import Doctor, DoctorAvailability
from accounts.models import User
from accounts.serializers import UserInfoSerializer
from patients.permissions import IsPatient, IsDoctorOrPatient
from patients.serializers import (PatientSerializer, PatientInfoSerializer, PatientEditProfileSerializer, PatientReportSerializer, PatientDependentReportSerializer,
                                  PatientPaymentStatusSerializer, PatientCashInSerializer, AppointmentSerializer)
from doctors.serializers import (
    DoctorInfoSerializer)
from utils.ai_call import get_patient_result_from_ai
from utils.payment_module import Payment
#from utils.check_mispelled_word import check_and_autocorrect_mispelled_word


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
            return PatientReportSerializer
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
        
        return super().get_serializer_class()
    
    def get_permissions(self):
        if self.action == 'ai_consultation':
            self.permission_classes = [IsAuthenticated, IsPatient]
        elif self.action == 'get_patient_record':
            self.permission_classes = [IsAuthenticated, IsDoctorOrPatient]
        elif self.action == 'patient_appointment':
            self.permission_classes = [IsAuthenticated, IsPatient]
        # elif self.action == 'get_paid_result':
        #     self.permission_classes = [IsAuthenticated, IsPatient]
        return super().get_permissions()
        

    @action(detail=False, methods=['get'])
    def search(self, request):
        queryset = self.get_queryset()
        serializer = PatientSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'], url_path='doctors')
    def get_all_doctors(self, request):
        if request.method == 'GET':
            doctors = Doctor.objects.filter(doctor_documents__is_approved=True)
            serializer = DoctorInfoSerializer(doctors, many=True, context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get', 'patch'], url_path='profile')
    def patient_profile(self, request):
        if request.method == "GET":
            try:
                instance = Patient.objects.get(patient_username=request.user)
                serializer = self.get_serializer(instance, context={'request': request})
                return Response(serializer.data, status=status.HTTP_200_OK)
            except Patient.DoesNotExist:
                return Response({"message": "No patient found"}, status=status.HTTP_200_OK)
            
        elif request.method == "PATCH":
            try:
                instance = Patient.objects.get(patient_username=request.user)
                serializer = self.get_serializer(
                    instance, data=request.data, partial=True, context={'request': request})
                serializer.is_valid(raise_exception=True)
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            except Patient.DoesNotExist:
                return Response(
                    {"message": settings.PATIENT_CONSTANTS.messages.PATIENT_DOES_NOT_EXIS},
                    status=status.HTTP_404_NOT_FOUND
                )
    
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
            serializer = PatientReportSerializer(report, context={'request': request})
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

    @action(detail=False, methods=['post', 'get', 'patch'], url_path='appointment')
    def patient_appointment(self, request):

        if request.method == 'POST':
            serializer = self.get_serializer(data=request.data, context={'request': request})
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        elif request.method == 'GET':
            if request.query_params.get('id'):
                try:
                    appointment = Appointement.objects.get(id=request.query_params.get('id'))
                    serializer = self.get_serializer(appointment, context={'request': request})
                    return Response(serializer.data, status=status.HTTP_200_OK)
                except Appointement.DoesNotExist:
                    return Response({"message": "No appointment found with this id provided"}, status=status.HTTP_404_NOT_FOUND)
            
            patient = Patient.objects.get(patient_username=request.user)
            appointments = Appointement.objects.filter(patient=patient)
            serializer = self.get_serializer(appointments, many=True, context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        elif request.method == 'PATCH':
            if not request.query_params.get('id'):
                return Response({"message": "Please provide an id"}, status=status.HTTP_400_BAD_REQUEST)
            try:
                appointment = Appointement.objects.get(id=request.query_params.get('id'))
                serializer = self.get_serializer(appointment, data=request.data, partial=True)
                serializer.is_valid(raise_exception=True)
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            except Appointement.DoesNotExist:
                return Response({"message": "No appointment found with this id provided"}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=False, methods=['post'], url_path='ai-consultation')
    def ai_consultation(self, request):
        choice = request.query_params.get('choice')
 
        dianostic_text = settings.PATIENT_CONSTANTS.messages.DIANOSTIC_TEXT
        prescription_text = settings.PATIENT_CONSTANTS.messages.PRESCRIPTION_TEXT
        recommendation_text = settings.PATIENT_CONSTANTS.messages.RECOMMENDATION_TEXT
        recommended_tests_text = settings.PATIENT_CONSTANTS.messages.RECOMMENDED_TESTS_TEXT

        if request.data.get('pain_area'):
                dianostic_text += f"Patient's pain area is {request.data.get('pain_area')}. \n"
        else:
            request.data['pain_area'] = 'Unknown'

        patient = Patient.objects.get(patient_username=request.user)
        doctor, created = User.objects.get_or_create(username="Dr Emile", user_type=User.DOCTOR)
        consultated_by = Doctor.objects.get(user=doctor)
      
        if choice.lower() == 'myself':

            if not patient.blood_group == '--':
                dianostic_text += f"Patient's blood group is {patient.blood_group}. \n"
            elif patient.alergies:
                prescription_text += f"Patient's alergies are {patient.alergies}. \n"
            
            patient_result = get_patient_result_from_ai(dianostic_text+request.data.get('symptoms'))
            prescription_result = get_patient_result_from_ai(prescription_text+request.data.get('symptoms'))
            recommendation_result = get_patient_result_from_ai(recommendation_text+request.data.get('symptoms'))
            recommended_tests_result = get_patient_result_from_ai(recommended_tests_text+request.data.get('symptoms'))
           
            # patient_result = "Test 1, Test 2, Test 3"
            # prescription_result = "Test 1, Test 2, Test 3"
            # recommendation_result = "Test 1, Test 2, Test 3"
            # recommended_tests_result = "Test 1, Test 2, Test 3"

            if patient_result:
                request.data['results'] = patient_result
                request.data['prescription'] = prescription_result
                request.data['recommendation'] = recommendation_result
                request.data['recommended_tests'] = recommended_tests_result

            serializer = self.get_serializer(data=request.data, context={'request': request})
            serializer.is_valid(raise_exception=True)
            serializer.save(
                consulted_by_doctor=consultated_by,
                patient_username=Patient.objects.get(patient_username=request.user))
            return Response({'id':serializer.data['id']}, status=status.HTTP_201_CREATED)
            
        elif choice:
            if request.data.get("dependent_blood_group") and request.data.get("dependent_alergies"):
                dianostic_text += f"Patient's blood group is {request.data.get('dependent_blood_group')} and alergies are {request.data.get('dependent_alergies')}. \n"
            elif request.data.get("dependent_blood_group"):
                dianostic_text += f"Patient's blood group is {request.data.get('dependent_blood_group')}. \n"
            elif request.data.get("dependent_alergies"):
                prescription_text += f"Patient's alergies are {request.data.get('dependent_alergies')}. \n"
            if request.data.get("dependent_age"):
                prescription_text += f"Patient's age is {request.data.get('dependent_age')} years old. \n"

            dependent_result = get_patient_result_from_ai(dianostic_text+request.data.get('dependent_symptoms'))
            dependent_prescription_result = get_patient_result_from_ai(prescription_text+request.data.get('dependent_symptoms'))
            dependent_recommendation_result = get_patient_result_from_ai(recommendation_text+request.data.get('dependent_symptoms'))
            dependent_recommended_tests_result = get_patient_result_from_ai(recommended_tests_text+request.data.get('dependent_symptoms'))
            
            
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
            serializer = PatientDependentReportSerializer(data=request.data, context={'request': request})
            serializer.is_valid(raise_exception=True)
            serializer.save(
                consulted_by_doctor=consultated_by,
                patient_username=Patient.objects.get(patient_username=request.user))
            return Response(
                {'id': serializer.data['id'] }, status=status.HTTP_201_CREATED)
            
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
                    serializer = PatientReportSerializer(report, context={'request': request})
                    return Response(serializer.data, status=status.HTTP_200_OK)
                
                dependent_report = PatientDependentReport.objects.get(id=id)
                dependent_report.is_paid = True
                dependent_report.save()
                serializer = PatientDependentReportSerializer(dependent_report, context={'request': request})
                return Response(serializer.data, status=status.HTTP_200_OK)
            except PatientReport.DoesNotExist:
                return Response({"message": "No patient report found with this id provided"}, status=status.HTTP_404_NOT_FOUND)
            except PatientDependentReport.DoesNotExist:
                return Response({"message": "No patient dependent report found with this id provided"}, status=status.HTTP_404_NOT_FOUND)
            
    # def get_paid_result(self, request):
    #     id = request.query_params.get('id')
    #     choice = request.query_params.get('choice')
    #     print("#############",id, choice)
    #     if request.method == 'GET':
    #         if not id or not choice:
    #             return Response({'message': 'Please provide an id and choice'}, status=status.HTTP_400_BAD_REQUEST)
    #         try:
    #             if choice == 'myself':
    #                 report = PatientReport.objects.get(id=id)
    #                 report.is_paid = True
    #                 report.save()
    #                 serializer = PatientReportSerializer(report, context={'request': request})
    #                 return Response(serializer.data, status=status.HTTP_200_OK)
                
    #             dependent_report = PatientDependentReport.objects.get(id=id)
    #             dependent_report.is_paid = True
    #             dependent_report.save()
    #             serializer = PatientDependentReportSerializer(dependent_report, context={'request': request})
    #             return Response(serializer.data, status=status.HTTP_200_OK)
    #         except PatientReport.DoesNotExist:
    #             return Response({"message": "No patient report found with this id provided"}, status=status.HTTP_404_NOT_FOUND)
    #         except PatientDependentReport.DoesNotExist:
    #             return Response({"message": "No patient dependent report found with this id provided"}, status=status.HTTP_404_NOT_FOUND)
            
    
    @action(detail=False, methods=['put', 'post'], url_path='payment')
    def patient_payment(self, request):

        if request.method == 'PUT':
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

