from rest_framework import serializers
from .models import Djangotest


class DjangotestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Djangotest
        fields = '__all__'