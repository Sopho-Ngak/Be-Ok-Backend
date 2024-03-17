from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated

from patients.permissions import IsPatient


from settings.models import DiseaseCategorie, RatingDoctor
from settings.serializers import DiseaseCategorieSerializer, DoctorRatingSerializer, DoctorRatesSerializer

@api_view(['GET'])
@permission_classes([IsAuthenticated,])
def get_disease_groups(request):
    disease_groups = DiseaseCategorie.objects.all()
    serializer = DiseaseCategorieSerializer(disease_groups, many=True, context={'request': request})
    return Response(serializer.data, status=status.HTTP_200_OK)


class RatingViewSets(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    queryset = RatingDoctor.objects.all()
    serializer_class = DoctorRatingSerializer


    def get_serializer_class(self):
        if self.action == 'doctor_rate':
            if self.request.method == 'POST':
                return DoctorRatesSerializer
            return DoctorRatingSerializer
        return super().get_serializer_class()
    
    def get_permissions(self):
        if self.action == 'doctor_rate':
            if self.request.method == 'POST':
                self.permission_classes = (IsAuthenticated, IsPatient)
        return super().get_permissions()

    def get_queryset(self):
        return self.queryset.filter(patient=self.request.user)

    def perform_create(self, serializer):
        serializer.save(patient=self.request.user)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post', 'get'], url_path='doctor-rate')
    def doctor_rate(self, request):

        if self.request.method == 'GET':
            return self.get_ratings(request)
        
        if self.request.method == 'POST':
            serializer = self.get_serializer(data=request.data, context={'request': request})
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
 
    def get_ratings(self, request):
    
        if doctor:= request.query_params.get('doctor_id', None):
            self.queryset = self.queryset.filter(doctor=doctor)

            serializer = DoctorRatingSerializer(self.queryset, many=True, context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)

        if name := request.query_params.get('username', None):
            
            self.queryset = self.queryset.filter(doctor__user__username__icontains=name)
            serializer = DoctorRatingSerializer(self.queryset, many=True, context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)

        serializer = DoctorRatingSerializer(self.queryset, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)


    # @action(detail=False, methods=['get'], url_path='search-by-patient')
    # def get_rating_by_patient(self, request):
    #     if patient:= request.query_params.get('patient', None):
    #         self.queryset = self.queryset.filter(patient=patient)
    #     serializer = DoctorRatingSerializer(self.queryset, many=True)
    #     return Response(serializer.data, status=status.HTTP_200_OK)

    # @action(detail=True, methods=['get'], url_path='rate')
    # def get_rate(self, request, pk=None):
    #     rate = self.queryset.get(pk=pk)
    #     serializer = DoctorRatesSerializer(rate.doctor_rate, many=True)
    #     return Response(serializer.data, status=status.HTTP_200_OK)
