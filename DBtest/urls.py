# 필요한 모듈 임포트
from django.contrib import admin
from django.urls import include, path
from rest_framework import routers
from DBConnect import views

# 특정 DB 테이블에 접근 하기 위한 주소 (ex: http://localhost:8080/SkdevsecBag/)
# trailing_slash=False
router = routers.DefaultRouter(trailing_slash=False)
router.register(r'SkdevsecBag', views.SkdevsecBagViewSet)
router.register(r'SkdevsecBoard', views.SkdevsecBoardViewSet)
router.register(r'SkdevsecComment', views.SkdevsecCommentViewSet)
router.register(r'SkdevsecOrderproduct', views.SkdevsecOrderproductViewSet)
router.register(r'SkdevsecOrderuser', views.SkdevsecOrderuserViewSet)
router.register(r'SkdevsecProduct', views.SkdevsecProductViewSet)
router.register(r'SkdevsecReview', views.SkdevsecReviewViewSet)
router.register(r'SkdevsecUser', views.SkdevsecUserViewSet)

# 접근 가능한 url 패턴 목록
urlpatterns = [
    # path('admin/', admin.site.urls),
    path('', include(router.urls)),
    # path('apt-auth', include('rest_framework.urls', namespace='rest_framework'))
]