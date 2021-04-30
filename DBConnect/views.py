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
# 회원가입, 아이디&닉네임 중복, 이메일 중복체크 및 전송, 로그인, 내 정보 보기, 회원 정보 수정 전 인증, 내 정보 수정하기, 비밀번호 변경
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
    # 관리자 페이지 (회원 정보 검색)
    @action(detail=False, methods=['POST'])
    def admin_user_info(self, request):
        # 권한이 1 이고 아이디가 admin일 시
        if request.data['authority'] == '1' and request.data['uid'] == 'admin':
            new_data = list()
            try:
                # POST 메소드로 날라온 Request의 데이터 각각 추출
                upage = request.data['upage']
                upage = int(upage)

                # DB 접근할 cursor
                cursor = connection.cursor()

                # SQL 쿼리문 작성
                strsql1 = "SELECT COUNT(*) FROM skdevsec_user"

                # DB에 명령문 전송
                cursor.execute(strsql1)
                datas = cursor.fetchone()

                new_data.append({"user_count": datas[0]})

                # SQL 쿼리문 작성
                strsql = "SELECT * FROM skdevsec_user order by ucreate_date desc limit " + str(upage * 10 - 10) + ", 10"

                # DB에 명령문 전송
                cursor.execute(strsql)
                datas = cursor.fetchone()

                # 데이터를 사용완료 했으면 DB와의 접속 종료(부하 방지)
                connection.commit()
                connection.close()

                # 게시판 정보를 보내기 위한 대입 로직 구현
                if datas is not None:
                    while datas:
                        new_data_in = dict()
                        new_data_in['uid'] = datas[0]
                        # pwd = ''
                        # for i in datas[1]:
                        #     pwd += '*'
                        new_data_in['upwd'] = datas[1]
                        new_data_in['unickname'] = datas[2]
                        new_data_in['uname'] = datas[3]
                        new_data_in['umail'] = datas[4]
                        new_data_in['uphone'] = datas[5]
                        new_data_in['ucreate_date'] = datas[6]
                        new_data_in['authority'] = datas[7]
                        new_data.append(new_data_in)
                        datas = cursor.fetchone()
                else:
                    return Response(0)

            # 에러가 발생했을 경우 에러 내용 출력
            except Exception as e:
                connection.rollback()
                print(e)
                return Response(0)

            # 성공 했을 시, 데이터 전송
            else:
                return Response(new_data)
        else :
            return Response(0)

    # sql 인젝션 되는 코드
    # 회원가입 함수
    @action(detail=False, methods=['POST'])
    def create_user(self, request):
        try:
            # DB 접근할 cursor
            cursor = connection.cursor()

            # POST 메소드로 날라온 Request의 데이터 각각 추출
            uid = request.data['uid']
            upwd = request.data['upwd']
            unickname = request.data['unickname']
            uname = request.data['uname']
            umail = request.data['umail']
            uphone = request.data['uphone']
            ucreate_date = request.data['ucreate_date']
            authority = request.data['authority']

            # SQL 쿼리문 작성
            strsql = "INSERT INTO skdevsec_user VALUES ('" + uid + "', " + "'" + upwd + "', " + "'" + unickname + "', " + "'" + uname + "', " + "'" + umail + "', " + "'" + uphone + "', " + "'" + ucreate_date + "', " + "'" + authority + "')"

            # DB에 명령문 전송
            cursor.execute(strsql)

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
    # 아이디 중복
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
            cursor.execute(strsql)
            datas = cursor.fetchall()

            # 데이터를 사용완료 했으면 DB와의 접속 종료(부하 방지)
            connection.commit()
            connection.close()

        # 에러가 발생했을 경우 에러 내용 출력
        except Exception as e:
            connection.rollback()
            print(e)
            return Response(0)

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
            cursor.execute(strsql)
            datas = cursor.fetchall()

            # 데이터를 사용완료 했으면 DB와의 접속 종료(부하 방지)
            connection.commit()
            connection.close()

        # 에러가 발생했을 경우 에러 내용 출력
        except Exception as e:
            connection.rollback()
            print("에러구문: ", e)
            return Response(0)

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

            # POST 메소드로 날라온 Request의 데이터 각각 추출
            umail = request.data['umail']

            # SQL 쿼리문 작성
            strsql = "SELECT * FROM skdevsec_user WHERE umail='" + umail + "'"

            # DB에 명령문 전송
            cursor.execute(strsql)
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
                    return Response(0)

    # sql 인젝션 되는 코드
    # 로그인
    @action(detail=False, methods=['POST'])
    def login(self, request):
        new_data = dict()
        try:
            # DB 접근할 cursor
            cursor = connection.cursor()

            # POST 메소드로 날라온 Request의 데이터 각각 추출
            uid = request.data['uid']
            upwd = request.data['upwd']

            # SQL 쿼리문 작성
            strsql = "SELECT unickname, authority FROM skdevsec_user WHERE uid='" + uid + "' " + "and upwd='" + upwd + "'"

            # DB에 명령문 전송
            cursor.execute(strsql)
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

            # POST 메소드로 날라온 Request의 데이터 각각 추출
            unickname = request.data['unickname']

            # SQL 쿼리문 작성
            strsql = "SELECT uid, unickname, uname, umail, uphone, ucreate_date FROM skdevsec_user WHERE unickname='" + unickname + "'"

            # DB에 명령문 전송
            cursor.execute(strsql)
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
            return Response(0)

        # 읽어들인 DB 값 전송
        else:
            if new_data is not None:
                return Response(new_data)
            else:
                return Response(0)

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
            cursor.execute(strsql)
            datas = cursor.fetchall()

            # 데이터를 사용완료 했으면 DB와의 접속 종료(부하 방지)
            connection.commit()
            connection.close()

        # 에러가 발생했을 경우 에러 내용 출력
        except Exception as e:
            connection.rollback()
            print(e)
            return Response(0)

        # 데이터가 존재하면(중복이면) 1을 전송 아니면 0을 전송
        else:
            if datas is not None:
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

            # POST 메소드로 날라온 Request의 데이터 각각 추출
            uid = request.data['uid']
            unickname = request.data['unickname']
            umail = request.data['umail']
            uphone = request.data['uphone']

            # SQL 쿼리문 작성
            strsql = "UPDATE skdevsec_user SET unickname='" + unickname + "', " + "umail='" + umail + "', " + "uphone='" + uphone + "' WHERE uid='" + uid + "'"

            # DB에 명령문 전송
            cursor.execute(strsql)

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

            # POST 메소드로 날라온 Request의 데이터 각각 추출
            unickname = request.data['unickname']
            upwd = request.data['upwd']

            # SQL 쿼리문 작성
            strsql = "UPDATE skdevsec_user SET upwd='" + upwd + "' WHERE unickname='" + unickname + "'"

            # DB에 명령문 전송
            cursor.execute(strsql)

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
    def board_output(self, request):
        new_data = list()

        try:
            # DB 접근할 cursor
            cursor = connection.cursor()

            # POST 메소드로 날라온 Request의 데이터 각각 추출
            bcate = request.data['bcate']
            bpage = request.data['bpage']
            bpage = int(bpage)

            # SQL 쿼리문 작성
            strsql1 = "SELECT COUNT(*) FROM skdevsec_board WHERE bcate='" + bcate + "'"

            # DB에 명령문 전송
            cursor.execute(strsql1)
            datas = cursor.fetchone()

            new_data.append({"board_count": datas[0]})

            # SQL 쿼리문 작성
            strsql = "SELECT bid, btitle ,bfile, bview, bcomment, unickname, bcreate_date, b_lock FROM skdevsec_board where bcate='" + bcate + "' order by bid desc limit " + str(bpage * 10 - 10) + ", 10"

            # DB에 명령문 전송
            cursor.execute(strsql)
            datas = cursor.fetchone()

            # 데이터를 사용완료 했으면 DB와의 접속 종료(부하 방지)
            connection.commit()
            connection.close()

            # 게시판 정보를 보내기 위한 대입 로직 구현
            if datas is not None:
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
            else:
                return Response(0)

        # 에러가 발생했을 경우 에러 내용 출력
        except Exception as e:
            connection.rollback()
            print(e)
            return Response(0)

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

            # POST 메소드로 날라온 Request의 데이터 각각 추출
            bid = request.data['bid']
            # SQL 쿼리문 작성
            strsql1 = "UPDATE skdevsec_board SET bview = bview+1 WHERE bid='" + bid + "'"
            strsql2 = "SELECT * FROM skdevsec_board WHERE bid='" + bid + "'"

            # DB에 명령문 전송
            cursor.execute(strsql1)

            # DB에 명령문 전송
            cursor.execute(strsql2)
            datas = cursor.fetchall()

            # 데이터를 사용완료 했으면 DB와의 접속 종료(부하 방지)
            connection.commit()
            connection.close()

            # 게시물 정보 대입
            for data in datas:
                new_data['bid'] = data[0]
                new_data['btitle'] = data[1]
                new_data['btext'] = data[2]
                new_data['bfile'] = data[3]
                new_data['bview'] = data[4]
                new_data['bcomment'] = data[5]
                new_data['unickname'] = data[6]
                new_data['bcreate_date'] = data[7]
                new_data['b_lock'] = data[8]

        # 에러가 발생했을 경우 에러 내용 출력
        except Exception as e:
            connection.rollback()
            print(e)
            return Response(0)

        # 성공 했을 시, 데이터 전송
        else:
            if new_data is not None:
                return Response(new_data)
            else:
                return Response(0)

    # sql 인젝션 되는 코드
    # 게시물 등록
    @action(detail=False, methods=['POST'])
    def board_upload(self, request):
        new_data = dict()
        try:
            # POST 메소드로 날라온 Request의 데이터 각각 추출
            new_data['btitle'] = request.data['btitle']
            new_data['btext'] = request.data['btext']
            new_data['bfile'] = request.data['bfile']
            new_data['bview'] = request.data['bview']
            new_data['bcomment'] = request.data['bcomment']
            new_data['unickname'] = request.data['unickname']
            new_data['bcreate_date'] = request.data['bcreate_date']
            new_data['bcate'] = request.data['bcate']
            new_data['b_lock'] = request.data['b_lock']

            if new_data['bfile']=="0":
                # DB 접근할 cursor
                cursor = connection.cursor()

                # SQL 쿼리문 작성
                strsql = "INSERT INTO skdevsec_board(btitle, btext, bfile, bview, bcomment, unickname, bcreate_date, bcate, b_lock) VALUES('" + new_data['btitle'] + "', '" + new_data['btext'] + "', '" + new_data['bfile'] + "', '" + new_data['bview'] + "', '" + new_data['bcomment'] + "', '" + new_data['unickname'] + "', '" + new_data['bcreate_date'] + "', '" + new_data['bcate'] + "', '" + new_data['b_lock'] + "')"

                # DB에 명령문 전송
                cursor.execute(strsql)

                # 데이터를 사용완료 했으면 DB와의 접속 종료(부하 방지)
                connection.commit()
                connection.close()

            else:
                # DB에 저장하기 위해 시리얼라이저 함수 사용
                file_serializer = SkdevsecBoardSerializer(data=new_data)

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
        new_data = dict()
        try:
            # DB 접근할 cursor
            cursor = connection.cursor()

            # 수정할 게시물 번호를 받아서 해당 DB를 저장
            data_check = SkdevsecBoard.objects.get(bid=request.data['bid'])

            # POST 메소드로 날라온 Request의 데이터 각각 추출
            bid = request.data['bid']
            new_data['btitle'] = request.data['btitle']
            new_data['btext'] = request.data['btext']
            new_data['bfile'] = request.data['bfile']
            new_data['bview'] = request.data['bview']
            new_data['bcomment'] = request.data['bcomment']
            new_data['unickname'] = request.data['unickname']
            new_data['bcreate_date'] = request.data['bcreate_date']
            new_data['bcate'] = request.data['bcate']
            new_data['b_lock'] = request.data['b_lock']

            # SQL 쿼리문 작성
            strsql1 = "SELECT bfile FROM skdevsec_board WHERE bid='" + bid + "'"

            # DB에 명령문 전송
            cursor.execute(strsql1)
            datas = cursor.fetchall()

            # 파일 삭제
            os.remove(datas[0][0])

            # DB에 저장하기 위해 시리얼라이저 함수 사용
            file_serializer = SkdevsecBoardSerializer(data_check, data=new_data)

            # 수정할 데이터를 업데이트함
            if file_serializer.is_valid():
                file_serializer.update(data_check, file_serializer.validated_data)
            else:
                print("문제 생김")
                return Response(0)

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

            # POST 메소드로 날라온 Request의 데이터 각각 추출
            bid = request.data['bid']

            # SQL 쿼리문 작성
            strsql1 = "SELECT bfile FROM skdevsec_board WHERE bid='" + bid + "'"
            strsql2 = "DELETE FROM skdevsec_board WHERE bid='" + bid + "'"

            # DB에 명령문 전송
            cursor.execute(strsql1)
            datas = cursor.fetchall()

            # 파일 삭제
            if datas is not None:
                os.remove(datas[0][0])

            # DB에 명령문 전송
            cursor.execute(strsql2)

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

            # POST 메소드로 날라온 Request의 데이터 각각 추출
            bid = request.data['bid']

            # SQL 쿼리문 작성
            strsql1 = "SELECT bfile FROM skdevsec_board WHERE bid='" + bid + "'"
            strsql2 = "UPDATE skdevsec_board SET bfile=0 WHERE bid='" + bid + "'"

            # DB에 명령문 전송
            cursor.execute(strsql1)
            datas = cursor.fetchall()

            # 파일 삭제
            if datas is not None:
                os.remove(datas[0][0])

            # DB에 명령문 전송
            cursor.execute(strsql2)

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

            # POST 메소드로 날라온 Request의 데이터 각각 추출
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
            cursor.execute(strsql)
            datas = cursor.fetchone()

            # 데이터를 사용완료 했으면 DB와의 접속 종료(부하 방지)
            connection.commit()
            connection.close()

            # 게시판 정보를 보내기 위한 대입 로직 구현
            if datas is not None:
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
            else:
                return Response(0)

        # 에러가 발생했을 경우 에러 내용 출력
        except Exception as e:
            connection.rollback()
            print(e)
            return  Response(0)

        # 성공 했을 시, 데이터 전송
        else:
            return Response(new_data)


# 댓글 관련 테이블
# 댓글 출력, 댓글 작성, 댓글 삭제
class SkdevsecCommentViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = SkdevsecComment.objects.all()
    serializer_class = SkdevsecCommentSerializer

    # sql 인젝션 되는 코드
    # 댓글 출력
    @action(detail=False, methods=['POST'])
    def view_comment(self, request):
        new_data = list()
        try:
            # DB 접근할 cursor
            cursor = connection.cursor()

            # POST 메소드로 날라온 Request의 데이터 각각 추출
            bid = request.data['bid']
            cpage = request.data['cpage']
            cpage = int(cpage)

            # SQL 쿼리문 작성
            strsql1 = "SELECT COUNT(*) FROM skdevsec_comment WHERE bid='" + bid + "'"

            # DB에 명령문 전송
            cursor.execute(strsql1)
            datas = cursor.fetchone()

            new_data.append({"comment_count": datas[0]})

            # SQL 쿼리문 작성
            strsql = "SELECT cid, unickname, ctext, ccreate_date, clock FROM skdevsec_comment where bid='" + bid + "' order by cid LIMIT " + str(cpage * 10 - 10) + " , 10"

            # DB에 명령문 전송
            cursor.execute(strsql)
            datas = cursor.fetchone()

            # 데이터를 사용완료 했으면 DB와의 접속 종료(부하 방지)
            connection.commit()
            connection.close()

            # 댓글 정보를 보내기 위한 대입 로직 구현
            if datas is not None:
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
                return Response(0)

        # 에러가 발생했을 경우 에러 내용 출력
        except Exception as e:
            connection.rollback()
            print(e)
            return Response(0)

        # 성공 했을 시, 데이터 전송
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
            bid = request.data['bid']
            unickname = request.data['unickname']
            ctext = request.data['ctext']
            ccreate_date = request.data['ccreate_date']
            clock = request.data['clock']

            # SQL 쿼리문 작성
            strsql = "INSERT INTO skdevsec_comment(bid, unickname, ctext, ccreate_date, clock) VALUES('" + bid + "', '" + unickname + "', '" + ctext + "', '" + ccreate_date + "', '" + clock + "')"

            # DB에 명령문 전송
            cursor.execute(strsql)

            # SQL 쿼리문 작성
            strsql1 = "UPDATE skdevsec_board SET bcomment=bcomment+1 WHERE bid='" + bid + "'"

            # DB에 명령문 전송
            cursor.execute(strsql1)

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
            strsql1 = "DELETE FROM skdevsec_comment WHERE cid='" + cid + "'"

            # DB에 명령문 전송
            cursor.execute(strsql1)

            # SQL 쿼리문 작성
            strsql1 = "UPDATE skdevsec_board SET bcomment=bcomment-1 WHERE bid='" + bid + "'"

            # DB에 명령문 전송
            cursor.execute(strsql1)

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


# 장바구니 테이블
# 장바구니 목록 출력, 장바구니 목록 삭제, 장바구니 비우기
class SkdevsecBagViewSet(viewsets.ReadOnlyModelViewSet):
    # 테이블 출력을 위한 최소 코드
    queryset = SkdevsecBag.objects.all()
    serializer_class = SkdevsecBagSerializer

    # sql 인젝션 되는 코드
    # 장바구니 목록 출력
    @action(detail=False, methods=['POST'])
    def bag_show(self, request):
        new_data = list()
        try:
            # DB 접근할 cursor
            cursor = connection.cursor()

            # POST 메소드로 날라온 Request의 데이터 각각 추출
            uid = request.data['uid']

            # SQL 쿼리문 작성
            strsql = "SELECT bag_id, pid FROM skdevsec_bag where uid='" + uid + "'"

            # DB에 명령문 전송
            cursor.execute(strsql)
            datas = cursor.fetchall()

            # 장바구니 목록이 있으면
            if datas is not None:
                for data in datas:
                    new_data_in = dict()
                    strsql = "SELECT pname, pcate, pimage, ptext, pprice FROM skdevsec_product WHERE pid='" + str(data[1]) + "'"
                    cursor.execute(strsql)
                    products = cursor.fetchone()
                    print(products)
                    # 상품 정보를 보내기 위한 대입 로직 구현
                    if products is not None:
                        new_data_in['bag_id'] = data[0]
                        new_data_in['pname'] = products[0]
                        new_data_in['pcate'] = products[1]
                        new_data_in['pimage'] = products[2]
                        new_data_in['ptext'] = products[3]
                        new_data_in['pprice'] = products[4]
                        new_data.append(new_data_in)
                    else:
                        Response(0)

                # 데이터를 사용완료 했으면 DB와의 접속 종료(부하 방지)
                connection.commit()
                connection.close()

            # 장바구니 목록이 없으면 0 전송
            else:
                # 데이터를 사용완료 했으면 DB와의 접속 종료(부하 방지)
                connection.commit()
                connection.close()
                return Response(0)

        # 에러가 발생했을 경우 에러 내용 출력
        except Exception as e:
            connection.rollback()
            print(e)
            return Response(0)

        # 성공 했을 시, 데이터 전송
        else:
            return Response(new_data)

    # sql 인젝션 되는 코드
    # 장바구니 목록 삭제
    @action(detail=False, methods=['POST'])
    def bag_delete(self, request):
        try:
            # DB 접근할 cursor
            cursor = connection.cursor()

            # POST 메소드로 날라온 Request의 데이터 각각 추출
            bag_id = request.data['bag_id']

            # SQL 쿼리문 작성
            strsql1 = "DELETE FROM skdevsec_bag WHERE bag_id='" + bag_id + "'"

            # DB에 명령문 전송
            cursor.execute(strsql1)

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
    # 장바구니 비우기
    @action(detail=False, methods=['POST'])
    def bag_delete_all(self, request):
        try:
            # DB 접근할 cursor
            cursor = connection.cursor()

            # POST 메소드로 날라온 Request의 데이터 각각 추출
            uid = request.data['uid']

            # SQL 쿼리문 작성
            strsql1 = "DELETE FROM skdevsec_bag WHERE uid='" + uid + "'"

            # DB에 명령문 전송
            cursor.execute(strsql1)

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


# 상품 관련 테이블
# 상품 리스트 출력, 상품 상세 페이지 출력, 상품 등록, 상품 수정, 상품 삭제
class SkdevsecProductViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = SkdevsecProduct.objects.all()
    serializer_class = SkdevsecProductSerializer

    # sql 인젝션 되는 코드
    # 상품 리스트 출력
    @action(detail=False, methods=['POST'])
    def product_output(self, request):
        new_data = list()
        try:
            # DB 접근할 cursor
            cursor = connection.cursor()

            # POST 메소드로 날라온 Request의 데이터 각각 추출
            pcate = request.data['pcate']
            ppage = int(request.data['ppage'])

            # SQL 쿼리문 작성
            strsql1 = "SELECT COUNT(*) FROM skdevsec_product WHERE pcate='" + pcate + "'"

            # DB에 명령문 전송
            cursor.execute(strsql1)
            datas = cursor.fetchone()

            if datas is not None:
                new_data.append({"product_count": datas[0]})

            # SQL 쿼리문 작성
            strsql = "SELECT * FROM skdevsec_product where pcate='" + pcate + "' order by pid desc limit " + str(ppage * 10 - 10) + ", 10"

            # DB에 명령문 전송
            cursor.execute(strsql)
            datas = cursor.fetchone()

            # 데이터를 사용완료 했으면 DB와의 접속 종료(부하 방지)
            connection.commit()
            connection.close()

            # 게시판 정보를 보내기 위한 대입 로직 구현
            if datas is not None:
                while datas:
                    new_data_in = dict()
                    new_data_in['pid'] = datas[0]
                    new_data_in['pname'] = datas[1]
                    new_data_in['pcate'] = datas[2]
                    new_data_in['pimage'] = datas[3]
                    new_data_in['ptext'] = datas[4]
                    new_data_in['pprice'] = datas[5]
                    new_data_in['pcreate_date'] = datas[6]
                    new_data_in['preview'] = datas[7]
                    new_data_in['preview_avg'] = datas[8]
                    new_data_in['pcount'] = datas[9]
                    new_data.append(new_data_in)
                    datas = cursor.fetchone()
            else:
                return Response(0)

            # 에러가 발생했을 경우 에러 내용 출력
        except Exception as e:
            connection.rollback()
            print(e)
            return Response(0)

        # 성공 했을 시, 데이터 전송
        else:
            return Response(new_data)

    # sql 인젝션 되는 코드
    # 상품상세 페이지 출력
    @action(detail=False, methods=['POST'])
    def product_inside(self, request):
        new_data = list()
        try:
            # DB 접근할 cursor
            cursor = connection.cursor()

            # POST 메소드로 날라온 Request의 데이터 각각 추출
            pid = request.data['pid']

            # SQL 쿼리문 작성
            strsql = "SELECT * FROM skdevsec_product WHERE pid='" + pid + "'"

            # DB에 명령문 전송
            cursor.execute(strsql)
            datas = cursor.fetchone()

            # 데이터를 사용완료 했으면 DB와의 접속 종료(부하 방지)
            connection.commit()
            connection.close()

            # 게시판 정보를 보내기 위한 대입 로직 구현
            if datas is not None:
                while datas:
                    new_data_in = dict()
                    new_data_in['pid'] = datas[0]
                    new_data_in['pname'] = datas[1]
                    new_data_in['pcate'] = datas[2]
                    new_data_in['pimage'] = datas[3]
                    new_data_in['ptext'] = datas[4]
                    new_data_in['pprice'] = datas[5]
                    new_data_in['pcreate_date'] = datas[6]
                    new_data_in['preview'] = datas[7]
                    new_data_in['preview_avg'] = datas[8]
                    new_data_in['pcount'] = datas[9]
                    new_data.append(new_data_in)
                    datas = cursor.fetchone()
            else:
                return Response(0)

        # 에러가 발생했을 경우 에러 내용 출력
        except Exception as e:
            connection.rollback()
            print(e)
            return  Response(0)

        # 성공 했을 시, 데이터 전송
        else:
            return Response(new_data)

    # sql 인젝션 되는 코드
    # 상품 등록
    @action(detail=False, methods=['POST'])
    def product_upload(self, request):
        new_data = dict()
        try:
            # POST 메소드로 날라온 Request의 데이터 각각 추출
            new_data['pname'] = request.data['pname']
            new_data['pcate'] = request.data['pcate']
            new_data['pimage'] = request.data['pimage']
            new_data['ptext'] = request.data['ptext']
            new_data['pprice'] = request.data['pprice']
            new_data['pcreate_date'] = request.data['pcreate_date']
            new_data['preview'] = request.data['preview']
            new_data['preview_avg'] = request.data['preview_avg']
            new_data['pcount'] = request.data['pcount']

            # DB에 저장하기 위해 시리얼라이저 함수 사용
            file_serializer = SkdevsecProductSerializer(data=new_data)

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
    # 상품 수정
    @action(detail=False, methods=['POST'])
    def change_product(self, request):
        new_data = dict()
        try:
            # DB 접근할 cursor
            cursor = connection.cursor()

            # 수정할 게시물 번호를 받아서 해당 DB를 저장
            data_check = SkdevsecProduct.objects.get(pid=request.data['pid'])

            # POST 메소드로 날라온 Request의 데이터 각각 추출
            pid = request.data['pid']
            new_data['pname'] = request.data['pname']
            new_data['pcate'] = request.data['pcate']
            new_data['pimage'] = request.data['pimage']
            new_data['ptext'] = request.data['ptext']
            new_data['pprice'] = request.data['pprice']
            new_data['pcreate_date'] = request.data['pcreate_date']
            new_data['preview'] = request.data['preview']
            new_data['preview_avg'] = request.data['preview_avg']
            new_data['pcount'] = request.data['pcount']

            # SQL 쿼리문 작성
            strsql1 = "SELECT pimage FROM skdevsec_product WHERE pid='" + pid + "'"

            # DB에 명령문 전송
            cursor.execute(strsql1)
            datas = cursor.fetchall()

            # 파일 삭제
            if datas is None:
                os.remove(datas[0][0])

            # DB에 저장하기 위해 시리얼라이저 함수 사용
            file_serializer = SkdevsecBoardSerializer(data_check, data=new_data)

            # 수정할 데이터를 업데이트함
            if file_serializer.is_valid():
                file_serializer.update(data_check, file_serializer.validated_data)
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
    # 상품 삭제
    @action(detail=False, methods=['POST'])
    def product_delete(self, request):
        try:
            # DB 접근할 cursor
            cursor = connection.cursor()

            # POST 메소드로 날라온 Request의 데이터 각각 추출
            pid = request.data['pid']

            # SQL 쿼리문 작성
            strsql1 = "SELECT pimage FROM skdevsec_product WHERE pid='" + pid + "'"
            strsql2 = "DELETE FROM skdevsec_product WHERE pid='" + pid + "'"

            # DB에 명령문 전송
            cursor.execute(strsql1)
            datas = cursor.fetchall()

            # 파일 삭제
            os.remove(datas[0][0])

            # DB에 명령문 전송
            cursor.execute(strsql2)

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
    # 상품 검색
    @action(detail=False, methods=['POST'])
    def product_search(self, request):
        new_data = list()
        try:
            # DB 접근할 cursor
            cursor = connection.cursor()

            # POST 메소드로 날라온 Request의 데이터 각각 추출
            pcode = request.data['pcode']
            psearch = request.data['psearch']
            pcode = int(pcode)

            # 검색 조건 코드 분류
            # 전체 0, 상품 명 1, 카테고리 2, 평점 이상 3
            if pcode == 0:
                # SQL 쿼리문 작성
                strsql = "SELECT pid, pcate, pimage, pname, pprice, preview, preview_avg FROM skdevsec_product WHERE (pname LIKE '%" + psearch + "%' OR pcate='" + psearch + "' OR preview > '" + psearch + "')"
            elif pcode == 1:
                strsql = "SELECT pid, pcate, pimage, pname, pprice, preview, preview_avg FROM skdevsec_product WHERE (pname LIKE '%" + psearch + "%')"
            elif pcode == 2:
                strsql = "SELECT pid, pcate, pimage, pname, pprice, preview, preview_avg FROM skdevsec_product WHERE (pcate='" + psearch + "')"
            elif pcode == 3:
                strsql = "SELECT pid, pcate, pimage, pname, pprice, preview, preview_avg FROM skdevsec_product WHERE (preview > '" + psearch + "')"
            else:
                return Response("코드 값 잘못 보냄!!")

            # DB에 명령문 전송
            cursor.execute(strsql)
            datas = cursor.fetchone()

            # 데이터를 사용완료 했으면 DB와의 접속 종료(부하 방지)
            connection.commit()
            connection.close()

            # 게시판 정보를 보내기 위한 대입 로직 구현
            if datas is not None:
                while datas:
                    new_data_in = dict()
                    new_data_in['pid'] = datas[0]
                    new_data_in['pcate'] = datas[1]
                    new_data_in['pimage'] = datas[2]
                    new_data_in['pname'] = datas[3]
                    new_data_in['pprice'] = datas[4]
                    new_data_in['preview'] = datas[5]
                    new_data_in['preview_avg'] = datas[6]
                    new_data.append(new_data_in)
                    datas = cursor.fetchone()
            else:
                return Response(0)

        # 에러가 발생했을 경우 에러 내용 출력
        except Exception as e:
            connection.rollback()
            print(e)
            return Response(0)

        # 성공 했을 시, 데이터 전송
        else:
            return Response(new_data)


# 상품 리뷰 관련 테이블
# 리뷰 출력, 리뷰 등록, 리뷰 삭제
class SkdevsecReviewViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = SkdevsecReview.objects.all()
    serializer_class = SkdevsecReviewSerializer

    # sql 인젝션 되는 코드
    # 리뷰 출력
    @action(detail=False, methods=['POST'])
    def review_output(self, request):
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

            # 데이터를 사용완료 했으면 DB와의 접속 종료(부하 방지)
            connection.commit()
            connection.close()

            # 댓글 정보를 보내기 위한 대입 로직 구현
            if datas is not None:
                while datas:
                    new_data_in = dict()
                    new_data_in['rid'] = datas[0]
                    new_data_in['rstar'] = datas[1]
                    new_data_in['unickname'] = datas[2]
                    new_data_in['rcreate_date'] = datas[3]
                    new_data.append(new_data_in)
                    datas = cursor.fetchone()
            else:
                return Response(0)

        # 에러가 발생했을 경우 에러 내용 출력
        except Exception as e:
            connection.rollback()
            print(e)
            return Response(0)

        # 성공 했을 시, 데이터 전송
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
            strsql1 = "DELETE FROM skdevsec_review WHERE rid='" + rid + "'"

            # DB에 명령문 전송
            cursor.execute(strsql1)

            # SQL 쿼리문 작성
            strsql2 = "UPDATE skdevsec_product SET preview = (SELECT COUNT(*) FROM skdevsec_review WHERE pid='" + pid + "'), preview_avg =(SELECT round(avg(rstar),1) FROM skdevsec_review WHERE pid='" + pid + "')  WHERE pid='" + pid + "'"

            # DB에 명령문 전송
            cursor.execute(strsql2)

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


# 결제 테이블
# 결제 정보 등록
class SkdevsecOrderuserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = SkdevsecOrderuser.objects.all()
    serializer_class = SkdevsecOrderuserSerializer

    # sql 인젝션 되는 코드
    # 결제 정보 등록
    @action(detail=False, methods=['POST'])
    def review_output(self, request):
        try:
            # DB 접근할 cursor
            cursor = connection.cursor()

            # POST 메소드로 날라온 Request의 데이터 각각 추출
            uid = request.data['uid']
            oname = request.data['oname']
            ophone = request.data['ophone']
            oaddress = request.data['oaddress']
            order_date = request.data['order_date']
            oprice = request.data['oprice']

            # SQL 쿼리문 작성
            strsql = "INSERT INTO skdevsec_orderuser(uid, oname, ophone, oaddress, order_date, oprice) VALUES('" + uid + "', '" + oname + "', '" + ophone + "', '" + oaddress + "', '" + order_date + "', '" + oprice + "')"
            # DB에 명령문 전송
            cursor.execute(strsql)

            # 데이터를 사용완료 했으면 DB와의 접속 종료(부하 방지)
            connection.commit()
            connection.close()

        # 에러가 발생했을 경우 에러 내용 출력
        except Exception as e:
            connection.rollback()
            print(e)
            return Response(0)

        # 성공 했을 시, 데이터 전송
        else:
            return Response(1)


# 결제 기록 테이블
class SkdevsecOrderproductViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = SkdevsecOrderproduct.objects.all()
    serializer_class = SkdevsecOrderproductSerializer
