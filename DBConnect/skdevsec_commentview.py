# 필요한 모듈 임포트
from django.db import connection
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from DBConnect.serializers import *


# 댓글 관련 테이블
class SkdevsecCommentViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = SkdevsecComment.objects.all()
    serializer_class = SkdevsecCommentSerializer

    # sql 인젝션 되는 코드
    # 댓글 출력
    @action(detail=False, methods=['POST'])
    def view_comment(self, request):
        # 데이터 저장을 위한 리스트 선언
        new_data = list()
        try:
            # DB 접근할 cursor
            cursor = connection.cursor()

            # POST 메소드로 날라온 Request의 데이터 각각 추출
            bid = request.data['bid']
            cpage = request.data['cpage']
            cpage = int(cpage)

            # SQL 쿼리문 작성
            strsql = "SELECT COUNT(*) FROM skdevsec_comment WHERE bid='" + bid + "'"

            # DB에 명령문 전송
            cursor.execute(strsql)
            count = cursor.fetchone()

            if count is not None:
                # 댓글 갯수 저장
                new_data.append({"comment_count": count[0]})

                # SQL 쿼리문 작성
                strsql1 = "SELECT cid, unickname, ctext, ccreate_date, clock FROM skdevsec_comment where bid='" + bid + "' order by cid LIMIT " + str(
                    cpage * 10 - 10) + " , 10"

                # DB에 명령문 전송
                cursor.execute(strsql1)
                datas = cursor.fetchone()

                # 데이터 갯수만큼 반복
                while datas:
                    new_data_in = dict()
                    new_data_in['cid'] = datas[0]
                    new_data_in['unickname'] = datas[1]
                    new_data_in['ctext'] = datas[2]
                    new_data_in['ccreate_date'] = datas[3]
                    new_data_in['clock'] = datas[4]
                    new_data.append(new_data_in)
                    datas = cursor.fetchone()

            else:
                connection.close()
                return Response({"comment_count": 0})

            # DB와 접속 종료
            connection.commit()
            connection.close()

        # 에러가 발생했을 경우 백엔드에 에러 내용 출력 프론트엔드에 0 전송
        except Exception as e:
            connection.rollback()
            print(f"view_comment 에러: {e}")
            return Response(0)

        # 성공 했을 시, 프론트엔드에 데이터 전송
        else:
            return Response(new_data)

    # sql 인젝션 되는 코드
    # 댓글 작성
    @action(detail=False, methods=['POST'])
    def comment_write(self, request):
        try:
            # DB 접근할 cursor
            cursor = connection.cursor()

            # POST 메소드로 날라온 Request의 데이터 각각 추출
            bid = str(request.data['bid'])
            unickname = str(request.data['unickname'])
            ctext = str(request.data['ctext'])
            ccreate_date = str(request.data['ccreate_date'])
            clock = str(request.data['clock'])

            # SQL 쿼리문 작성
            strsql = "INSERT INTO skdevsec_comment(bid, unickname, ctext, ccreate_date, clock) VALUES('" + bid + "', '" + unickname + "', '" + ctext + "', '" + ccreate_date + "', '" + clock + "')"

            # DB에 명령문 전송
            cursor.execute(strsql)

            # SQL 쿼리문 작성
            strsql1 = "UPDATE skdevsec_board SET bcomment=bcomment+1 WHERE bid='" + bid + "'"

            # DB에 명령문 전송
            cursor.execute(strsql1)

            # 데이터를 사용완료 했으면 DB와 접속 종료(부하 방지)
            connection.commit()
            connection.close()

        # 에러가 발생했을 경우 백엔드에 에러 내용 출력 및 프론트엔드에 0 전송
        except Exception as e:
            connection.rollback()
            print(f"comment_write 에러: {e}")
            return Response(0)

        # 성공 했을 시, 프론트엔드에 1 전송
        else:
            return Response(1)

    # sql 인젝션 되는 코드
    # 댓글 삭제
    @action(detail=False, methods=['POST'])
    def comment_delete(self, request):
        try:
            # DB 접근할 cursor
            cursor = connection.cursor()

            # POST 메소드로 날라온 Request의 데이터 각각 추출
            bid = request.data['bid']
            cid = request.data['cid']

            # SQL 쿼리문 작성
            strsql = "DELETE FROM skdevsec_comment WHERE cid='" + cid + "'"

            # DB에 명령문 전송
            cursor.execute(strsql)

            # SQL 쿼리문 작성
            strsql1 = "UPDATE skdevsec_board SET bcomment=bcomment-1 WHERE bid='" + bid + "'"

            # DB에 명령문 전송
            cursor.execute(strsql1)

            # 데이터를 사용완료 했으면 DB와 접속 종료(부하 방지)
            connection.commit()
            connection.close()

        # 에러가 발생했을 경우 백엔드에 에러 내용 출력 및 프론트엔드 0 전송
        except Exception as e:
            connection.rollback()
            print(f"comment_delete 에러: {e}")
            return Response(0)

        # 성공 했을 시, 프론트엔드에 1 전송
        else:
            return Response(1)
