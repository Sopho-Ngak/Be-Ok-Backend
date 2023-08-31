from django.shortcuts import render
from rest_framework.decorators import permission_classes, api_view
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated


from rest_framework import viewsets, status
from rest_framework.response import Response

from .models import Doctor, DoctorDocument, DoctorAvailability, DiseaseGroup, Disease
from doctors.serializers import DiseaseGroupSerializer, DiseaseSerializer

@api_view(['GET'])
@permission_classes([IsAuthenticated,])
def get_disease_groups(request):
    disease_groups = DiseaseGroup.objects.all()
    serializer = DiseaseGroupSerializer(disease_groups, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)