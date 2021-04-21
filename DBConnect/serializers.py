from rest_framework import serializers
from .models import djangotest


class djangotestSerializer(serializers.ModelSerializer):
    class Meta:
        model = djangotest
        fields = '__all__'