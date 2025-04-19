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

        # get id and filter the queryset
        if id:= request.query_params.get('id', None):
            self.queryset = self.queryset.filter(id=id)

            if not self.queryset.exists():
                return Response({
                    "errorMessage": "Hospital not found with the given id",
                    "status_code": status.HTTP_404_NOT_FOUND,
                }, status=status.HTTP_404_NOT_FOUND)

        serializer = HospitalSerializer(self.queryset, many=True)
        return Response({
            "successMessage": "Hospitals fetched successfully",
            "status_code": status.HTTP_200_OK,
            "data":serializer.data}, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'], url_path='search-by-name')
    def get_hospital_by_name(self, request):
        if not request.query_params.get("name"):
            return Response({
                "errorMessage": "Provide a hospital name to search",
                "status_code": status.HTTP_400_BAD_REQUEST,
            }, status=status.HTTP_400_BAD_REQUEST)
        
        name= request.query_params.get('name', None)
        self.queryset = self.queryset.filter(name__icontains=name)
        if not self.queryset.exists():
            return Response({
                "errorMessage": "Hospital not found with the given name",
                "status_code": status.HTTP_404_NOT_FOUND,
            }, status=status.HTTP_404_NOT_FOUND)
        
        serializer = HospitalSerializer(self.queryset, many=True)
        return Response({
            "successMessage": "Hospitals fetched successfully",
            "status_code": status.HTTP_200_OK,
            "date":serializer.data
            }, status=status.HTTP_200_OK)
    