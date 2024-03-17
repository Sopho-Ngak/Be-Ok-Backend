from rest_framework import serializers

from hospital.models import Hospital, Service, Galery, OpeningHours


class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = [
            'id',
            'name',
            'created_at',
            'updated_at'        
        ]


class GalerySerializer(serializers.ModelSerializer):
    class Meta:
        model = Galery
        fields = [
            'id',
            'image',
            'created_at',
            'updated_at'
        ]


class OpeningHoursSerializer(serializers.ModelSerializer):
    class Meta:
        model = OpeningHours
        fields = [
            'id',
            'day',
            'open_time',
            'close_time',
            'closed',
            'created_at',
            'updated_at'
        ]


class HospitalSerializer(serializers.ModelSerializer):
    services = ServiceSerializer(many=True, read_only=True, source='hospital_services')
    galeries = GalerySerializer(many=True, read_only=True, source='hospital_galery')
    opening_hours = OpeningHoursSerializer(many=True, read_only=True, source='hospital_opening_hour')

    class Meta:
        model = Hospital
        fields = [
            'id',
            'type',
            'name',
            'address',
            'main_photo',
            'city',
            'state',
            'country',
            'phone',
            'email',
            'website',
            'created_at',
            'updated_at',
            'services',
            'galeries',
            'opening_hours' 
        ]