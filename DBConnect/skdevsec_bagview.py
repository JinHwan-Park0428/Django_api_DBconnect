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
            cursor_product = connection.cursor()
            # POST 메소드로 날라온 Request의 데이터 각각 추출
            unickname = request.data['unickname']
            # SQL 쿼리문 작성
            sql_query_1 = "SELECT * FROM skdevsec_user WHERE unickname=%s"
            # DB에 쿼리 전달
            cursor.execute(sql_query_1, (unickname, ))
            # 응답 값 저장
            uid = cursor.fetchone()
            # unickname에 해당하는 uid가 있다면
            if uid is not None:
                # SQL 쿼리문 작성
                sql_query_2 = "SELECT * FROM skdevsec_bag where uid=%s"
                # DB에 쿼리 전달
                cursor.execute(sql_query_2, (uid[0], ))
                # 응답 값 저장
                data = cursor.fetchone()
            # uid가 없다면
            else:
                # DB와 연결 종료
                connection.close()
                # 0 전송
                return Response(0)
            # uid에 해당하는 skdevsec_bag 데이터가 있다면
            if data is not None:
                # 데이터 만큼 반복 할 것
                while data:
                    # 데이터를 저장할 딕셔너리 선언
                    new_data_in = dict()
                    # SQL 쿼리문 작성
                    sql_query_3 = "SELECT * FROM skdevsec_product WHERE pid=%s"
                    # DB에 쿼리 전달
                    cursor_product.execute(sql_query_3, (int(data[2]), ))
                    # 응답 값 저장
                    products = cursor_product.fetchone()
                    # pid에 해당하는 skdevsec_product 값이 있으면
                    if products is not None:
                        # 필요한 데이터를 딕셔너리에 저장
                        new_data_in['bag_id'] = data[0]
                        new_data_in['pid'] = data[2]
                        new_data_in['pname'] = products[1]
                        new_data_in['pcate'] = products[2]
                        new_data_in['pimage'] = products[3]
                        new_data_in['ptext'] = products[4]
                        new_data_in['pprice'] = products[5]
                        new_data_in['bcount'] = data[3]
                        # 딕셔너리를 리스트에 저장
                        new_data.append(new_data_in)
                    # 값이 없으면
                    else:
                        # DB와 접속 종료
                        connection.close()
                        # 0 값 전송
                        return Response(0)
                    # while data를 한번 실행하고, 다음 데이터를 불러온다.
                    data = cursor.fetchone()
            # 장바구니 목록이 없으면 0 전송
            else:
                # DB와 접속 종료
                connection.close()
                # 0 값 전송
                return Response(0)
        # 에러 처리
        except Exception as e:
            # DB 변경점을 롤백
            connection.rollback()
            # 에러 출력
            print(f"에러: {e}")
            # 0 전송
            return Response(0)
        # try 구문에서 오류가 안나면
        else:
            # DB와 접속 종료
            connection.close()
            # 데이터 전송
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
            # DB에 쿼리 전달
            cursor.execute(sql_query, (bag_id, ))
            # DB 변경점을 저장
            connection.commit()
            # DB와 연결 종료
            connection.close()
        # 에러 처리
        except Exception as e:
            # DB 변경점을 롤백
            connection.rollback()
            # 에러 출력
            print(f"에러: {e}")
            # 0 전송
            return Response(0)
        # try 구문에서 오류 없으면, 1 전송
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
            # DB에 쿼리 전달
            cursor.execute(sql_query_1, (unickname, ))
            # 응답 값 저장
            uid = cursor.fetchone()
            # unickname에 해당하는 데이터가 있으면
            if uid is not None:
                # SQL 쿼리문 작성
                sql_query_2 = "SELECT * FROM skdevsec_bag WHERE uid=%s AND pid=%s"
                # DB에 쿼리 전달
                cursor.execute(sql_query_2, (uid[0], pid,))
                # 응답 값 저장
                data = cursor.fetchone()
            # 데이터가 없으면
            else:
                # 0 전송
                return Response(0)
            # 해당하는 uid와 pid를 만족하는 데이터가 있으면
            if data is not None:
                # SQL 쿼리문 작성
                sql_query_3 = "UPDATE skdevsec_bag SET bcount=bcount+%s WHERE pid=%s AND uid=%s"
                # DB에 쿼리 전달
                cursor.execute(sql_query_3, (bcount, pid, uid[0]))
            # 데이터가 없으면
            else:
                # SQL 쿼리문 작성
                sql_query_3 = "INSERT INTO skdevsec_bag(uid, pid, bcount) VALUES(%s, %s, %s)"
                # DB에 쿼리 전달
                cursor.execute(sql_query_3, (uid[0], pid, bcount))
            # DB 변경점 저장
            connection.commit()
            # DB와 접속 종료
            connection.close()
        # 에러 처리
        except Exception as e:
            # DB 변경점 롤백
            connection.rollback()
            # 에러 출력
            print(f"에러: {e}")
            # 0 전송
            return Response(0)
        # try 구문에서 에러가 발생하지 않으면
        else:
            # 1 전송
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
            # DB에 쿼리 전달
            cursor.execute(sql_query_1, (unickname, ))
            # 응답 값 저장
            uid = cursor.fetchone()
            # unickname에 해당하는 uid가 있으면
            if uid is not None:
                # SQL 쿼리문 작성
                sql_query_2 = "SELECT COUNT(*) FROM skdevsec_bag where uid=%s"
                # DB에 쿼리 전달
                cursor.execute(sql_query_2, (uid[0], ))
                # 응답 값 저장
                count = cursor.fetchone()
            # 없으면
            else:
                # 0 전송
                return Response(0)
        # 에러 처리
        except Exception as e:
            # DB 변경점 롤백
            connection.rollback()
            # 에러 출력
            print(f"에러: {e}")
            # 0 전송
            return Response(0)
        # 성공 했을 시, 프론트엔드에 데이터 전송
        else:
            # 데이터가 있으면
            if count is not None:
                # DB와 접속 종료
                connection.close()
                # 데이터 개수 전송
                return Response({"bag_count": count[0]})
            # 데이터가 없으면
            else:
                # DB와 접속 종료
                connection.close()
                # 데이터 개수 전송
                return Response({"bag_count": 0})
