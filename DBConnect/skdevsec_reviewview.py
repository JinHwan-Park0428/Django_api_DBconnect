# 필요한 모듈 임포트
from django.db import connection
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from DBConnect.serializers import *
from rest_framework.permissions import IsAuthenticated


# 상품 리뷰 관련 테이블
class SkdevsecReviewViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = SkdevsecReview.objects.all()
    serializer_class = SkdevsecReviewSerializer
    permission_classes = [IsAuthenticated]

    # 리뷰 출력
    @action(detail=False, methods=['POST'])
    def review_output(self, request):
        # 데이터 저장을 위한 리스트 선언
        new_data = list()
        try:
            # DB 접근할 cursor
            cursor = connection.cursor()

            # POST 메소드로 날라온 Request의 데이터 각각 추출
            pid = int(request.data['pid'])

            # SQL 쿼리문 작성
            sql_query = "SELECT * FROM skdevsec_review where pid=%s order by rid desc"

            # DB에 명령문 전송
            cursor.execute(sql_query, (pid, ))
            data = cursor.fetchone()

            # 데이터가 있으면
            if data is not None:
                # 데이터만큼 반복
                while data:
                    new_data_in = dict()
                    new_data_in['rid'] = int(data[0])
                    new_data_in['rstar'] = float(data[2])
                    new_data_in['unickname'] = data[3]
                    new_data_in['rcreate_date'] = data[4]
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

        # 에러가 발생했을 경우 백엔드에 에러 내용 출력 및 프론트엔드에 0 전송
        except Exception as e:
            connection.rollback()
            print(f"에러: {e}")
            return Response(0)

        # 성공 했을 시, 프론트엔드에 데이터 전송
        else:
            return Response(new_data)

    # 리뷰 작성
    @action(detail=False, methods=['POST'])
    def review_write(self, request):
        try:
            # DB 접근할 cursor
            cursor = connection.cursor()

            # POST 메소드로 날라온 Request의 데이터 각각 추출
            pid = int(request.data['pid'])
            rstar = float(request.data['rstar'])
            unickname = request.data['unickname']
            rcreate_date = request.data['rcreate_date']

            # SQL 쿼리문 작성
            sql_query_1 = "INSERT INTO skdevsec_review(pid, rstar, unickname, rcreate_date) VALUES(%s, %f, %s, %s)"

            # DB에 명령문 전송
            cursor.execute(sql_query_1, (pid, rstar, unickname, rcreate_date))
            connection.commit()

            # SQL 쿼리문 작성
            sql_query_2 = "UPDATE skdevsec_product SET preview = (SELECT COUNT(*) FROM skdevsec_review WHERE pid=%s), " \
                          "preview_avg =(SELECT round(avg(rstar),1) FROM skdevsec_review WHERE pid=%s)  WHERE pid=%s "

            # DB에 명령문 전송
            cursor.execute(sql_query_2, (pid, pid, pid))

            # DB와 접속 종료
            connection.commit()
            connection.close()

        # 에러가 발생했을 경우 백엔드에 에러 내용 출력 및 프론트엔드에 0 전송
        except Exception as e:
            connection.rollback()
            print(f"에러: {e}")
            return Response(0)

        # 성공 했을 시, 프론트 엔드에 1 전송
        else:
            return Response(1)

    # 리뷰 삭제
    @action(detail=False, methods=['POST'])
    def comment_delete(self, request):
        try:
            # DB 접근할 cursor
            cursor = connection.cursor()

            # POST 메소드로 날라온 Request의 데이터 각각 추출
            rid = int(request.data['rid'])
            pid = int(request.data['pid'])

            # SQL 쿼리문 작성
            sql_query_1 = "DELETE FROM skdevsec_review WHERE rid=%s"

            # DB에 명령문 전송
            cursor.execute(sql_query_1, (rid, ))
            connection.commit()

            # SQL 쿼리문 작성
            sql_query_2 = "UPDATE skdevsec_product SET preview = (SELECT COUNT(*) FROM skdevsec_review WHERE pid=%s), " \
                          "preview_avg =(SELECT round(avg(rstar),1) FROM skdevsec_review WHERE pid=%s)  WHERE pid=%s "

            # DB에 명령문 전송
            cursor.execute(sql_query_2, (pid, pid, pid,))

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

    # 리뷰 검증
    @action(detail=False, methods=['POST'])
    def review_certified(self, request):
        try:
            # 데이터 처리를 위한 리스트 선언
            pname_list = list()

            # DB 접근할 cursor
            cursor = connection.cursor()
            cursor_oid = connection.cursor()

            # POST 메소드로 날라온 Request의 데이터 각각 추출
            unickname = request.data['unickname']
            pname = request.data['pname']

            # SQL 쿼리문 작성
            sql_query_1 = "SELECT * FROM skdevsec_user WHERE unickname=%s"

            # DB에 명령문 전송
            cursor.execute(sql_query_1, (unickname, ))
            uid = cursor.fetchone()

            if uid is not None:
                # SQL 쿼리문 작성
                sql_query_2 = "SELECT * FROM skdevsec_orderuser WHERE uid=%s"

                # DB에 명령문 전송
                cursor_oid.execute(sql_query_2, (uid[0], ))
                oid = cursor_oid.fetchone()

            else:
                return Response(0)

            while oid:
                # SQL 쿼리문 작성
                sql_query_3 = "SELECT * FROM skdevsec_orderproduct WHERE oid=%s"

                # DB에 명령문 전송
                cursor.execute(sql_query_3, (int(oid[0]), ))
                _pname = cursor.fetchone()

                pname_list.append(_pname[2])
                oid = cursor_oid.fetchone()

            pname_count = {}

            for i in pname_list:
                try:
                    pname_count[i] += 1
                except:
                    pname_count[i] = 1

            # 만약 사용자가 상품을 구매했으면 리뷰한 적이 있는지 확인
            if pname in pname_list:
                # SQL 쿼리문 작성
                sql_query_4 = "SELECT * FROM skdevsec_product WHERE pname=%s"

                # DB에 명령문 전송
                cursor.execute(sql_query_4, (pname, ))
                pid = cursor.fetchone()

                # SQL 쿼리문 작성
                sql_query_5 = "SELECT COUNT(*) FROM skdevsec_review WHERE pid=%s AND unickname=%s"

                # DB에 명령문 전송
                cursor.execute(sql_query_5, (int(pid[0]), unickname, ))
                review = cursor.fetchone()
            # 구매한적이 없으면 프론트엔드로 0 전송
            else:
                return Response(0)

            # DB와 접속 종료
            connection.close()

        # 에러가 발생했을 경우 백엔드에 에러 내용 출력 및 프론트엔드에 0 전송
        except Exception as e:
            connection.rollback()
            print(f"에러: {e}")
            return Response(0)

        # 리뷰를 작성할 수 없으면 프론트엔드에 1 전송, 작성할 수 있으면 0 전송
        else:
            if pname_count[pname] <= int(review[0]):
                return Response(1)
            else:
                return Response(0)