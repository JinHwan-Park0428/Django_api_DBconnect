from django.db import connection
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from DBConnect.serializers import *


# 결제 내역 테이블
class SkdevsecOrderproductViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = SkdevsecOrderproduct.objects.all()
    serializer_class = SkdevsecOrderproductSerializer

    # 결제 내역 출력
    @action(detail=False, methods=['POST'])
    def pay_result_output(self, request):
        new_data = list()
        try:
            cursor = connection.cursor()

            oid = int(request.data['oid'])

            sql_query = "SELECT * FROM skdevsec_orderproduct WHERE oid=%s"
            cursor.execute(sql_query, (oid, ))
            data = cursor.fetchone()

            if data is not None:
                while data:
                    new_data_in = dict()
                    new_data_in['opid'] = data[0]
                    new_data_in['pname'] = data[2]
                    new_data_in['pcate'] = data[3]
                    new_data_in['pprice'] = data[4]
                    new_data_in['pcount'] = data[5]
                    new_data.append(new_data_in)

                    data = cursor.fetchone()
            else:
                connection.close()
                return Response(0)

            connection.close()

        except Exception as e:
            connection.rollback()
            print(f"에러: {e}")
            return Response(0)

        else:
            return Response(new_data)
