from rest_framework import serializers
from settings.models import DiseaseCategorie, BodyPart, Hospital


class DiseaseCategorieSerializer(serializers.ModelSerializer):
    class Meta:
        model = DiseaseCategorie
        fields = '__all__'