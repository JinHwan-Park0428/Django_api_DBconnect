from rest_framework import viewsets
from rest_framework import permissions
from DBConnect.models import *
from DBConnect.serializers import *
from django.db import connection
from rest_framework.decorators import action
from rest_framework.response import Response


class SkdevsecBagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = SkdevsecBag.objects.all()
    serializer_class = SkdevsecBagSerializer

    # 관리자 권한 요구 코드
    # permission_classes = [permissions.IsAuthenticated]

    # sql 인젝션 방어용 코드
    # @action(detail=False, methods=['GET'])
    # def search(self, request):
    #     q = request.query_params.get('q', None)
    #     print("q값 출력:", type(q))
    #
    #     qs = self.get_queryset().filter(bag_id=q)
    #     serializer = self.get_serializer(qs, many=True)
    #     # print(serializer.data)
    #
    #     return Response(serializer.data)

    # #sql 인젝션 되는 코드
    # @action(detail=False, methods=['POST'])
    # def search(self, request):
    #     new_data = dict()
    #     # books = Book.objects.all()
    #     try:
    #         cursor = connection.cursor()
    #         # q = request.query_params.get('q', None)
    #         # print(request.data)
    #         q1 = request.data['userid']
    #         q2 = request.data['userpwd']
    #         strSql = "SELECT userid, userpwd FROM Djangotest where userid='" +q1+"'"+" or "+ "userpwd='"+ q2+ "'"
    #         result = cursor.execute(strSql)
    #         datas = cursor.fetchall()
    #         for data in datas:
    #             new_data['userid'] = data[0]
    #             new_data['userpwd'] = data[1]
    #
    #
    #         connection.commit()
    #         connection.close()
    #
    #     except Exception as e:
    #         connection.rollback()
    #         print(e)
    #
    #     return Response(new_data)

class SkdevsecBoardViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = SkdevsecBoard.objects.all()
    serializer_class = SkdevsecBoardSerializer

class SkdevsecCommentViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = SkdevsecComment.objects.all()
    serializer_class = SkdevsecCommentSerializer

class SkdevsecOrderproductViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = SkdevsecOrderproduct.objects.all()
    serializer_class = SkdevsecOrderproductSerializer

class SkdevsecOrderuserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = SkdevsecOrderuser.objects.all()
    serializer_class = SkdevsecOrderuserSerializer

class SkdevsecProductViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = SkdevsecProduct.objects.all()
    serializer_class = SkdevsecProductBagSerializer

class SkdevsecReviewViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = SkdevsecReview.objects.all()
    serializer_class = SkdevsecReviewSerializer

class SkdevsecUserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = SkdevsecUser.objects.all()
    serializer_class = SkdevsecUserSerializer

