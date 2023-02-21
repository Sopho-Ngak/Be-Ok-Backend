# Python imports

# Django imports
from django.shortcuts import render

# Third party imports
import enchant
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny


# Local imports
from patients.models import Patient
from patients.serializers import PatientSerializer
from utils.ai_call import get_patient_result_from_ai
from utils.check_mispelled_word import check_and_autocorrect_mispelled_word


class PatientViewSet(viewsets.ModelViewSet):
    queryset = Patient.objects.all().order_by('user__username')
    serializer_class = PatientSerializer

    # def get_queryset(self):
    #     if self.request.GET.get('name'):
    #         return Patient.objects.filter(name__icontains=self.request.Get.get('name'))
    #     return self.queryset

    def get_permissions(self):
        return [AllowAny()]

    def get_serializer_class(self):
        if self.action == 'create_patient_result':
            return PatientSerializer
        return super().get_serializer_class()

    @action(detail=False, methods=['get'])
    def search(self, request):
        queryset = self.get_queryset()
        serializer = PatientSerializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'], url_path='consult-doctor')
    def create_patient_result(self, request):
        base_text = "Act as a doctor and give me a diagnosis by recommending me some medications. Make use of paragraph for diagnosis, prescription and recommendation: \n"
        patient_result = get_patient_result_from_ai(base_text+request.data['symptoms'])
        print("#######################################\n\n", patient_result, "\n\n#######################################")
        if patient_result:
            request.data['results'] = patient_result
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
        return Response({'message': 'Our doctor is having many requests at the moment.Please try again.'})

    @action(detail=False, methods=['post'], url_path='correct-symptoms')
    def correct_symptoms_word(self, request):
        word =  request.data.get('word')
        if word:
            data = check_and_autocorrect_mispelled_word(word)
            return Response(data, status=status.HTTP_200_OK)

