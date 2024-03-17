from rest_framework import serializers
from settings.models import DiseaseCategorie, DoctorRate, RatingDoctor
from patients.models import Patient
from patients.serializers import MinumumPatientInfoSerializer
from doctors.serializers import MinimumDoctorInfoSerializer


class DiseaseCategorieSerializer(serializers.ModelSerializer):
    class Meta:
        model = DiseaseCategorie
        fields = '__all__'


class DoctorRatesSerializer(serializers.ModelSerializer):
    patient = serializers.HiddenField(default=serializers.CurrentUserDefault())
    rate = serializers.IntegerField(min_value=1, max_value=5)
    patient_info = serializers.SerializerMethodField()
    class Meta:
        model = DoctorRate
        fields = [
            'id',
            'patient',
            'patient_info',
            'rate',
            'comment',
            'created_at'
        
        ]

    def get_patient_info(self, obj):
        serializer = MinumumPatientInfoSerializer(instance=obj.patient, context=self.context)
        return serializer.data

    def create(self, validated_data):
        try:
            doctor = self.context['request'].data.get('doctor')
            patient = Patient.objects.get(patient_username__id=validated_data['patient'].id)
            instance = DoctorRate.objects.create(patient=patient, rate=validated_data['rate'], comment=validated_data['comment'])
            rate_doctor, _ = RatingDoctor.objects.get_or_create(doctor=doctor)
            rate_doctor.rates.add(instance)
            rate_doctor.save()
            return instance
        except Exception as e:
            raise e

class DoctorRatingSerializer(serializers.ModelSerializer):
    rates_average = serializers.SerializerMethodField()
    raters = serializers.SerializerMethodField()
    doctor_rate_count = serializers.SerializerMethodField()
    doctor_profile = serializers.SerializerMethodField()
    class Meta:
        model = RatingDoctor
        fields = [
            'id',
            'doctor',
            'doctor_profile',
            'doctor_rate_count',
            'rates_average',
            'raters',
            'created_at',
            'updated_at'
        ]

    def get_doctor_profile(self, obj):
        serializer = MinimumDoctorInfoSerializer(obj.doctor, context=self.context)
        return serializer.data
        # return 

    def get_rates_average(self, obj):
        return obj.rates_average
    
    def get_doctor_rate_count(self, obj):
        return obj.doctor_rate_count
    
    def get_raters(self, obj):
        return DoctorRatesSerializer(obj.get_all_rates, many=True, context=self.context).data