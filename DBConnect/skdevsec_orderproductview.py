# 필요한 모듈 임포트
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
            # DB 접근할 cursor
            cursor = connection.cursor()

            # POST 메소드로 날라온 Request의 데이터 각각 추출
            oid = int(request.data['oid'])

            # SQL 쿼리문 작성
            sql_query = "SELECT * FROM skdevsec_orderproduct WHERE oid=%s"

            # DB에 명령문 전송
            cursor.execute(sql_query, (oid, ))
            data = cursor.fetchone()

            # 데이터가 있으면
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
            # 데이터가 없으면
            else:
                # DB와 접속 종료
                connection.close()
                # 프론트엔드로 0 전송
                return Response(0)

            # DB와 접속 종료
            connection.close()

        # 에러가 발생했을 경우 백엔드에 에러 내용 출력 및 프론트엔드로 0 전송
        except Exception as e:
            connection.rollback()
            print(f"에러: {e}")
            return Response(0)

        # 성공 했을 시, 프론트엔드에 1 전송
        else:
            return Response(new_data)
