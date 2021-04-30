# 필요한 모듈 임포트
from rest_framework import serializers
from .models import *

# 각각의 클래스는 Django Rest API에서 테이블 내용을 출력하기 위한 기본 세팅 상태
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

class SkdevsecProductSerializer(serializers.ModelSerializer):
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