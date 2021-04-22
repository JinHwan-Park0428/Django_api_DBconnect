from rest_framework import viewsets
from rest_framework import permissions
from DBConnect.models import Djangotest
from DBConnect.serializers import DjangotestSerializer
from django.db import connection
import requests
import json

from rest_framework.decorators import action
from rest_framework.response import Response


# Create your views here.
class DjangotestViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Djangotest.objects.all()
    serializer_class = DjangotestSerializer

    # 관리자 권한 요구 코드
    # permission_classes = [permissions.IsAuthenticated]

    # sql 인젝션 방어용 코드
    # @action(detail=False, methods=['GET'])
    # def search(self, request):
    #     q = request.query_params.get('q', None)
    #     print("q값 출력:", type(q))
    #
    #     qs = self.get_queryset().filter(userkey=q)
    #     serializer = self.get_serializer(qs, many=True)
    #     # print(serializer.data)
    #
    #     return Response(serializer.data)

    #sql 인젝션 되는 코드
    @action(detail=False, methods=['POST'])
    def search(self, request):
        new_data = dict()
        # books = Book.objects.all()
        try:
            cursor = connection.cursor()
            # q = request.query_params.get('q', None)
            # print(request.data)
            q1 = request.data['userid']
            q2 = request.data['userpwd']
            strSql = "SELECT userid, userpwd FROM Djangotest where userid='" +q1+"'"+" or "+ "userpwd='"+ q2+ "'"
            result = cursor.execute(strSql)
            datas = cursor.fetchall()
            for data in datas:
                new_data['userid'] = data[0]
                new_data['userpwd'] = data[1]


            connection.commit()
            connection.close()

        except Exception as e:
            connection.rollback()
            print(e)

        return Response(new_data)

