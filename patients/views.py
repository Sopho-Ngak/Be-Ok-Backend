# Python imports

# Django imports
from django.shortcuts import render

# Third party imports
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny


# Local imports
from patients.models import Patient
from doctors.models import Doctor
from patients.serializers import (PatientSerializer, PatientReportSerializer, PatientDependentReportSerializer,
                                  PatientPaymentStatusSerializer, PatientCashInSerializer)
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
        if self.action == 'create_patient_result':
            return PatientReportSerializer
        elif self.action == 'get_patient_record':
            return PatientSerializer
        elif self.action == 'patient_payment':
            if self.request.method == 'PUT':
                return PatientPaymentStatusSerializer
            elif self.request.method == 'POST':
                return PatientCashInSerializer
        
        return super().get_serializer_class()

    @action(detail=False, methods=['get'])
    def search(self, request):
        queryset = self.get_queryset()
        serializer = PatientSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'], url_path='get-patient-record')
    def get_patient_record(self, request):
        patient = Patient.objects.get(user=request.user)
        serializer = PatientSerializer(patient)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'], url_path='consult-doctor')
    def create_patient_result(self, request):
        choice = request.GET.get('choice')
        # base_text = "Act as a doctor and give me a diagnosis by recommending me some medications. Make use of paragraph for diagnosis, prescription and recommendation: \n"
        dianostic_text = "Act as a doctor and give me just a possible diagnosis to tell what the patient sick of: \n"
        prescription_text = "Act as a doctor and give me just a possible prescription of medication to take: \n"
        recommendation_text = "Act as a doctor and give me just possible recommendation to follow: \n"
        recommended_tests_text = "Act as a doctor and give me just a possible recommended tests: \n"

        if request.data.get('pain_area'):
                dianostic_text += f"Patient's pain area is {request.data.get('pain_area')}. \n"
        else:
            request.data['pain_area'] = 'Unknown'
      
        try:
            patient = Patient.objects.get(user=request.user)
        except Patient.DoesNotExist:
            raise Response({'error': 'Patient does not exist'}, status=status.HTTP_400_BAD_REQUEST)
        if choice == 'Myself':
            if not request.data.get('symptoms'):
                return Response({'error': 'Please enter your symptoms'}, status=status.HTTP_400_BAD_REQUEST)
            
            # if patient.blood_group and patient.alergies:
            #     base_text += f"Patient's blood group is {patient.blood_group} and alergies are {patient.alergies}. \n"
            if not patient.blood_group == '--':
                dianostic_text += f"Patient's blood group is {patient.blood_group}. \n"
            elif patient.alergies:
                prescription_text += f"Patient's alergies are {patient.alergies}. \n"
            
            patient_result = get_patient_result_from_ai(dianostic_text+request.data.get('symptoms'))
            prescription_result = get_patient_result_from_ai(prescription_text+request.data.get('symptoms'))
            recommendation_result = get_patient_result_from_ai(recommendation_text+request.data.get('symptoms'))
            recommended_tests_result = get_patient_result_from_ai(recommended_tests_text+request.data.get('symptoms'))
            if patient_result:
                request.data['results'] = patient_result
                request.data['prescription'] = prescription_result
                request.data['recommendation'] = recommendation_result
                request.data['recommended_tests'] = recommended_tests_result

                serializer = self.get_serializer(data=request.data, context={'request': request})
                serializer.is_valid(raise_exception=True)
                serializer.save()
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

            dependent_result = get_patient_result_from_ai(dianostic_text+request.data.get('dependent_symptoms'))
            dependent_prescription_result = get_patient_result_from_ai(prescription_text+request.data.get('dependent_symptoms'))
            dependent_recommendation_result = get_patient_result_from_ai(recommendation_text+request.data.get('dependent_symptoms'))
            dependent_recommended_tests_result = get_patient_result_from_ai(recommended_tests_text+request.data.get('dependent_symptoms'))
            if dependent_result:
                request.data['dependent_results'] = dependent_result
                request.data['dependent_prescription'] = dependent_prescription_result
                request.data['dependent_recommendation'] = dependent_recommendation_result
                request.data['dependent_recommended_tests'] = dependent_recommended_tests_result
                serializer = PatientDependentReportSerializer(data=request.data, context={'request': request})
                serializer.is_valid(raise_exception=True)
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response({'message': 'Please select a choice'}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({'message': 'Our doctor is having many requests at the moment.Please try again.'}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['put', 'post'], url_path='payment')
    def patient_payment(self, request):
        payment_instance= Payment()
        if request.method == 'PUT':
            print(request.data)
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            payment_instance.phone_number = serializer.data['phone_number']
            payment_instance.reference_key = serializer.data['reference_key']
            payment_instance.kind = serializer.data['kind']
            transaction = payment_instance.check_status()
            if len(transaction["transactions"])>0:
                transaction_status = transaction['transactions'][0]['data']['status']
                if transaction_status == 'successful':
                    return Response({'message': 'Payment successful'}, status=status.HTTP_200_OK)
                elif transaction_status == 'failed':
                    return Response({'message': 'Payment failed. Make sure you have enough funds in your account and try again'}, status=status.HTTP_424_FAILED_DEPENDENCY)
                elif transaction_status == 'pending':
                    return Response({'message': 'Payment pending'}, status=status.HTTP_102_PROCESSING)
            else:
                return Response({'message': 'Transaction not found'}, status=status.HTTP_404_NOT_FOUND)

        if request.method == 'POST':
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            payment_instance.phone_number = serializer.data['phone_number']
            payment_instance.amount = serializer.data['amount']

            payment = payment_instance.pay()

            return Response(payment, status=status.HTTP_200_OK)
            

            




    


    # @action(detail=False, methods=['post'], url_path='correct-symptoms')
    # def correct_symptoms_word(self, request):
    #     word =  request.data.get('word')
    #     if word:
    #         data = check_and_autocorrect_mispelled_word(word)
    #         return Response(data, status=status.HTTP_200_OK)
    #     return Response({'message': 'Please enter a word'}, status=status.HTTP_400_BAD_REQUEST)

