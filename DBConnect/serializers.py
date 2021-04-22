from rest_framework import serializers
from .models import *


class SkdevsecBagSerializer(serializers.ModelSerializer):
    class Meta:
        model = SkdevsecBag
        fields = '__all__'

class SkdevsecBoardSerializer(serializers.ModelSerializer):
    class Meta:
        model = SkdevsecBoard
        fields = '__all__'

class SkdevsecCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = SkdevsecComment
        fields = '__all__'

class SkdevsecOrderproductSerializer(serializers.ModelSerializer):
    class Meta:
        model = SkdevsecOrderproduct
        fields = '__all__'

class SkdevsecOrderuserSerializer(serializers.ModelSerializer):
    class Meta:
        model = SkdevsecOrderuser
        fields = '__all__'

class SkdevsecProductBagSerializer(serializers.ModelSerializer):
    class Meta:
        model = SkdevsecProduct
        fields = '__all__'

class SkdevsecReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = SkdevsecReview
        fields = '__all__'

class SkdevsecUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = SkdevsecUser
        fields = '__all__'