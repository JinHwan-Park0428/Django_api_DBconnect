# 필요한 모듈 임포트
from django.contrib import admin
from django.urls import include, path

# 접근 가능한 url 패턴 목록
urlpatterns = path('', include('DBConnect.urls'))
