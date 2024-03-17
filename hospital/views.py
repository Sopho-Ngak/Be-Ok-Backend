# Third party imports
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from hospital.models import Hospital
from hospital.serializers import HospitalSerializer


class HospitalViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    queryset = Hospital.objects.all()
    serializer_class = HospitalSerializer

    @action(detail=False, methods=['get'], url_path='all')
    def get_hospitals(self, request):

        if id:= request.query_params.get('id', None):
            self.queryset = self.queryset.filter(id=id)

        serializer = HospitalSerializer(self.queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'], url_path='search-by-name')
    def get_hospital_by_name(self, request):
        if name:= request.query_params.get('name', None):
            self.queryset = self.queryset.filter(name__icontains=name)
        serializer = HospitalSerializer(self.queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    