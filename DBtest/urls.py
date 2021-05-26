# 필요한 모듈 임포트
from django.urls import include, path
from django.conf.urls.static import static
from django.conf import settings
from django.views.static import serve

# 접근 가능한 url 패턴 목록
urlpatterns = [path('', include('DBConnect.urls')),
               path(r'^static/(?P<path>.*)$', serve, {'document_root': settings.STATIC_ROOT}),]

