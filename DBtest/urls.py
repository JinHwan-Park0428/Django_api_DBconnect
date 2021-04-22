from django.contrib import admin
from django.urls import include, path
from rest_framework import routers
from DBConnect import views


router = routers.DefaultRouter()
router.register(r'SkdevsecBag', views.SkdevsecBagViewSet)
router.register(r'SkdevsecBoard', views.SkdevsecBoardViewSet)
router.register(r'SkdevsecComment', views.SkdevsecCommentViewSet)
router.register(r'SkdevsecOrderproduct', views.SkdevsecOrderproductViewSet)
router.register(r'SkdevsecOrderuser', views.SkdevsecOrderuserViewSet)
router.register(r'SkdevsecProduct', views.SkdevsecProductViewSet)
router.register(r'SkdevsecReview', views.SkdevsecReviewViewSet)
router.register(r'SkdevsecUser', views.SkdevsecUserViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(router.urls)),
    path('apt-auth', include('rest_framework.urls', namespace='rest_framework'))
]