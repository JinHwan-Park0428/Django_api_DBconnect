# 필요한 모듈 임포트
from django.db import connection
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from DBConnect.serializers import *

# 상품 리뷰 관련 테이블
class SkdevsecReviewViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = SkdevsecReview.objects.all()
    serializer_class = SkdevsecReviewSerializer

    # sql 인젝션 되는 코드
    # 리뷰 출력
    @action(detail=False, methods=['POST'])
    def review_output(self, request):
        # 데이터 저장을 위한 리스트 선언
        new_data = list()
        try:
            # DB 접근할 cursor
            cursor = connection.cursor()

            # POST 메소드로 날라온 Request의 데이터 각각 추출
            pid = request.data['pid']

            # SQL 쿼리문 작성
            strsql = "SELECT rid, rstar, unickname, rcreate_date FROM skdevsec_review where pid='" + pid + "' order by rid desc"

            # DB에 명령문 전송
            cursor.execute(strsql)
            datas = cursor.fetchone()

            # 데이터가 있으면
            if datas is not None:
                # 데이터만큼 반복
                while datas:
                    new_data_in = dict()
                    new_data_in['rid'] = datas[0]
                    new_data_in['rstar'] = datas[1]
                    new_data_in['unickname'] = datas[2]
                    new_data_in['rcreate_date'] = datas[3]
                    new_data.append(new_data_in)
                    datas = cursor.fetchone()
            # 데이터가 없으면
            else:
                # DB와 접속 종료
                connection.commit()
                connection.close()
                # 프론트엔드로 0 전송
                return Response(0)

            # DB와 접속 종료
            connection.commit()
            connection.close()

        # 에러가 발생했을 경우 백엔드에 에러 내용 출력 및 프론트엔드에 0 전송
        except Exception as e:
            connection.rollback()
            print(f"review_output 에러: {e}")
            return Response(0)

        # 성공 했을 시, 프론트엔드에 데이터 전송
        else:
            return Response(new_data)

    # sql 인젝션 되는 코드
    # 리뷰 작성
    @action(detail=False, methods=['POST'])
    def review_write(self, request):
        try:
            # DB 접근할 cursor
            cursor = connection.cursor()

            # POST 메소드로 날라온 Request의 데이터 각각 추출
            pid = request.data['pid']
            rstar = request.data['rstar']
            unickname = request.data['unickname']
            rcreate_date = request.data['rcreate_date']

            # SQL 쿼리문 작성
            strsql1 = "INSERT INTO skdevsec_review(pid, rstar, unickname, rcreate_date) VALUES('" + pid + "', '" + rstar + "', '" + unickname + "', '" + rcreate_date + "')"

            # DB에 명령문 전송
            cursor.execute(strsql1)

            # SQL 쿼리문 작성
            strsql2 = "UPDATE skdevsec_product SET preview = (SELECT COUNT(*) FROM skdevsec_review WHERE pid='" + pid + "'), preview_avg =(SELECT round(avg(rstar),1) FROM skdevsec_review WHERE pid='" + pid + "')  WHERE pid='" + pid + "'"

            # DB에 명령문 전송
            cursor.execute(strsql2)

            # DB와 접속 종료
            connection.commit()
            connection.close()

        # 에러가 발생했을 경우 백엔드에 에러 내용 출력 및 프론트엔드에 0 전송
        except Exception as e:
            connection.rollback()
            print(f"review_write 에러: {e}")
            return Response(0)

        # 성공 했을 시, 프론트 엔드에 1 전송
        else:
            return Response(1)

    # sql 인젝션 되는 코드
    # 리뷰 삭제
    @action(detail=False, methods=['POST'])
    def comment_delete(self, request):
        try:
            # DB 접근할 cursor
            cursor = connection.cursor()

            # POST 메소드로 날라온 Request의 데이터 각각 추출
            rid = request.data['rid']
            pid = request.data['pid']

            # SQL 쿼리문 작성
            strsql = "DELETE FROM skdevsec_review WHERE rid='" + rid + "'"

            # DB에 명령문 전송
            cursor.execute(strsql)

            # SQL 쿼리문 작성
            strsql1 = "UPDATE skdevsec_product SET preview = (SELECT COUNT(*) FROM skdevsec_review WHERE pid='" + pid + "'), preview_avg =(SELECT round(avg(rstar),1) FROM skdevsec_review WHERE pid='" + pid + "')  WHERE pid='" + pid + "'"

            # DB에 명령문 전송
            cursor.execute(strsql1)

            # DB와 접속 종료
            connection.commit()
            connection.close()

        # 에러가 발생했을 경우 백엔드에 에러 내용 출력 및 프론트엔드에 0 전송
        except Exception as e:
            connection.rollback()
            print(f"comment_delete 에러: {e}")
            return Response(0)

        # 성공 했을 시, 프론트엔드에 1 전송
        else:
            return Response(1)

    # sql 인젝션 되는 코드
    # 리뷰 검증
    @action(detail=False, methods=['POST'])
    def review_certified(self, request):
        try:
            # 데이터 처리를 위한 리스트 선언
            pname_list = list()

            # DB 접근할 cursor
            cursor = connection.cursor()

            # POST 메소드로 날라온 Request의 데이터 각각 추출
            unickname = request.data['unickname']
            pname = request.data['pname']

            # SQL 쿼리문 작성
            strsql = "SELECT uid FROM skdevsec_user WHERE unickname='" + unickname + "'"

            # DB에 명령문 전송
            cursor.execute(strsql)
            uid = cursor.fetchone()

            # SQL 쿼리문 작성
            strsql1 = "SELECT oid FROM skdevsec_orderuser WHERE uid='" + uid[0] + "'"

            # DB에 명령문 전송
            cursor.execute(strsql1)
            oids = cursor.fetchall()

            for oid in oids:
                # SQL 쿼리문 작성
                strsql2 = "SELECT pname FROM skdevsec_orderproduct WHERE oid='" + str(oid[0]) + "'"

                # DB에 명령문 전송
                cursor.execute(strsql2)
                pnames = cursor.fetchall()

                for _pname in pnames:
                    pname_list.append(_pname[0])

            pname_count = {}
            for i in pname_list:
                try:
                    pname_count[i] += 1
                except:
                    pname_count[i] = 1

            # 만약 사용자가 상품을 구매했으면 리뷰한 적이 있는지 확인
            if pname in pname_list:
                # SQL 쿼리문 작성
                strsql3 = "SELECT pid FROM skdevsec_product WHERE pname='" + pname + "'"

                # DB에 명령문 전송
                cursor.execute(strsql3)
                pid = cursor.fetchone()

                # SQL 쿼리문 작성
                strsql4 = "SELECT COUNT(*) FROM skdevsec_review WHERE pid='" + str(pid[0]) + "' AND unickname='" + unickname + "'"

                # DB에 명령문 전송
                cursor.execute(strsql4)
                review = cursor.fetchall()
            # 구매한적이 없으면 프론트엔드로 0 전송
            else:
                return Response(0)

            # DB와 접속 종료
            connection.commit()
            connection.close()

        # 에러가 발생했을 경우 백엔드에 에러 내용 출력 및 프론트엔드에 0 전송
        except Exception as e:
            connection.rollback()
            print(f"review_certified 에러: {e}")
            return Response(0)

        # 리뷰를 작성할 수 없으면 프론트엔드에 1 전송, 작성할 수 있으면 0 전송
        else:
            if pname_count[pname] <= int(review[0][0]):
                return Response(1)
            else:
                return Response(0)