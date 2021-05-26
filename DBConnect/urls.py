# 필요한 모듈 임포트
from django.urls import include, path
from rest_framework import routers
from . import skdevsec_bagview, skdevsec_boardview, skdevsec_userview, skdevsec_reviewview, skdevsec_commentview, \
    skdevsec_productview, skdevsec_orderuserview, skdevsec_orderproductview
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls import url
from django.views.static import serve

# trailing_slash=False
router = routers.SimpleRouter(trailing_slash=False)
router.register(r'SkdevsecBag', skdevsec_bagview.SkdevsecBagViewSet)
router.register(r'SkdevsecBoard', skdevsec_boardview.SkdevsecBoardViewSet)
router.register(r'SkdevsecComment', skdevsec_commentview.SkdevsecCommentViewSet)
router.register(r'SkdevsecOrderproduct', skdevsec_orderproductview.SkdevsecOrderproductViewSet)
router.register(r'SkdevsecOrderuser', skdevsec_orderuserview.SkdevsecOrderuserViewSet)
router.register(r'SkdevsecProduct', skdevsec_productview.SkdevsecProductViewSet)
router.register(r'SkdevsecReview', skdevsec_reviewview.SkdevsecReviewViewSet)
router.register(r'SkdevsecUser', skdevsec_userview.SkdevsecUserViewSet)

# 접근 가능한 url 패턴 목록
urlpatterns = [
    path('', include(router.urls)),
]
#
# urlpatterns += url(r'^static/(?P<path>.\*)$', serve, {
#     'document_root': settings.STATIC_ROOT,
# })

# + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT, insecure=True)
