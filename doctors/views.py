from datetime import datetime
from django.utils import timezone

from django.shortcuts import render
from rest_framework.decorators import permission_classes, api_view
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated


from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Doctor, DoctorDocument, DoctorAvailability, DiseaseGroup, Disease
from doctors.permissions import IsDoctor, IsDoctorAndProfileOwner
from doctors.serializers import (
    DiseaseGroupSerializer, DiseaseSerializer, DoctorDocumentSerializer, DoctorAvailabilitySerializer, DoctorInfoSerializer,
    DoctorSerializer)
from patients.models import Appointement, PatientReport, PatientDependentReport, Patient
from patients.serializers import DoctorAppointmentInfoSerializer, PatientReportSerializer, PatientDependentReportSerializer

@api_view(['GET'])
@permission_classes([IsAuthenticated,])
def get_disease_groups(request):
    disease_groups = DiseaseGroup.objects.all()
    serializer = DiseaseGroupSerializer(disease_groups, many=True, context={'request': request})
    return Response(serializer.data, status=status.HTTP_200_OK)

class DoctorViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsDoctor]
    queryset = Doctor.objects.all()
    serializer_class = DoctorInfoSerializer

    def get_serializer_class(self):
        match self.action:
            case 'doctor_profile':
                match self.request.method:
                    case 'GET':
                        return DoctorInfoSerializer
                    case _:
                        return DoctorSerializer
            case 'doctor_documents':
                return DoctorDocumentSerializer
            
            case 'doctor_availabilities' | 'available_doctors':
                return DoctorAvailabilitySerializer
            case 'doctor_appointments':
                return DoctorAppointmentInfoSerializer
            case 'doctor_consultation':
                match self.request.method:
                    case 'GET' | 'POST' | 'PATCH':
                        match self.request.query_params.get('consult_type'):
                            case 'patient':
                                return PatientReportSerializer
                            case 'dependent':
                                return PatientDependentReportSerializer
            case _:
                return super().get_serializer_class()
    
    def get_permissions(self):
        if self.action == 'doctor_availabilities':
            if self.request.method == 'GET':
                self.permission_classes = [IsAuthenticated, ]
            else:
                self.permission_classes = [IsAuthenticated, IsDoctorAndProfileOwner]
        elif self.action in ['doctor_profile','available_doctors']:
            if self.request.method == 'GET':
                self.permission_classes = [IsAuthenticated, ]
            else:
                self.permission_classes = [IsAuthenticated, IsDoctorAndProfileOwner]
        elif self.action == 'doctor_documents':
            self.permission_classes = [IsAuthenticated, IsDoctorAndProfileOwner]
        elif self.action == 'doctor_appointments':
            self.permission_classes = [IsAuthenticated, IsDoctorAndProfileOwner]
        elif self.action == 'doctor_consultation':
            self.permission_classes = [IsAuthenticated, IsDoctor]
        elif self.action == 'get_all_doctors':
            self.permission_classes = [IsAuthenticated, ]
        return super().get_permissions()
    
    @action(detail=False, methods=['get'], url_path='search-doctor')
    def search_doctor(self, request):
        pass

    @action(detail=False, methods=['get', 'patch'], url_path='profile')
    def doctor_profile(self, request):
        if request.method == 'GET':
            id = request.query_params.get('id')
            if id:
                try:
                    doctor = Doctor.objects.get(id=id)
                    serializer = self.get_serializer(doctor, context={'request': request})
                    return Response(serializer.data, status=status.HTTP_200_OK)
                except Doctor.DoesNotExist:
                    return Response({'message': 'No doctor found with the id provided'}, status=status.HTTP_400_BAD_REQUEST)
                
            doctor = Doctor.objects.get(user=request.user)
            serializer = self.get_serializer(doctor, context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        # Update doctor profile
        elif request.method == 'PATCH':
            doctor = Doctor.objects.get(user=request.user)
            serializer = self.get_serializer(doctor, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get', 'patch'], url_path='doctor-documents')
    def doctor_documents(self, request):
        if request.method == 'GET':
            doctor_instance = Doctor.objects.get(user=request.user)
            document, _ = DoctorDocument.objects.get_or_create(doctor=doctor_instance)
            serializer = self.get_serializer(document)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        elif request.method == 'PATCH':
            doctor_instance = Doctor.objects.get(user=request.user)
            document, _ = DoctorDocument.objects.get_or_create(doctor=doctor_instance)
            serializer = self.get_serializer(document, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get', 'patch'], url_path='appointments')
    def doctor_appointments(self, request):
        if request.method == 'GET':
            id = request.query_params.get('id')
            if id:
                try:
                    appointments = Appointement.objects.filter(id=id, doctor_availability__ending_date__gte=timezone.now(), doctor__user=request.user)
                    serializer = self.get_serializer(appointments, many=True)
                    return Response(serializer.data, status=status.HTTP_200_OK)
                except Appointement.DoesNotExist:
                    return Response({'message': 'No appointment found with the id provided'}, status=status.HTTP_400_BAD_REQUEST)
            appointments = Appointement.objects.filter(doctor__user=request.user, doctor_availability__ending_date__gte=timezone.now())
            serializer = self.get_serializer(appointments, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        elif request.method == 'PATCH':
            id = request.query_params.get('id')
            if not id:
                return Response({'message': 'Please provide appointment id'}, status=status.HTTP_400_BAD_REQUEST)
            
            try:
                appointment = Appointement.objects.get(id=id)
                appointment.is_confirmed = True
                appointment.save()
                serializer = self.get_serializer(appointment)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except Appointement.DoesNotExist:
                return Response({'message': 'No appointment found with the id provided'}, status=status.HTTP_400_BAD_REQUEST)
            
    @action(detail=False, methods=['get', 'post', 'patch'], url_path='consultation')
    def doctor_consultation(self, request):
        if request.method == 'GET':
            consult_id = request.query_params.get('consult_id')
            consult_type = request.query_params.get('consult_type')

            if consult_id:            
                if consult_type not in ['patient', 'dependent']:
                    return Response({'message': 'Please provide correct consultation type'}, status=status.HTTP_400_BAD_REQUEST)
            
                try:
                    if consult_type == 'patient':
                        consultation = PatientReport.objects.get(id=consult_id)
                        serializer = self.get_serializer(consultation)
                        return Response(serializer.data, status=status.HTTP_200_OK)
                    elif consult_type == 'dependent':
                        consultation = PatientDependentReport.objects.get(id=consult_id)
                        serializer = self.get_serializer(consultation)
                        return Response(serializer.data, status=status.HTTP_200_OK)
                except PatientReport.DoesNotExist:
                    return Response({'message': 'No consultation found with the id provided'}, status=status.HTTP_400_BAD_REQUEST)
                except PatientDependentReport.DoesNotExist:
                    return Response({'message': 'No consultation found with the id provided'}, status=status.HTTP_400_BAD_REQUEST)
                
            patient_consulted_by = PatientReport.objects.filter(consulted_by_doctor__user=request.user)
            dependent_consulted_by = PatientDependentReport.objects.filter(consulted_by_doctor__user=request.user)
            patien_serializer = PatientReportSerializer(patient_consulted_by, many=True, context={'request': request})
            dependent_serializer = PatientDependentReportSerializer(dependent_consulted_by, many=True, context={'request': request})
            
            return Response(
                {
                    'patient': patien_serializer.data, 
                    'dependent': dependent_serializer.data
                }, 
                status=status.HTTP_200_OK
                )
        
        elif request.method == 'POST':
            '''
            Doctor making consultation
            '''
            if not request.query_params.get('consult_type'):
                return Response({'message': 'Please provide consultation type'}, status=status.HTTP_400_BAD_REQUEST)
            
            try:
                # if request.query_params.get('consult_type') == 'patient':
                patient = Patient.objects.get(id=request.data.get('patient_username'))
                # elif request.query_params.get('consult_type') == 'dependent':
                #     patient = Patient.objects.get(id=request.data.get('dependent'))
            except Patient.DoesNotExist:
                return Response({'message': 'No patient found with the id provided'}, status=status.HTTP_400_BAD_REQUEST)
            
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save(consulted_by_doctor=Doctor.objects.get(user=request.user), patient_username=patient)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        elif request.method == 'PATCH':
            '''
            Doctor updating consultation
            '''
            consult_id = request.query_params.get('consult_id')
            consult_type = request.query_params.get('consult_type')

            if consult_type not in ['patient', 'dependent']:
                return Response({'message': 'Please provide correct consultation type'}, status=status.HTTP_400_BAD_REQUEST)
            
            if not consult_id:
                return Response({'message': 'Please provide consultation id'}, status=status.HTTP_400_BAD_REQUEST)

            try:
                if consult_type == 'patient':
                    consultation = PatientReport.objects.get(id=consult_id)
                    serializer = self.get_serializer(consultation, data=request.data, partial=True)
                    serializer.is_valid(raise_exception=True)
                    serializer.save(consulted_by_doctor=Doctor.objects.get(user=request.user))
                    return Response(serializer.data, status=status.HTTP_200_OK)
                elif consult_type == 'dependent':
                    consultation = PatientDependentReport.objects.get(id=consult_id)
                    serializer = self.get_serializer(consultation, data=request.data, partial=True)
                    serializer.is_valid(raise_exception=True)
                    serializer.save()
                    return Response(serializer.data, status=status.HTTP_200_OK)
            except PatientReport.DoesNotExist:
                return Response({'message': 'No consultation found with the id provided'}, status=status.HTTP_400_BAD_REQUEST)
            except PatientDependentReport.DoesNotExist:
                return Response({'message': 'No consultation found with the id provided'}, status=status.HTTP_400_BAD_REQUEST)


        
    @action(detail=False, methods=['patch', 'post', 'get'], url_path='availabilities')
    def doctor_availabilities(self, request):
        if request.method == 'GET':
            id = request.query_params.get('id')
            doctor = request.query_params.get('doctor')
            if id:
                try:
                    availability = DoctorAvailability.objects.get(id=id, is_booked=False, ending_date__gte=timezone.now())
                    serializer = self.get_serializer(availability)
                    return Response(serializer.data, status=status.HTTP_200_OK)
                except DoctorAvailability.DoesNotExist:
                    return Response({'message': 'No availability found with the id provided. It\'s eigther booked or not exist'}, status=status.HTTP_400_BAD_REQUEST)
                
            elif doctor:
                try:
                    doctor = Doctor.objects.get(id=doctor)
                    availabilities = DoctorAvailability.objects.filter(doctor=doctor, is_booked=False, ending_date__gte=timezone.now())
                    serializer = self.get_serializer(availabilities, many=True)
                    return Response(serializer.data, status=status.HTTP_200_OK)
                except Doctor.DoesNotExist:
                    return Response({'message': 'No doctor found with the id provided'}, status=status.HTTP_400_BAD_REQUEST)
        
            doctor = Doctor.objects.get(user=request.user)
            availabilities = DoctorAvailability.objects.filter(doctor=doctor, is_booked=False, ending_date__gte=timezone.now())
            serializer = self.get_serializer(availabilities)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        elif request.method == 'POST':
            doctor = Doctor.objects.get(user=request.user)
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save(doctor=doctor)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        elif request.method == 'PATCH':
            id = request.query_params.get('id')
            if not id:
                return Response({'message': 'Please provide availability id'}, status=status.HTTP_400_BAD_REQUEST)
            try:
                availability = DoctorAvailability.objects.get(id=id)
                serializer = self.get_serializer(availability, data=request.data, partial=True)
                serializer.is_valid(raise_exception=True)
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            except DoctorAvailability.DoesNotExist:
                return Response({'message': 'No availability found with the id provided'}, status=status.HTTP_400_BAD_REQUEST)
            
    @action(detail=False, methods=['get'], url_path='available-doctors')
    def available_doctors(self, request):
        '''
        Get all available doctors
        '''
        availabilities = DoctorAvailability.objects.filter(is_booked=False, ending_date__gte=timezone.now())
        serializer = self.get_serializer(availabilities, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)