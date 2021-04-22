from rest_framework import viewsets
from rest_framework import permissions
from DBConnect.models import Djangotest
from DBConnect.serializers import DjangotestSerializer
from django.db import connection

from rest_framework.decorators import action
from rest_framework.response import Response


# Create your views here.
class DjangotestViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Djangotest.objects.all()
    serializer_class = DjangotestSerializer

    permission_classes = [permissions.IsAuthenticated]

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
    @action(detail=False, methods=['GET'])
    def search(self, request):
        # books = Book.objects.all()
        try:
            cursor = connection.cursor()
            q = request.query_params.get('q', None)
            strSql = "SELECT userid, userpwd FROM Djangotest where userkey=" +q
            result = cursor.execute(strSql)
            datas = cursor.fetchall()
            print(datas)

            connection.commit()
            connection.close()

        except:
            connection.rollback()
            print("Failed selecting in BookListView")

        return Response(datas)

