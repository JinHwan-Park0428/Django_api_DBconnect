# 필요한 모듈 임포트
import os
from rest_framework import viewsets
from DBConnect.serializers import *
from django.db import connection
from rest_framework.decorators import action
from rest_framework.response import Response
from random import *
from DBtest.settings import EMAIL_HOST_USER
from django.core.mail import send_mail
from DBConnect.models import *

# 각각의 클래스는 필요한 기능에 따른 SQL 쿼리문을 작성할 것
# 각각의 클래스의 함수에 접근 하기 위한 주소 예시
# ex) http://localhost:8000/테이블명/함수명/
# ex) http://localhost:8000/SkdevsecUser/create_user/

# 회원 정보 관련 테이블
# 회원가입, 아이디&닉네임 중복, 로그인, 내 정보 보기, 내 정보 수정하기
class SkdevsecUserViewSet(viewsets.ReadOnlyModelViewSet):
    # 테이블 출력을 위한 최소 코드
    queryset = SkdevsecUser.objects.all()
    serializer_class = SkdevsecUserSerializer

    # 관리자 권한 요구 코드
    # permission_classes = [permissions.IsAuthenticated]
    #
    # sql 인젝션 방어용 코드 ( GET 버전 나중에 수정 혹은 제거 해야함)
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

    # sql 인젝션 되는 코드
    # 회원가입 함수
    @action(detail=False, methods=['POST'])
    def create_user(self, request):
        try:
            # DB 접근할 cursor
            cursor = connection.cursor()

            # POST 메소드로 날라온 Request의 데이타 각각 추출
            uid = request.data['uid']
            upwd = request.data['upwd']
            unickname = request.data['unickname']
            uname = request.data['uname']
            umail = request.data['umail']
            uphone = request.data['uphone']
            ucreate_date = request.data['ucreate_date']
            authority = request.data['authority']

            # SQL 쿼리문 작성
            strsql = "INSERT INTO skdevsec_user VALUES ('" + uid + "', " + "'" + upwd + "', " + "'" + unickname + "', " + "'" + uname + "', " + "'" + umail + "', " + "'" + uphone + "', " + "'" + ucreate_date + "', " + "'" + authority +"')"

            # DB에 명령문 전송
            result = cursor.execute(strsql)

            # 데이터를 사용완료 했으면 DB와의 접속 종료(부하 방지)
            connection.commit()
            connection.close()

        # 에러가 발생했을 경우 에러 내용 출력 및 0 전송
        except Exception as e:
            connection.rollback()
            print(e)
            return Response(0)

        # 성공 했을 시, 1 전송
        else:
            return Response(1)

    # sql 인젝션 되는 코드
    # 아이디 중복&닉네임 중복
    @action(detail=False, methods=['POST'])
    def id_check(self, request):
        try:
            # DB 접근할 cursor
            cursor = connection.cursor()

            # POST 메소드로 날라온 Request의 데이터 각각 추출:
            uid = request.data['uid']

            # SQL 쿼리문 작성
            strsql = "SELECT * FROM skdevsec_user WHERE uid='" + uid + "'"

            # DB에 명령문 전송
            result = cursor.execute(strsql)
            datas = cursor.fetchall()

            # 데이터를 사용완료 했으면 DB와의 접속 종료(부하 방지)
            connection.commit()
            connection.close()

        # 에러가 발생했을 경우 에러 내용 출력
        except Exception as e:
            connection.rollback()
            print(e)

        # 데이터가 존재하면(중복이면) 1을 전송 아니면 0을 전송
        else:
            if len(datas) != 0:
                return Response(1)
            else:
                return Response(0)

    # sql 인젝션 되는 코드
    # 닉네임 중복
    @action(detail=False, methods=['POST'])
    def nickname_check(self, request):
        try:
            # DB 접근할 cursor
            cursor = connection.cursor()

            # POST 메소드로 날라온 Request의 데이터 각각 추출:
            unickname = request.data['unickname']

            # SQL 쿼리문 작성
            strsql = "SELECT * FROM skdevsec_user WHERE unickname='" + unickname + "'"
            # DB에 명령문 전송
            result = cursor.execute(strsql)
            datas = cursor.fetchall()

            # 데이터를 사용완료 했으면 DB와의 접속 종료(부하 방지)
            connection.commit()
            connection.close()

        # 에러가 발생했을 경우 에러 내용 출력
        except Exception as e:
            connection.rollback()
            print("에러구문: ", e)

        # 데이터가 존재하면(중복이면) 1을 전송 아니면 0을 전송
        else:
            if len(datas) != 0:
                return Response(1)
            else:
                return Response(0)

    # sql 인젝션 되는 코드
    # 이메일 중복 체크 및 인증 메일 전송
    @action(detail=False, methods=['POST'])
    def email_check(self, request):
        try:
            # DB 접근할 cursor
            cursor = connection.cursor()

            # POST 메소드로 날라온 Request의 데이타 각각 추출
            umail = request.data['umail']

            # SQL 쿼리문 작성
            strsql = "SELECT * FROM skdevsec_user WHERE umail='" + umail + "'"

            # DB에 명령문 전송
            result = cursor.execute(strsql)
            datas = cursor.fetchall()

            # 데이터를 사용완료 했으면 DB와의 접속 종료(부하 방지)
            connection.commit()
            connection.close()

        # 에러가 발생했을 경우 에러 내용 출력
        except Exception as e:
            connection.rollback()
            print("에러 내용: ", e)

            # 데이터가 존재하면(중복이면) 1을 전송 아니면 0을 전송
        else:
            if len(datas) != 0:
                return Response(1)
            else:
                try:
                    # 8자리 난수를 생성해서 인증번호로서, 메일 전송
                    i = randint(10000000, 99999999)
                    mail_title = "이메일 인증을 완료해주세요"
                    send_mail(mail_title, f"인증번호 : {i}", EMAIL_HOST_USER, [umail], fail_silently=False)
                    return Response(i)

                # 에러가 발생했을 경우 에러 내용 출력
                except Exception as e:
                    connection.rollback()
                    print("에러 내용1: ", e)

    # sql 인젝션 되는 코드
    # 로그인
    @action(detail=False, methods=['POST'])
    def login(self, request):
        new_data = dict()
        try:
            # DB 접근할 cursor
            cursor = connection.cursor()

            # POST 메소드로 날라온 Request의 데이타 각각 추출
            uid = request.data['uid']
            upwd = request.data['upwd']

            # SQL 쿼리문 작성
            strsql = "SELECT unickname, authority FROM skdevsec_user WHERE uid='" + uid + "' " + "and upwd='" + upwd + "'"

            # DB에 명령문 전송
            result = cursor.execute(strsql)
            datas = cursor.fetchall()

            # 데이터를 사용완료 했으면 DB와의 접속 종료(부하 방지)
            connection.commit()
            connection.close()

            # 불러온 데이터를 딕셔너리 형태로 저장
            for data in datas:
                new_data['unickname'] = data[0]
                new_data['authority'] = data[1]

        # 에러가 발생했을 경우 에러 내용 출력 및 로그인 실패 코드(0) 전송
        except Exception as e:
            connection.rollback()
            print(e)

        # 관리자 로그인이면 2 일반 사용자이면 1 전송
        else:
            if len(new_data) != 0:
                if new_data['authority'] == 1:
                    new_data['login_check'] = 2
                    return Response({'unickname': new_data['unickname'], 'login_check': new_data['login_check']})
                else:
                    new_data['login_check'] = 1
                    return Response({'unickname': new_data['unickname'], 'login_check': new_data['login_check']})
            else:
                return Response(0)

    # sql 인젝션 되는 코드
    # 내 정보 보기
    @action(detail=False, methods=['POST'])
    def view_info(self, request):
        new_data = dict()
        try:
            # DB 접근할 cursor
            cursor = connection.cursor()

            # POST 메소드로 날라온 Request의 데이타 각각 추출
            unickname = request.data['unickname']

            # SQL 쿼리문 작성
            strsql = "SELECT uid, unickname, uname, umail, uphone, ucreate_date FROM skdevsec_user WHERE unickname='" + unickname + "'"

            # DB에 명령문 전송
            result = cursor.execute(strsql)
            datas = cursor.fetchall()

            # 데이터를 사용완료 했으면 DB와의 접속 종료(부하 방지)
            connection.commit()
            connection.close()

            # 정보를 딕셔너리 형태로 재정립
            for data in datas:
                new_data['uid'] = data[0]
                new_data['unickname'] = data[1]
                new_data['uname'] = data[2]
                new_data['umail'] = data[3]
                new_data['uphone'] = data[4]
                new_data['ucreate_date'] = data[5]

        # 에러가 발생했을 경우 에러 내용 출력
        except Exception as e:
            connection.rollback()
            print(e)

        # 읽어들인 DB 값 전송
        else:
            return Response(new_data)

    # sql 인젝션 되는 코드
    # 회원 정보 수정 인증
    @action(detail=False, methods=['POST'])
    def before_change(self, request):
        try:
            # DB 접근할 cursor
            cursor = connection.cursor()

            # POST 메소드로 날라온 Request의 데이터 각각 추출:
            unickname = request.data['unickname']
            upwd = request.data['upwd']

            # SQL 쿼리문 작성
            strsql = "SELECT * FROM skdevsec_user WHERE unickname='" + unickname + "' and upwd ='" + upwd + "'"

            # DB에 명령문 전송
            result = cursor.execute(strsql)
            datas = cursor.fetchall()

            # 데이터를 사용완료 했으면 DB와의 접속 종료(부하 방지)
            connection.commit()
            connection.close()

        # 에러가 발생했을 경우 에러 내용 출력
        except Exception as e:
            connection.rollback()
            print(e)

        # 데이터가 존재하면(중복이면) 1을 전송 아니면 0을 전송
        else:
            if len(datas) != 0:
                return Response(1)
            else:
                return Response(0)

    # sql 인젝션 되는 코드
    # 내 정보 수정하기
    @action(detail=False, methods=['POST'])
    def change_info(self, request):
        try:
            # DB 접근할 cursor
            cursor = connection.cursor()

            # POST 메소드로 날라온 Request의 데이타 각각 추출
            uid = request.data['uid']
            unickname = request.data['unickname']
            umail = request.data['umail']
            uphone = request.data['uphone']

            # SQL 쿼리문 작성
            strsql = "UPDATE skdevsec_user SET unickname='" + unickname + "', " + "umail='" + umail + "', " +"uphone='" + uphone+ "' WHERE uid='" + uid + "'"

            # DB에 명령문 전송
            result = cursor.execute(strsql)
            datas = cursor.fetchall()

            # 데이터를 사용완료 했으면 DB와의 접속 종료(부하 방지)
            connection.commit()
            connection.close()

        # 에러가 발생했을 경우 에러 내용 출력 및 실패 코드 전송
        except Exception as e:
            connection.rollback()
            print(e)
            return Response(0)

        # 수정 완료 되면 성공 코드 전송
        else:
            return Response(1)

    # sql 인젝션 되는 코드
    # 비밀번호 변경
    @action(detail=False, methods=['POST'])
    def change_pwd(self, request):
        try:
            # DB 접근할 cursor
            cursor = connection.cursor()

            # POST 메소드로 날라온 Request의 데이타 각각 추출
            unickname = request.data['unickname']
            upwd = request.data['upwd']

            # SQL 쿼리문 작성
            strsql = "UPDATE skdevsec_user SET upwd='" + upwd + "' WHERE unickname='" + unickname + "'"

            # DB에 명령문 전송
            result = cursor.execute(strsql)

            # 데이터를 사용완료 했으면 DB와의 접속 종료(부하 방지)
            connection.commit()
            connection.close()

        # 에러가 발생했을 경우 에러 내용 출력 및 실패 코드 전송
        except Exception as e:
            connection.rollback()
            print(e)
            return Response(0)

        # 수정 완료 되면 성공 코드 전송
        else:
            return Response(1)


# 게시판 관련 테이블
# 게시판 출력, 게시물 출력, 게시물 등록, 게시물 수정, 게시물 삭제, 파일 삭제, 게시물 검색
class SkdevsecBoardViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = SkdevsecBoard.objects.all()
    serializer_class = SkdevsecBoardSerializer

    # sql 인젝션 되는 코드
    # 게시판 출력
    @action(detail=False, methods=['POST'])
    def board_outside(self, request):
        new_data = list()

        try:
            # DB 접근할 cursor
            cursor = connection.cursor()

            # POST 메소드로 날라온 Request의 데이타 각각 추출
            bcate = request.data['bcate']
            bpage = request.data['bpage']
            bpage = int(bpage)

            # SQL 쿼리문 작성
            strsql = "SELECT bid, btitle ,bfile, bview, bcomment, unickname, bcreate_date, b_lock FROM skdevsec_board where bcate='" + bcate + "' order by bid desc limit " + str(bpage*10-10) + ", 10"

            # DB에 명령문 전송
            result = cursor.execute(strsql)
            datas = cursor.fetchone()

            # 데이터를 사용완료 했으면 DB와의 접속 종료(부하 방지)
            connection.commit()
            connection.close()

            # 게시판 정보를 보내기 위한 대입 로직 구현
            if datas != None:
                while datas:
                    new_data_in = dict()
                    new_data_in['bid'] = datas[0]
                    new_data_in['btitle'] = datas[1]
                    new_data_in['bfile'] = datas[2]
                    new_data_in['bview'] = datas[3]
                    new_data_in['bcomment'] = datas[4]
                    new_data_in['unickname'] = datas[5]
                    new_data_in['bcreate_date'] = datas[6]
                    new_data_in['b_lock'] = datas[7]
                    new_data.append(new_data_in)
                    datas = cursor.fetchone()
            else : pass

        # 에러가 발생했을 경우 에러 내용 출력
        except Exception as e:
            connection.rollback()
            print(e)

        # 성공 했을 시, 데이터 전송
        else:
            return Response(new_data)

    # sql 인젝션 되는 코드
    # 게시물 출력
    @action(detail=False, methods=['POST'])
    def board_inside(self, request):
        new_data = dict()
        try:
            # DB 접근할 cursor
            cursor = connection.cursor()

            # POST 메소드로 날라온 Request의 데이타 각각 추출
            bid = request.data['bid']
            # SQL 쿼리문 작성
            strsql1 = "UPDATE skdevsec_board SET bview = bview+1 WHERE bid='" + bid + "'"
            strsql2 = "SELECT * FROM skdevsec_board WHERE bid='" + bid + "'"

            # DB에 명령문 전송
            result = cursor.execute(strsql1)

            # DB에 명령문 전송
            result = cursor.execute(strsql2)
            datas = cursor.fetchall()

            # 데이터를 사용완료 했으면 DB와의 접속 종료(부하 방지)
            connection.commit()
            connection.close()

            # 게시물 정보 대입
            new_data['bid'] = datas[0]
            new_data['btitle'] = datas[1]
            new_data['btext'] = datas[2]
            new_data['bfile'] = datas[3]
            new_data['bview'] = datas[4]
            new_data['bcomment'] = datas[5]
            new_data['unickname'] = datas[6]
            new_data['bcreate_date'] = datas[7]
            new_data['b_lock'] = datas[8]

        # 에러가 발생했을 경우 에러 내용 출력
        except Exception as e:
            connection.rollback()
            print(e)

        # 성공 했을 시, 데이터 전송
        else:
            return Response(new_data)

    # sql 인젝션 되는 코드
    # 게시물 등록
    @action(detail=False, methods=['POST'])
    def board_upload(self, request):
        new_data = dict()
        try:
            # POST 메소드로 날라온 Request의 데이타 각각 추출
            new_data['btitle'] = request.data['btitle']
            new_data['btext'] = request.data['btext']
            new_data['bfile'] = request.data['bfile']
            new_data['bview'] = request.data['bview']
            new_data['bcomment'] = request.data['bcomment']
            new_data['unickname'] = request.data['unickname']
            new_data['bcreate_date'] = request.data['bcreate_date']
            new_data['bcate'] = request.data['bcate']
            new_data['b_lock'] = request.data['b_lock']

            # DB에 저장하기 위해 시리얼라이저 함수 사용
            file_serializer = SkdevsecBoardSerializer(data = new_data)

            # 저장이 가능한 상태면 저장
            if file_serializer.is_valid():
                file_serializer.save()
            else:
                print("문제 생김")
                return Response(0)

        # 에러가 발생했을 경우 에러 내용 출력 및 실패 값 반환
        except Exception as e:
            connection.rollback()
            print(e)
            return Response(0)

        # 성공 했을 시, 성공 값 반환
        else:
            return Response(1)

    # sql 인젝션 되는 코드
    # 게시물 수정
    @action(detail=False, methods=['POST'])
    def change_board(self, request):
        try:
            # DB 접근할 cursor
            cursor = connection.cursor()

            # POST 메소드로 날라온 Request의 데이타 각각 추출
            bid = request.data['bid']
            btitle = request.data['btitle']
            btext = request.data['btext']
            bfile = request.data['bfile']
            bcate = request.data['bcate']
            b_lock = request.data['b_lock']

            # SQL 쿼리문 작성
            strsql1 = "UPDATE skdevsec_board SET btitle='" + btitle + "', btext='" + btext + "', bfile='" + bfile + "', bcate='" + bcate + "', b_lock='" + b_lock + "' WHERE bid='" + bid + "'"

            # DB에 명령문 전송
            result = cursor.execute(strsql1)

            # 데이터를 사용완료 했으면 DB와의 접속 종료(부하 방지)
            connection.commit()
            connection.close()

        # 에러가 발생했을 경우 에러 내용 출력 및 실패 값 반환
        except Exception as e:
            connection.rollback()
            print(e)
            return Response(0)

        # 성공 했을 시, 성공 값 반환
        else:
            return Response(1)

    # sql 인젝션 되는 코드
    # 게시물 삭제
    @action(detail=False, methods=['POST'])
    def board_delete(self, request):
        try:
            # DB 접근할 cursor
            cursor = connection.cursor()

            # POST 메소드로 날라온 Request의 데이타 각각 추출
            bid = request.data['bid']

            # SQL 쿼리문 작성
            strsql1 = "SELECT bfile FROM skdevsec_board WHERE bid='" + bid + "'"
            strsql2 = "DELETE FROM skdevsec_board WHERE bid='" + bid + "'"

            # DB에 명령문 전송
            result = cursor.execute(strsql1)
            datas = cursor.fetchall()
            # 파일 삭제
            os.remove(datas[0][0])

            # DB에 명령문 전송
            result = cursor.execute(strsql2)

            # 데이터를 사용완료 했으면 DB와의 접속 종료(부하 방지)
            connection.commit()
            connection.close()

        # 에러가 발생했을 경우 에러 내용 출력 및 실패 값 반환
        except Exception as e:
            connection.rollback()
            print(e)
            return Response(0)

        # 성공 했을 시, 성공 값 반환
        else:
            return Response(1)

    # sql 인젝션 되는 코드
    # 파일 삭제
    @action(detail=False, methods=['POST'])
    def file_delete(self, request):
        try:
            # DB 접근할 cursor
            cursor = connection.cursor()

            # POST 메소드로 날라온 Request의 데이타 각각 추출
            bid = request.data['bid']
            bfile = request.data['bfile']

            # SQL 쿼리문 작성
            strsql1 = "SELECT bfile FROM skdevsec_board WHERE bid='" + bid + "'"
            strsql2 = "UPDATE skdevsec_board SET bfile=0 WHERE bid='" + bid + "'"

            # DB에 명령문 전송
            result = cursor.execute(strsql1)
            datas = cursor.fetchall()

            # 파일 삭제
            os.remove(datas[0][0])

            # DB에 명령문 전송
            result = cursor.execute(strsql2)

            # 데이터를 사용완료 했으면 DB와의 접속 종료(부하 방지)
            connection.commit()
            connection.close()

        # 에러가 발생했을 경우 에러 내용 출력 및 실패 값 반환
        except Exception as e:
            connection.rollback()
            print(e)
            return Response(0)

        # 성공 했을 시, 성공 값 반환
        else:
            return Response(1)

    # sql 인젝션 되는 코드
    # 게시물 검색
    @action(detail=False, methods=['POST'])
    def board_search(self, request):
        new_data = list()
        try:
            # DB 접근할 cursor
            cursor = connection.cursor()

            # POST 메소드로 날라온 Request의 데이타 각각 추출
            bcode = request.data['bcode']
            bsearch = request.data['bsearch']
            bcode = int(bcode)
            # 검색 조건 코드 분류
            # 전체 0, 제목 1, 내용 2, 작성자 3, 제목 + 내용 4
            if bcode == 0:
                # SQL 쿼리문 작성
                strsql = "SELECT bid, btitle, bfile, bview, bcomment, unickname, bcreate_date FROM skdevsec_board WHERE (btitle LIKE '%" + bsearch + "%' OR btext LIKE '%" + bsearch + "%' OR unickname LIKE '%" + bsearch + "%') AND b_lock=0"
            elif bcode == 1:
                strsql = "SELECT bid, btitle, bfile, bview, bcomment, unickname, bcreate_date FROM skdevsec_board WHERE (btitle LIKE '%" + bsearch + "%') AND b_lock=0"
            elif bcode == 2:
                strsql = "SELECT bid, btitle, bfile, bview, bcomment, unickname, bcreate_date FROM skdevsec_board WHERE (btext LIKE '%" + bsearch + "%') AND b_lock=0"
            elif bcode == 3:
                strsql = "SELECT bid, btitle, bfile, bview, bcomment, unickname, bcreate_date FROM skdevsec_board WHERE (unickname LIKE '%" + bsearch + "%') AND b_lock=0"
            elif bcode == 4:
                strsql = "SELECT bid, btitle, bfile, bview, bcomment, unickname, bcreate_date FROM skdevsec_board WHERE (btitle LIKE '%" + bsearch + "%' OR btext LIKE '%" + bsearch + "%') AND b_lock=0"
            else:
                return Response("코드 값 잘못 보냄!!")

            # DB에 명령문 전송
            result = cursor.execute(strsql)
            datas = cursor.fetchone()

            # 데이터를 사용완료 했으면 DB와의 접속 종료(부하 방지)
            connection.commit()
            connection.close()

            # 게시판 정보를 보내기 위한 대입 로직 구현
            if datas != None:
                while datas:
                    new_data_in = dict()
                    new_data_in['bid'] = datas[0]
                    new_data_in['btitle'] = datas[1]
                    new_data_in['bfile'] = datas[2]
                    new_data_in['bview'] = datas[3]
                    new_data_in['bcomment'] = datas[4]
                    new_data_in['unickname'] = datas[5]
                    new_data_in['bcreate_date'] = datas[6]
                    new_data_in['b_lock'] = 0
                    new_data.append(new_data_in)
                    datas = cursor.fetchone()
            else : pass

        # 에러가 발생했을 경우 에러 내용 출력
        except Exception as e:
            connection.rollback()
            print(e)

        # 성공 했을 시, 데이터 전송
        else:
            return Response(new_data)

class SkdevsecBagViewSet(viewsets.ReadOnlyModelViewSet):
    # 테이블 출력을 위한 최소 코드
    queryset = SkdevsecBag.objects.all()
    serializer_class = SkdevsecBagSerializer


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



