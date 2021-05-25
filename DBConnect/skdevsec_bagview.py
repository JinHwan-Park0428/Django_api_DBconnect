# 필요한 모듈 임포트
from django.db import connection
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from DBConnect.serializers import *


# 장바구니 테이블
class SkdevsecBagViewSet(viewsets.ReadOnlyModelViewSet):
    # 테이블 출력을 위한 최소 코드
    queryset = SkdevsecBag.objects.all()
    serializer_class = SkdevsecBagSerializer

    # 장바구니 목록 출력
    @action(detail=False, methods=['POST'])
    def bag_show(self, request):
        # 데이터를 저장하기 위한 리스트 선언
        new_data = list()
        try:
            # DB 접근할 cursor
            cursor = connection.cursor()

            # POST 메소드로 날라온 Request의 데이터 각각 추출
            unickname = request.data['unickname']

            # SQL 쿼리문 작성
            sql_query_1 = "SELECT * FROM skdevsec_user WHERE unickname=%s"

            # DB에 명령문 전송
            cursor.execute(sql_query_1, (unickname, ))
            uid = cursor.fetchone()

            if uid is not None:
                # SQL 쿼리문 작성
                sql_query_2 = "SELECT * FROM skdevsec_bag where uid=%s"

                # DB에 명령문 전송
                cursor.execute(sql_query_2, (uid[0], ))
                data = cursor.fetchone()

            else:
                return Response(0)

            # 장바구니 목록이 있으면
            if data is not None:
                # 장바구니 갯수만큼 반복
                while data:
                    new_data_in = dict()
                    # SQL 쿼리문 작성
                    sql_query_3 = "SELECT * FROM skdevsec_product WHERE pid=%s"
                    # DB에 명령문 전송
                    cursor.execute(sql_query_3, (int(data[2]), ))
                    products = cursor.fetchone()
                    # 상품이 있으면
                    if products is not None:
                        new_data_in['bag_id'] = data[0]
                        new_data_in['pid'] = data[1]
                        new_data_in['pname'] = products[1]
                        new_data_in['pcate'] = products[2]
                        new_data_in['pimage'] = products[3]
                        new_data_in['ptext'] = products[4]
                        new_data_in['pprice'] = products[5]
                        new_data_in['bcount'] = data[3]
                        new_data.append(new_data_in)
                    # 상품이 없으면
                    else:
                        # DB와 접속 종료
                        connection.close()
                        return Response(0)

                    data = cursor.fetchone()
            # 장바구니 목록이 없으면 0 전송
            else:
                # DB와 접속 종료
                connection.close()
                return Response(0)

            # DB와 접속 종료
            connection.close()

        # 에러가 발생했을 경우 백엔드에 에러 내용 출력 및 프론트엔드에 0 전송
        except Exception as e:
            connection.rollback()
            print(f"에러: {e}")
            return Response(0)

        # 성공 했을 시, 프론트엔드에 데이터 전송
        else:
            return Response(new_data)

    # 장바구니 목록 삭제
    @action(detail=False, methods=['POST'])
    def bag_delete(self, request):
        try:
            # DB 접근할 cursor
            cursor = connection.cursor()

            # POST 메소드로 날라온 Request의 데이터 각각 추출
            bag_id = int(request.data['bag_id'])

            # SQL 쿼리문 작성
            sql_query = "DELETE FROM skdevsec_bag WHERE bag_id=%s"

            # DB에 명령문 전송
            cursor.execute(sql_query, (bag_id, ))

            # DB와 접속 종료
            connection.commit()
            connection.close()

        # 에러가 발생했을 경우 백엔드에 에러 내용 출력 및 프론트엔드에 0 전송
        except Exception as e:
            connection.rollback()
            print(f"에러: {e}")
            return Response(0)

        # 성공 했을 시, 프론트엔드에 1 전송
        else:
            return Response(1)

    # 장바구니 등록
    @action(detail=False, methods=['POST'])
    def bag_add(self, request):
        try:
            # DB 접근할 cursor
            cursor = connection.cursor()

            # POST 메소드로 날라온 Request의 데이터 각각 추출
            unickname = request.data['unickname']
            pid = int(request.data['pid'])
            bcount = int(request.data['bcount'])

            # SQL 쿼리문 작성
            sql_query_1 = "SELECT * FROM skdevsec_user WHERE unickname=%s"

            # DB에 명령문 전송
            cursor.execute(sql_query_1, (unickname, ))
            uid = cursor.fetchone()

            if uid is not None:
                # SQL 쿼리문 작성
                sql_query_2 = "SELECT * FROM skdevsec_bag WHERE uid=%s AND pid=%s"

                # DB에 명령문 전송
                cursor.execute(sql_query_2, (uid[0], pid,))
                data = cursor.fetchone()
            else:
                return Response(0)

            # 장바구니에 상품이 있으면
            if data is not None:
                # SQL 쿼리문 작성
                sql_query_3 = "UPDATE skdevsec_bag SET bcount=bcount+%s WHERE pid=%s AND uid=%s"
                # DB에 명령문 전송
                cursor.execute(sql_query_3, (bcount, pid, uid[0]))
            else:
                # SQL 쿼리문 작성
                sql_query_3 = "INSERT INTO skdevsec_bag(uid, pid, bcount) VALUES(%s, %s, %s)"
                # DB에 명령문 전송
                cursor.execute(sql_query_3, (uid[0], pid, bcount))

            # DB와 접속 종료
            connection.commit()
            connection.close()

        # 에러가 발생했을 경우 백엔드에 에러 내용 출력 및 프론트엔드에 0 전송
        except Exception as e:
            connection.rollback()
            print(f"에러: {e}")
            return Response(0)

        # 성공 했을 시, 프론트엔드에 1 전송
        else:
            return Response(1)

    # 장바구니 갯수
    @action(detail=False, methods=['POST'])
    def bag_count(self, request):
        # 데이터를 저장하기 위한 리스트 선언
        try:
            # DB 접근할 cursor
            cursor = connection.cursor()

            # POST 메소드로 날라온 Request의 데이터 각각 추출
            unickname = request.data['unickname']

            # SQL 쿼리문 작성
            sql_query_1 = "SELECT * FROM skdevsec_user WHERE unickname=%s"

            # DB에 명령문 전송
            cursor.execute(sql_query_1, (unickname, ))
            uid = cursor.fetchone()

            if uid is not None:
                # SQL 쿼리문 작성
                sql_query_2 = "SELECT COUNT(*) FROM skdevsec_bag where uid=%s"

                # DB에 명령문 전송
                cursor.execute(sql_query_2, (uid[0], ))
                count = cursor.fetchone()
            else:
                return Response(0)

            # DB와 접속 종료
            connection.close()

        # 에러가 발생했을 경우 백엔드에 에러 내용 출력 및 프론트엔드에 0 전송
        except Exception as e:
            connection.rollback()
            print(f"에러: {e}")
            return Response(0)

        # 성공 했을 시, 프론트엔드에 데이터 전송
        else:
            if count is not None:
                return Response({"bag_count": count[0]})
            else :
                return Response({"bag_count": 0})
