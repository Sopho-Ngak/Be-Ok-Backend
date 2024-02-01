from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated


from settings.models import DiseaseCategorie, BodyPart, Hospital
from settings.serializers import DiseaseCategorieSerializer

@api_view(['GET'])
@permission_classes([IsAuthenticated,])
def get_disease_groups(request):
    disease_groups = DiseaseCategorie.objects.all()
    serializer = DiseaseCategorieSerializer(disease_groups, many=True, context={'request': request})
    return Response(serializer.data, status=status.HTTP_200_OK)
