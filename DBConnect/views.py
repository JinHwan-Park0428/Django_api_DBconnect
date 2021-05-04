# 필요한 모듈 임포트
import os
from random import *
from django.core.mail import send_mail
from django.db import connection
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from DBConnect.serializers import *
from DBtest.settings import EMAIL_HOST_USER
from . import sms_send
import requests
import json


# 각각의 클래스는 필요한 기능에 따른 SQL 쿼리문을 작성할 것
# 각각의 클래스의 함수에 접근 하기 위한 주소 예시
# ex) http://localhost:8000/테이블명/함수명/
# ex) http://localhost:8000/SkdevsecUser/create_user/

# 회원 정보 관련 테이블
# 회원 가입, 아이디 중복 체크, 닉네임 중복 체크, 이메일 중복 체크 및 인증 메일 전송, 로그인, 내 정보 보기, 회원 정보 수정 전 인증
# 내 정보 수정하기, 비밀번호 변경, 회원 탈퇴, 회원 정보 출력, 회원 정보 검색
class SkdevsecUserViewSet(viewsets.ReadOnlyModelViewSet):
    # 테이블 출력을 위한 최소 코드
    queryset = SkdevsecUser.objects.all()
    serializer_class = SkdevsecUserSerializer

    # 관리자 권한 요구 코드
    # permission_classes = [permissions.IsAuthenticated]

    # sql 인젝션 되는 코드
    # 관리자 페이지 (회원 정보 보기)
    @action(detail=False, methods=['POST'])
    def admin_user_info(self, request):
        # 권한이 1 이고 닉네임이 admin일 시
        if request.data['authority'] == '1' and request.data['unickname'] == 'admin':
            # 데이터 저장을 위한 리스트 선언
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

                # 전체 유저 수를 저장
                new_data.append({"user_count": datas[0]})

                # SQL 쿼리문 작성
                strsql = "SELECT * FROM skdevsec_user order by ucreate_date desc limit " + str(upage * 10 - 10) + ", 10"

                # DB에 명령문 전송
                cursor.execute(strsql)
                datas = cursor.fetchone()

                # 데이터가 존재 한다면
                if len(datas) != 0:
                    # 데이터 갯수 만큼 반복
                    # 데이터를 딕셔너리 형태로 저장 후, 리스트에 추가
                    while datas:
                        new_data_in = dict()
                        new_data_in['uid'] = datas[0]
                        # new_data_in['upwd'] = datas[1]
                        new_data_in['unickname'] = datas[2]
                        new_data_in['uname'] = datas[3]
                        new_data_in['umail'] = datas[4]
                        new_data_in['uphone'] = datas[5]
                        new_data_in['ucreate_date'] = datas[6]
                        new_data_in['authority'] = datas[7]
                        new_data.append(new_data_in)
                        datas = cursor.fetchone()
                # 데이터가 존재 하지 않는 다면
                else:
                    # DB와 접속 종료 후 프론트엔드에 0 전송
                    connection.commit()
                    connection.close()
                    return Response(0)

                # DB와 접속 종료
                connection.commit()
                connection.close()

            # 에러가 발생했을 경우 백엔드에 에러 출력 및 프론트엔드에 0 전송
            except Exception as e:
                connection.rollback()
                print(f"admin_user_info 에러: {e}")
                return Response(0)

            # 데이터 처리가 끝났으면 프론트엔드에 데이터 전송
            else:
                return Response(new_data)
        # 관리자가 아니면 프론트엔드에 0 전송
        else:
            return Response(0)

    # sql 인젝션 되는 코드
    # 관리자 페이지 (회원 정보 검색)
    @action(detail=False, methods=['POST'])
    def admin_user_search(self, request):
        # 권한이 1 이고 닉네임이 admin일 시
        if request.data['authority'] == '1' and request.data['unickname'] == 'admin':
            # 데이터 저장을 위한 리스트 선언
            new_data = list()
            try:
                # POST 메소드로 날라온 Request의 데이터 각각 추출
                ucode = request.data['ucode']
                usearch = request.data['usearch']
                ucode = int(ucode)

                # DB 접근할 cursor
                cursor = connection.cursor()

                # SQL 쿼리문 작성
                # 0 : 이름 / 1 : 닉네임 / 2 : 아이디 / 3 : 이메일
                if ucode == 0:
                    strsql = "SELECT * FROM skdevsec_user where uname LIKE '%" + usearch + "%'"
                elif ucode == 1:
                    strsql = "SELECT * FROM skdevsec_user where unickname LIKE '%" + usearch + "%'"
                elif ucode == 2:
                    strsql = "SELECT * FROM skdevsec_user where uid LIKE '%" + usearch + "%'"
                elif ucode == 3:
                    strsql = "SELECT * FROM skdevsec_user where uemail LIKE '%" + usearch + "%'"
                else:
                    return Response("코드 값 잘못 보냄!!")

                # DB에 명령문 전송
                cursor.execute(strsql)
                datas = cursor.fetchone()

                # DB와 접속 종료
                connection.commit()
                connection.close()

                # 데이터가 있으면
                if len(datas) != 0:
                    # 데이터 만큼 반복
                    while datas:
                        new_data_in = dict()
                        new_data_in['uid'] = datas[0]
                        # new_data_in['upwd'] = datas[1]
                        new_data_in['unickname'] = datas[2]
                        new_data_in['uname'] = datas[3]
                        new_data_in['umail'] = datas[4]
                        new_data_in['uphone'] = datas[5]
                        new_data_in['ucreate_date'] = datas[6]
                        new_data_in['authority'] = datas[7]
                        new_data.append(new_data_in)
                        datas = cursor.fetchone()
                # 데이터가 없으면
                else:
                    # 프론트엔드에 0 전송
                    return Response(0)

            # 에러가 발생했을 경우 백엔드에 에러 내용 출력 및 프론트엔드에 0 전송
            except Exception as e:
                connection.rollback()
                print(f"admin_user_search 에러: {e}")
                return Response(0)

            # 데이터 저장 완료 시, 프론트엔드에 데이터 전송
            else:
                return Response(new_data)
        # 관리자가 아니면 프론트엔드에 0 전송
        else:
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

            # DB와 접속 종료
            connection.commit()
            connection.close()

        # 에러가 발생했을 경우 백엔드에 에러 내용 출력 및 프론트엔드에 0 전송
        except Exception as e:
            connection.rollback()
            print(f"create_user 에러: {e}")
            return Response(0)

        # 성공 했을 시, 프론트 엔드에 1 전송
        else:
            return Response(1)

    # sql 인젝션 되는 코드
    # 아이디 중복
    @action(detail=False, methods=['POST'])
    def id_check(self, request):
        try:
            # DB 접근할 cursor
            cursor = connection.cursor()

            # POST 메소드로 날라온 Request의 데이터 각각 추출
            uid = request.data['uid']

            # SQL 쿼리문 작성
            strsql = "SELECT * FROM skdevsec_user WHERE uid='" + uid + "'"

            # DB에 명령문 전송
            cursor.execute(strsql)
            datas = cursor.fetchall()

            # DB와 접속 종료
            connection.commit()
            connection.close()

        # 에러가 발생했을 경우 백엔드에 에러 내용 출력 및 프론트엔드에 0 전송
        except Exception as e:
            connection.rollback()
            print(f"id_check 에러: {e}")
            return Response(0)

        # 데이터가 존재하면(중복이면) 프론트엔드 1을 전송 아니면 0을 전송
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

            # DB와 접속 종료
            connection.commit()
            connection.close()

        # 에러가 발생했을 경우 백엔드 에러 내용 출력 및 프론트엔드에 0 전송
        except Exception as e:
            connection.rollback()
            print(f"nickname_check 에러: {e}")
            return Response(0)

        # 데이터가 존재하면(중복이면) 프론트엔드에 1을 전송 아니면 0을 전송
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

            # DB와 접속 종료
            connection.commit()
            connection.close()

        # 에러가 발생했을 경우 백엔드에 에러 내용 출력 및 프론트엔드에 0 전송
        except Exception as e:
            connection.rollback()
            print(f"email_check 에러: {e}")
            return Response(0)

        # 데이터가 존재하면(중복이면) 프론트엔드에 1을 전송 아니면 이메일 전송 작업 시작
        else:
            if len(datas) != 0:
                return Response(1)
            else:
                try:
                    # 8자리 난수를 생성해서 인증번호로서, 메일 전송
                    i = randint(10000000, 99999999)
                    # 이메일 제목
                    mail_title = "이메일 인증을 완료해주세요"
                    # 이메일 제목, 내용, 보내는 사람, 받을 사람, 옵션 순서
                    send_mail(mail_title, f"인증번호 : {i}", EMAIL_HOST_USER, [umail], fail_silently=False)
                    # 프론트 엔드에 인증번호 전송
                    return Response(i)

                # 에러가 발생했을 경우 백엔드에 에러 내용 출력 및 프론트엔드에 0 전송
                except Exception as e:
                    connection.rollback()
                    print(f"email_send 에러: {e}")
                    return Response(0)

    # sql 인젝션 되는 코드
    # 로그인
    @action(detail=False, methods=['POST'])
    def login(self, request):
        # 데이터 저장을 위한 딕셔너리 선언
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

            # DB와 접속 종료
            connection.commit()
            connection.close()

            # 불러온 데이터를 딕셔너리 형태로 저장
            for data in datas:
                new_data['unickname'] = data[0]
                new_data['authority'] = data[1]

        # 에러가 발생했을 경우 백엔드에 에러 내용 출력 및 프론트엔드에 0 전송
        except Exception as e:
            connection.rollback()
            print(f"login 에러: {e}")
            return Response(0)

        # 관리자 로그인이면 2 일반 사용자이면 1 로그인 실패면 0을 프론트엔드에 전송
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
        # 데이터 저장을 위한 딕셔너리 선언
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

            # DB와 접속 종료
            connection.commit()
            connection.close()

            # 정보를 딕셔너리 형태로 저장
            for data in datas:
                new_data['uid'] = data[0]
                new_data['unickname'] = data[1]
                new_data['uname'] = data[2]
                new_data['umail'] = data[3]
                new_data['uphone'] = data[4]
                new_data['ucreate_date'] = data[5]

        # 에러가 발생했을 경우 백엔드에 에러 내용 출력 및 프론트엔드에 0 전송
        except Exception as e:
            connection.rollback()
            print(f"view_info 에러: {e}")
            return Response(0)

        # 데이터가 있으면 프론트엔드에 데이터 전송 없으면 0 전송
        else:
            if len(new_data) != 0:
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

            # DB와 접속 종료
            connection.commit()
            connection.close()

        # 에러가 발생했을 경우 백엔드에 에러 내용 출력 및 프론트엔드에 0 전송
        except Exception as e:
            connection.rollback()
            print(f"before_change 에러: {e}")
            return Response(0)

        # 데이터가 존재하면 1, 없으면 0을 프론트엔드에 전송
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

            # POST 메소드로 날라온 Request의 데이터 각각 추출
            uid = request.data['uid']
            unickname = request.data['unickname']
            umail = request.data['umail']
            uphone = request.data['uphone']

            # SQL 쿼리문 작성
            strsql = "UPDATE skdevsec_user SET unickname='" + unickname + "', " + "umail='" + umail + "', " + "uphone='" + uphone + "' WHERE uid='" + uid + "'"

            # DB에 명령문 전송
            cursor.execute(strsql)

            # DB와 접속 종료
            connection.commit()
            connection.close()

        # 에러가 발생했을 경우 백엔드에 에러 내용 출력 및 프론트엔드에 0 전송
        except Exception as e:
            connection.rollback()
            print(f"change_info 에러: {e}")
            return Response(0)

        # 성공하면 프론트엔드에 0 전송
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

            # DB와 접속 종료
            connection.commit()
            connection.close()

        # 에러가 발생했을 경우 백엔드에 에러 내용 출력 및 프론트엔드에 0 전송
        except Exception as e:
            connection.rollback()
            print(f"change_pwd 에러: {e}")
            return Response(0)

        # 변경 완료 되면 프론트엔드에 1 전송
        else:
            return Response(1)

    # sql 인젝션 되는 코드
    # 회원 탈퇴
    @action(detail=False, methods=['POST'])
    def delete_user(self, request):
        try:
            # DB 접근할 cursor
            cursor = connection.cursor()

            # POST 메소드로 날라온 Request의 데이터 각각 추출
            unickname = request.data['unickname']

            # SQL 쿼리문 작성
            strsql = "DELETE FROM skdevsec_user WHERE unickname='" + unickname + "'"

            # DB에 명령문 전송
            cursor.execute(strsql)

            # DB와 접속 종료
            connection.commit()
            connection.close()

        # 에러가 발생했을 경우 백엔드에 에러 내용 출력 및 프론트엔드에 0 전송
        except Exception as e:
            connection.rollback()
            print(f"delete_user 에러: {e}")
            return Response(0)

        # 삭제 되면 프론트엔드에 1 전송
        else:
            return Response(1)


# 게시판 관련 테이블
# 게시판 출력, 게시물 상세 보기, 게시물 등록, 게시물 수정, 게시물 삭제, 파일 삭제, 게시물 검색, 내 게시물 보기(마이페이지)
class SkdevsecBoardViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = SkdevsecBoard.objects.all()
    serializer_class = SkdevsecBoardSerializer

    # sql 인젝션 되는 코드
    # 게시판 출력
    @action(detail=False, methods=['POST'])
    def board_output(self, request):
        # 데이터 저장을 위한 리스트 선언
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

            # 게시물 갯수 저장
            new_data.append({"board_count": datas[0]})

            # SQL 쿼리문 작성
            strsql = "SELECT bid, btitle ,bfile, bview, bcomment, unickname, bcreate_date, b_lock FROM skdevsec_board where bcate='" + bcate + "' order by bid desc limit " + str(
                bpage * 10 - 10) + ", 10"

            # DB에 명령문 전송
            cursor.execute(strsql)
            datas = cursor.fetchone()

            # 데이터가 있으면
            if len(datas) != 0:
                # 있는 만큼 반복
                while datas:
                    # 게시물 정보를 딕셔너리에 저장 후 리스트에 추가
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
            # 데이터가 없으면
            else:
                # DB와 접속 종료 및 프론트엔드에 0 전송
                connection.commit()
                connection.close()
                return Response(0)

            # DB와 접속 종료
            connection.commit()
            connection.close()

        # 에러가 발생했을 경우 백엔드에 에러 내용 출력 및 프론트엔드에 0 전송
        except Exception as e:
            connection.rollback()
            print(f"board_output 에러: {e}")
            return Response(0)

        # 데이터가 저장 됐으면, 프론트엔드에 데이터 전송
        else:
            return Response(new_data)

    # sql 인젝션 되는 코드
    # 게시물 상세 보기
    @action(detail=False, methods=['POST'])
    def board_inside(self, request):
        # 데이터 저장을 위한 딕셔너리 선언
        new_data = dict()
        try:
            # DB 접근할 cursor
            cursor = connection.cursor()

            # POST 메소드로 날라온 Request의 데이터 각각 추출
            bid = request.data['bid']

            # SQL 쿼리문 작성
            strsql1 = "UPDATE skdevsec_board SET bview = bview+1 WHERE bid='" + bid + "'"

            # DB에 명령문 전송
            cursor.execute(strsql1)

            # SQL 쿼리문 작성
            strsql2 = "SELECT * FROM skdevsec_board WHERE bid='" + bid + "'"

            # DB에 명령문 전송
            cursor.execute(strsql2)
            datas = cursor.fetchall()

            # DB와 접속 종료
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

        # 에러가 발생했을 경우 백엔드에 에러 내용 출력 및 프론트엔드에 0 전송
        except Exception as e:
            connection.rollback()
            print(f"board_inside 에러: {e}")
            return Response(0)

        # 데이터를 저장했으면, 프론트엔드에 데이터 전송
        else:
            if len(new_data) != 0:
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

            # 업로드할 파일이 없으면
            if new_data['bfile'] == "0":
                # DB 접근할 cursor
                cursor = connection.cursor()

                # SQL 쿼리문 작성
                strsql = "INSERT INTO skdevsec_board(btitle, btext, bfile, bview, bcomment, unickname, bcreate_date, bcate, b_lock) VALUES('" + \
                         new_data['btitle'] + "', '" + new_data['btext'] + "', '" + new_data['bfile'] + "', '" + \
                         new_data['bview'] + "', '" + new_data['bcomment'] + "', '" + new_data['unickname'] + "', '" + \
                         new_data['bcreate_date'] + "', '" + new_data['bcate'] + "', '" + new_data['b_lock'] + "')"

                # DB에 명령문 전송
                cursor.execute(strsql)

                # DB와 접속 종료
                connection.commit()
                connection.close()
            # 업로드할 파일이 있으면
            else:
                # DB에 저장하기 위해 시리얼라이저 함수 사용
                file_serializer = SkdevsecBoardSerializer(data=new_data)

                # 저장이 가능한 상태면 저장
                if file_serializer.is_valid():
                    file_serializer.save()
                # 저장이 불가능하면 백엔드에 에러 알림 및 프론트엔드에 0 전송
                else:
                    print("serializer 에러")
                    return Response(0)

        # 에러가 발생했을 경우 백엔드에 에러 내용 출력 및 프론트엔드에 0 전송
        except Exception as e:
            connection.rollback()
            print(f"board_upload 에러: {e}")
            return Response(0)

        # 성공 했을 시, 프론트엔드에 1 전송
        else:
            return Response(1)

    # sql 인젝션 되는 코드
    # 게시물 수정
    @action(detail=False, methods=['POST'])
    def change_board(self, request):
        # 데이터 저장을 위한 딕셔너리 선언
        new_data = dict()
        new_data1 = dict()
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
            strsql = "SELECT bfile FROM skdevsec_board WHERE bid='" + bid + "'"

            # DB에 명령문 전송
            cursor.execute(strsql)
            datas = cursor.fetchall()

            # 게시물 기존 파일이 존재하면 삭제
            if datas[0][0] != "0":
                os.remove(datas[0][0])

            # DB에 저장하기 위해 시리얼라이저 함수 사용
            file_serializer = SkdevsecBoardSerializer(data_check, data=new_data)

            # 수정할 데이터를 업데이트함
            if file_serializer.is_valid():
                file_serializer.update(data_check, file_serializer.validated_data)
            # 업데이트 불가능하면 백엔드에 에러 알림 및 프론트엔드에 0 전송
            else:
                print("serializer 에러")
                return Response(0)

            # SQL 쿼리문 작성
            strsql1 = "SELECT * FROM skdevsec_board WHERE bid='" + bid + "'"

            # DB에 명령문 전송
            cursor.execute(strsql1)
            datas = cursor.fetchall()

            # DB와 접속 종료
            connection.commit()
            connection.close()

            # 게시물 정보 대입
            for data in datas:
                new_data1['bid'] = data[0]
                new_data1['btitle'] = data[1]
                new_data1['btext'] = data[2]
                new_data1['bfile'] = data[3]
                new_data1['bview'] = data[4]
                new_data1['bcomment'] = data[5]
                new_data1['unickname'] = data[6]
                new_data1['bcreate_date'] = data[7]
                new_data1['b_lock'] = data[8]

        # 에러가 발생했을 경우 벡엔드에 에러 내용 출력 및 프론트엔드에 0 전송
        except Exception as e:
            connection.rollback()
            print(f"change_board 에러: {e}")
            return Response(0)

        # 수정된 게시물 정보를 프론트엔드에 전송
        else:
            return Response(new_data1)

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
            strsql = "SELECT bfile FROM skdevsec_board WHERE bid='" + bid + "'"

            # DB에 명령문 전송
            cursor.execute(strsql)
            datas = cursor.fetchall()

            # 파일이 존재하면 삭제
            if datas[0][0] != "0":
                os.remove(datas[0][0])

            # SQL 쿼리문 작성
            strsql1 = "DELETE FROM skdevsec_board WHERE bid='" + bid + "'"

            # DB에 명령문 전송
            cursor.execute(strsql1)

            # DB와 접속 종료
            connection.commit()
            connection.close()

        # 에러가 발생했을 경우 백엔드에 에러 내용 출력 및 프론트엔드에 0 전송
        except Exception as e:
            connection.rollback()
            print(f"board_delete 에러: {e}")
            return Response(0)

        # 삭제되면, 프론트엔드에 1 전송
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
            strsql = "SELECT bfile FROM skdevsec_board WHERE bid='" + bid + "'"

            # DB에 명령문 전송
            cursor.execute(strsql)
            datas = cursor.fetchall()

            # 파일 삭제
            if datas[0][0] != "0":
                os.remove(datas[0][0])

            # SQL 쿼리문 작성
            strsql1 = "UPDATE skdevsec_board SET bfile=0 WHERE bid='" + bid + "'"

            # DB에 명령문 전송
            cursor.execute(strsql1)

            # DB와 접속 종료
            connection.commit()
            connection.close()

        # 에러가 발생했을 경우 백엔드에 에러 내용 출력 및 프론트엔드에 0 전송
        except Exception as e:
            connection.rollback()
            print(f"file_delete 에러: {e}")
            return Response(0)

        # 성공 했을 시, 프론트엔드에 1 전송송
        else:
            return Response(1)

    # sql 인젝션 되는 코드
    # 게시물 검색
    @action(detail=False, methods=['POST'])
    def board_search(self, request):
        # 데이터 저장을 위한 리스트 선언
        new_data = list()
        try:
            # DB 접근할 cursor
            cursor = connection.cursor()

            # POST 메소드로 날라온 Request의 데이터 각각 추출
            bcode = request.data['bcode']
            bcate = request.data['bcate']
            bsearch = request.data['bsearch']
            bcode = int(bcode)

            # 검색 조건 코드 분류
            # 전체 0, 제목 1, 내용 2, 작성자 3, 제목 + 내용 4
            # SQL 쿼리문 작성
            if bcode == 0:
                strsql = "SELECT bid, btitle, bfile, bview, bcomment, unickname, bcreate_date FROM skdevsec_board WHERE (btitle LIKE '%" + bsearch + "%' OR btext LIKE '%" + bsearch + "%' OR unickname LIKE '%" + bsearch + "%') AND b_lock=0 AND bcate='" + bcate + "'"
            elif bcode == 1:
                strsql = "SELECT bid, btitle, bfile, bview, bcomment, unickname, bcreate_date FROM skdevsec_board WHERE (btitle LIKE '%" + bsearch + "%') AND b_lock=0 AND bcate='" + bcate + "'"
            elif bcode == 2:
                strsql = "SELECT bid, btitle, bfile, bview, bcomment, unickname, bcreate_date FROM skdevsec_board WHERE (btext LIKE '%" + bsearch + "%') AND b_lock=0 AND bcate='" + bcate + "'"
            elif bcode == 3:
                strsql = "SELECT bid, btitle, bfile, bview, bcomment, unickname, bcreate_date FROM skdevsec_board WHERE (unickname LIKE '%" + bsearch + "%') AND b_lock=0 AND bcate='" + bcate + "'"
            elif bcode == 4:
                strsql = "SELECT bid, btitle, bfile, bview, bcomment, unickname, bcreate_date FROM skdevsec_board WHERE (btitle LIKE '%" + bsearch + "%' OR btext LIKE '%" + bsearch + "%') AND b_lock=0 AND bcate='" + bcate + "'"
            else:
                return Response("코드 값 잘못 보냄!!")

            # DB에 명령문 전송
            cursor.execute(strsql)
            datas = cursor.fetchone()

            # 데이터가 있으면
            if len(datas) != 0:
                # 데이터만큼 반복
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
            # 데이터가 없으면
            else:
                # DB와 접속 종료
                connection.commit()
                connection.close()
                # 프론트엔드에 0 전송
                return Response(0)

            # DB와 접속 종료
            connection.commit()
            connection.close()

        # 에러가 발생했을 경우 백엔드에 에러 내용 출력 및 프론트엔드에 0 전송
        except Exception as e:
            connection.rollback()
            print(f"board_search 에러: {e}")
            return Response(0)

        # 성공 했을 시, 프론트엔드에 데이터 전송
        else:
            return Response(new_data)

    # sql 인젝션 되는 코드
    # 내 게시물 보기(마이페이지)
    @action(detail=False, methods=['POST'])
    def my_board(self, request):
        # 데이터 저장하기 위한 리스트 선언
        new_data = list()
        try:
            # DB 접근할 cursor
            cursor = connection.cursor()

            # POST 메소드로 날라온 Request의 데이타 각각 추출
            unickname = request.data['unickname']
            bpage = request.data['bpage']
            bpage = int(bpage)

            # SQL 쿼리문 작성
            strsql = "SELECT COUNT(*) FROM skdevsec_board WHERE unickname='" + unickname + "'"

            # DB에 명령문 전송
            cursor.execute(strsql)
            datas = cursor.fetchone()

            # 게시물 갯수 저장
            new_data.append({"board_count": datas[0]})

            # SQL 쿼리문 작성
            strsql1 = "SELECT bid, btitle ,bfile, bview, bcomment, unickname, bcreate_date, b_lock FROM skdevsec_board where unickname='" + unickname + "' order by bcreate_date desc limit " + str(
                bpage * 10 - 10) + ", 10"

            # DB에 명령문 전송
            cursor.execute(strsql1)
            datas = cursor.fetchone()

            # 데이터가 있으면
            if len(datas) != 0:
                # 데이터 갯수만큼 반복
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
            # 데이터가 없으면
            else:
                # DB와 접속 종료
                connection.commit()
                connection.close()
                # 프론트엔드에 0 전송
                return Response(0)

            # DB와 접속 종료
            connection.commit()
            connection.close()

        # 에러가 발생했을 경우 백엔드에 에러 내용 출력 및 프론트엔드에 0 전송
        except Exception as e:
            connection.rollback()
            print(f"my_board 에러: {e}")
            return Response(0)

        # 성공 했을 시, 프론트엔드에 데이터 전송
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
            datas = cursor.fetchone()

            # 댓글 갯수 저장
            new_data.append({"comment_count": datas[0]})

            # SQL 쿼리문 작성
            strsql1 = "SELECT cid, unickname, ctext, ccreate_date, clock FROM skdevsec_comment where bid='" + bid + "' order by cid LIMIT " + str(
                cpage * 10 - 10) + " , 10"

            # DB에 명령문 전송
            cursor.execute(strsql1)
            datas = cursor.fetchone()

            # 데이터가 있으면
            if len(datas) != 0:
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
            # 데이터가 없으면
            else:
                # DB와 접속 종료
                connection.commit()
                connection.close()
                # 프론트엔드에 0 전송
                return Response(0)

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


# 장바구니 테이블
# 장바구니 목록 출력, 장바구니 목록 삭제, 장바구니 비우기, 장바구니 등록, 장바구니 결제
class SkdevsecBagViewSet(viewsets.ReadOnlyModelViewSet):
    # 테이블 출력을 위한 최소 코드
    queryset = SkdevsecBag.objects.all()
    serializer_class = SkdevsecBagSerializer

    # sql 인젝션 되는 코드
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
            strsql = "SELECT uid FROM skdevsec_user WHERE unickname='" + unickname + "'"

            # DB에 명령문 전송
            cursor.execute(strsql)
            uid = cursor.fetchone()

            # SQL 쿼리문 작성
            strsql1 = "SELECT bag_id, pid, bcount FROM skdevsec_bag where uid='" + uid[0] + "'"

            # DB에 명령문 전송
            cursor.execute(strsql1)
            datas = cursor.fetchall()

            # 장바구니 목록이 있으면
            if len(datas) != 0:
                # 장바구니 갯수만큼 반복
                for data in datas:
                    new_data_in = dict()
                    # SQL 쿼리문 작성
                    strsql2 = "SELECT pname, pcate, pimage, ptext, pprice FROM skdevsec_product WHERE pid='" + str(data[1]) + "'"
                    # DB에 명령문 전송
                    cursor.execute(strsql2)
                    products = cursor.fetchone()
                    # 상품이 있으면
                    if len(products) != 0:
                        new_data_in['bag_id'] = data[0]
                        new_data_in['pid'] = data[1]
                        new_data_in['pname'] = products[0]
                        new_data_in['pcate'] = products[1]
                        new_data_in['pimage'] = products[2]
                        new_data_in['ptext'] = products[3]
                        new_data_in['pprice'] = products[4]
                        new_data_in['bcount'] = data[2]
                        new_data.append(new_data_in)
                    # 상품이 없으면
                    else:
                        # DB와 접속 종료
                        connection.commit()
                        connection.close()
                        return Response(0)
            # 장바구니 목록이 없으면 0 전송
            else:
                # DB와 접속 종료
                connection.commit()
                connection.close()
                return Response(0)

            # DB와 접속 종료
            connection.commit()
            connection.close()

        # 에러가 발생했을 경우 백엔드에 에러 내용 출력 및 프론트엔드에 0 전송
        except Exception as e:
            connection.rollback()
            print(f"bag_show 에러: {e}")
            return Response(0)

        # 성공 했을 시, 프론트엔드에 데이터 전송
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
            strsql = "DELETE FROM skdevsec_bag WHERE bag_id='" + bag_id + "'"

            # DB에 명령문 전송
            cursor.execute(strsql)

            # DB와 접속 종료
            connection.commit()
            connection.close()

        # 에러가 발생했을 경우 백엔드에 에러 내용 출력 및 프론트엔드에 0 전송
        except Exception as e:
            connection.rollback()
            print(f"bag_delete 에러: {e}")
            return Response(0)

        # 성공 했을 시, 프론트엔드에 1 전송
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
            unickname = request.data['unickname']

            # SQL 쿼리문 작성
            strsql = "SELECT uid FROM skdevsec_user WHERE unickname='" + unickname + "'"

            # DB에 명령문 전송
            cursor.execute(strsql)
            uid = cursor.fetchone()

            # SQL 쿼리문 작성
            strsql1 = "DELETE FROM skdevsec_bag WHERE uid='" + uid[0] + "'"

            # DB에 명령문 전송
            cursor.execute(strsql1)

            # DB와 접속 종료
            connection.commit()
            connection.close()

        # 에러가 발생했을 경우 백엔드에 에러 내용 출력 및 프론트엔드에 0 전송
        except Exception as e:
            connection.rollback()
            print(f"bag_delete_all 에러: {e}")
            return Response(0)

        # 성공 했을 시, 프론트엔드에 1 전송
        else:
            return Response(1)

    # sql 인젝션 되는 코드
    # 장바구니 등록
    @action(detail=False, methods=['POST'])
    def bag_add(self, request):
        try:
            # DB 접근할 cursor
            cursor = connection.cursor()

            # POST 메소드로 날라온 Request의 데이터 각각 추출
            unickname = request.data['unickname']
            pid = request.data['pid']
            bcount = request.data['bcount']

            # SQL 쿼리문 작성
            strsql = "SELECT uid FROM skdevsec_user WHERE unickname='" + unickname + "'"

            # DB에 명령문 전송
            cursor.execute(strsql)
            uid = cursor.fetchone()

            # SQL 쿼리문 작성
            strsql1 = "SELECT uid FROM skdevsec_bag WHERE uid='" + uid[0] + "' AND pid='" + pid + "'"

            # DB에 명령문 전송
            cursor.execute(strsql1)
            uid1 = cursor.fetchall()

            # 장바구니에 상품이 있으면
            if len(uid1) != 0:
                # SQL 쿼리문 작성
                strsql2 = "UPDATE skdevsec_bag SET bcount=bcount+'" + bcount + "' WHERE pid='" + pid + "' AND uid='" + uid1[0][0] + "'"
                # DB에 명령문 전송
                cursor.execute(strsql2)
            else:
                # SQL 쿼리문 작성
                strsql2 = "INSERT INTO skdevsec_bag(uid, pid, bcount) VALUES('" + uid[0] + "', '" + pid + "', '" + bcount + "')"
                # DB에 명령문 전송
                cursor.execute(strsql2)

            # DB와 접속 종료
            connection.commit()
            connection.close()

        # 에러가 발생했을 경우 백엔드에 에러 내용 출력 및 프론트엔드에 0 전송
        except Exception as e:
            connection.rollback()
            print(f"bag_add 에러: {e}")
            return Response(0)

        # 성공 했을 시, 프론트엔드에 1 전송
        else:
            return Response(1)

    # sql 인젝션 되는 코드
    # 장바구니 결제
    @action(detail=False, methods=['POST'])
    def bag_pay(self, request):
        # 데이터 저장을 위한 리스트 선언
        new_data = list()
        new_data1 = list()
        try:
            # DB 접근할 cursor
            cursor = connection.cursor()

            # POST 메소드로 날라온 Request의 데이터 각각 추출
            unickname = request.data['unickname']

            # SQL 쿼리문 작성
            strsql = "SELECT uid FROM skdevsec_user WHERE unickname='" + unickname + "'"

            # DB에 명령문 전송
            cursor.execute(strsql)
            uid = cursor.fetchone()

            # SQL 쿼리문 작성
            strsql1 = "SELECT pid, bcount FROM skdevsec_bag WHERE uid='" + uid[0] + "'"

            # DB에 명령문 전송
            cursor.execute(strsql1)
            datas = cursor.fetchone()

            # 데이터가 있으면
            if len(datas) != 0:
                #데이터 만큼 반복
                while datas:
                    new_data.append(datas)
                    datas = cursor.fetchone()
            # 데이터가 없으면
            else:
                # DB와 접속 종료
                connection.commit()
                connection.close()
                # 프론트엔드에 0 전송
                return Response(0)

            # 받은 데이터에서 상품 번호와, 장바구니에 추가한 갯수를 분리
            for pid, bcount in new_data:
                # SQL 쿼리문 작성
                strsql2 = "SELECT pname, pcate, pimage, pprice FROM skdevsec_product WHERE pid='" + str(pid) + "'"

                # DB에 명령문 전송
                cursor.execute(strsql2)
                datas1 = cursor.fetchone()
                # 상풍 데이터가 있으면
                if len(datas1) != 0:
                    # 데이터를 딕셔너리에 저장
                    while datas1:
                        new_data_in = dict()
                        new_data_in['pname'] = datas1[0]
                        new_data_in['pcate'] = datas1[1]
                        new_data_in['pimage'] = datas1[2]
                        new_data_in['pprice'] = datas1[3]
                        new_data_in['pcount'] = bcount
                        new_data1.append(new_data_in)
                        datas1 = cursor.fetchone()
                # 상품 데이터가 없으면 프론트 엔드에 0 전송
                else:
                    return Response(0)

            # DB와 접속 종료
            connection.commit()
            connection.close()

        # 에러가 발생했을 경우 백엔드에 에러 내용 출력 및 프론트엔드에 0 전송
        except Exception as e:
            connection.rollback()
            print(f"bag_pay 에러: {e}")
            return Response(0)

        # 성공 했을 시, 데이터 전송
        else:
            return Response(new_data1)


# 상품 관련 테이블
# 상품 리스트 출력, 상품 상세 페이지 출력, 상품 등록, 상품 수정, 상품 삭제, 상품 검색
class SkdevsecProductViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = SkdevsecProduct.objects.all()
    serializer_class = SkdevsecProductSerializer

    # sql 인젝션 되는 코드
    # 상품 리스트 출력
    @action(detail=False, methods=['POST'])
    def item_list(self, request):
        new_data = list()
        try:
            # DB 접근할 cursor
            cursor = connection.cursor()

            # # POST 메소드로 날라온 Request의 데이터 각각 추출
            ppage = int(request.data['ppage'])

            # SQL 쿼리문 작성
            strsql = "SELECT COUNT(*) FROM skdevsec_product"

            # DB에 명령문 전송
            cursor.execute(strsql)
            datas = cursor.fetchone()

            # 상품 갯수 저장
            new_data.append({"product_count": datas[0]})

            # SQL 쿼리문 작성
            strsql1 = "SELECT * FROM skdevsec_product order by pid desc limit " + str(ppage * 8 - 8) + ", 8"

            # DB에 명령문 전송
            cursor.execute(strsql1)
            datas = cursor.fetchone()

            # 데이터가 있으면
            if len(datas) != 0:
                # 데이터 수만큼 반복
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
            # 데이터가 없으면
            else:
                # DB와 접속 종료
                connection.commit()
                connection.close()
                return Response(0)

            # DB와 접속 종료
            connection.commit()
            connection.close()

        # 에러가 발생했을 경우 백엔드에 에러 내용 출력 및 프론트엔드에 0 전송
        except Exception as e:
            connection.rollback()
            print(f"item_list 에러: {e}")
            return Response(0)

        # 성공 했을 시, 프론트엔드에 데이터 전송
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

            # 데이터가 있으면
            if len(datas) != 0:
                # 데이터 수만큼 반복
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
            # 데이터가 없으면
            else:
                # DB와 접속 종료
                connection.commit()
                connection.close()
                # 프론트엔드에 0 전송
                return Response(0)

            # DB와 접속 종료
            connection.commit()
            connection.close()

        # 에러가 발생했을 경우 백엔드에 에러 내용 출력 및 프론트엔드에 0 전송
        except Exception as e:
            connection.rollback()
            print(f"product_inside 에러: {e}")
            return Response(0)

        # 성공 했을 시, 프론트엔드에 데이터 전송
        else:
            return Response(new_data)

    # sql 인젝션 되는 코드
    # 상품 등록
    @action(detail=False, methods=['POST'])
    def product_upload(self, request):
        # 데이터 저장을 위한 딕셔너리 설정
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
            # 불가능한 상태면 에러 알림 및 프론트엔드에 0 전송
            else:
                print("serializer 에러")
                return Response(0)

        # 에러가 발생했을 경우 백엔드에 에러 내용 출력 및 프론트엔드에 0 전송
        except Exception as e:
            connection.rollback()
            print(f"product_upload 에러: {e}")
            return Response(0)

        # 성공 했을 시, 프론트엔드에 1 전송
        else:
            return Response(1)

    # sql 인젝션 되는 코드
    # 상품 수정
    @action(detail=False, methods=['POST'])
    def change_product(self, request):
        # 데이터 저장을 위한 딕셔너리 선언
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
            strsql = "SELECT pimage FROM skdevsec_product WHERE pid='" + pid + "'"

            # DB에 명령문 전송
            cursor.execute(strsql)
            datas = cursor.fetchall()

            # 파일이 존재하면 삭제
            if datas[0][0] != "0":
                os.remove(datas[0][0])

            # DB에 저장하기 위해 시리얼라이저 함수 사용
            file_serializer = SkdevsecBoardSerializer(data_check, data=new_data)

            # 수정할 데이터를 업데이트함
            if file_serializer.is_valid():
                file_serializer.update(data_check, file_serializer.validated_data)
            # 불가능한 상태면 에러 알림 및 프론트엔드에 0 전송
            else:
                print("serializer 에러")
                return Response(0)

        # 에러가 발생했을 경우 백엔드에 에러 내용 출력 및 프론트엔드에 0 전송
        except Exception as e:
            connection.rollback()
            print(f"change_product 에러: {e}")
            return Response(0)

        # 성공 했을 시, 프론트엔드에 1 전송
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
            strsql = "SELECT pimage FROM skdevsec_product WHERE pid='" + pid + "'"

            # DB에 명령문 전송
            cursor.execute(strsql)
            datas = cursor.fetchall()

            # 파일이 존재하면 삭제
            if datas[0][0] != "0":
                os.remove(datas[0][0])

            # SQL 쿼리문 작성
            strsql1 = "DELETE FROM skdevsec_product WHERE pid='" + pid + "'"

            # DB에 명령문 전송
            cursor.execute(strsql1)

            # DB와 접속 종료
            connection.commit()
            connection.close()

        # 에러가 발생했을 경우 백엔드에 에러 내용 출력 및 프론트엔드에 0 전송
        except Exception as e:
            connection.rollback()
            print(f"product_delete 에러: {e}")
            return Response(0)

        # 성공 했을 시, 프론트엔드에 1 전송
        else:
            return Response(1)

    # sql 인젝션 되는 코드
    # 상품 검색
    @action(detail=False, methods=['POST'])
    def product_search(self, request):
        # 데이터 저장을 위한 리스트 선언
        new_data = list()
        try:
            # DB 접근할 cursor
            cursor = connection.cursor()

            # POST 메소드로 날라온 Request의 데이터 각각 추출
            pcode = request.data['pcode']
            psearch = request.data['psearch']
            pcode = int(pcode)

            # psearch = ["검색단어", "카테고리", "카테고리", ...]
            # 검색 조건 코드 분류
            # 상품 명 0, 카테고리 1
            if pcode == 0:
                # SQL 쿼리문 작성
                strsql = "SELECT pid, pcate, pimage, pname, pprice, preview, preview_avg FROM skdevsec_product WHERE (pname LIKE '%" + psearch[0] + "%')"
            elif pcode == 1:
                strsql = "SELECT pid, pcate, pimage, pname, pprice, preview, preview_avg FROM skdevsec_product WHERE (pname LIKE '%" + psearch[0] + "%') AND (pcate='"
                for pcate in psearch[1:]:
                    strsql = strsql + pcate + "' OR pcate='"
                strsql = strsql + "')"
            else:
                return Response("코드 값 잘못 보냄!!")

            # DB에 명령문 전송
            cursor.execute(strsql)
            datas = cursor.fetchone()

            # 데이터가 있으면
            if len(datas) != 0:
                # 데이터만큼 반복
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
            # 데이터가 없으면
            else:
                # DB와 접속 종료
                connection.commit()
                connection.close()
                # 프론트엔드에 0 전송
                return Response(0)

            # DB와 접속 종료
            connection.commit()
            connection.close()

        # 에러가 발생했을 경우 백엔드에 에러 내용 출력 및 프론트엔드에 0 전송
        except Exception as e:
            connection.rollback()
            print(f"product_search 에러: {e}")
            return Response(0)

        # 성공 했을 시, 프론트엔드에 데이터 전송
        else:
            return Response(new_data)


# 상품 리뷰 관련 테이블
# 리뷰 출력, 리뷰 등록, 리뷰 삭제, 리뷰 검증
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
            if len(datas) != 0:
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
            oid = cursor.fetchone()

            # SQL 쿼리문 작성
            strsql2 = "SELECT pname FROM skdevsec_orderproduct WHERE oid='" + oid[0] + "'"

            # DB에 명령문 전송
            cursor.execute(strsql2)
            pnames = cursor.fetchall()

            # 데이터 처리를 위한 리스트 선언
            pname_list = list()

            for pname in pnames:
                pname_list.append(pname[0])

            # 만약 사용자가 상품을 구매했으면 리뷰한 적이 있는지 확인
            if pname in pname_list:
                # SQL 쿼리문 작성
                strsql3 = "SELECT pid FROM skdevsec_product WHERE pname='" + pnames + "'"

                # DB에 명령문 전송
                cursor.execute(strsql3)
                pid = cursor.fetchone()

                # SQL 쿼리문 작성
                strsql4 = "SELECT * FROM skdevsec_review WHERE pid='" + pid[0] + "' AND unickname='" + unickname + "'"

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
            if len(review) != 0:
                return Response(1)
            else:
                return Response(0)


# 결제 기록 테이블
# 카카오 페이 admin key : 28743e8e95f287447491df3d2ea26c22
# 결제 전 핸드폰 인증, 인증 번호 확인, 결제 결과 저장, 결제 기능, 결제 결과 출력
class SkdevsecOrderuserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = SkdevsecOrderuser.objects.all()
    serializer_class = SkdevsecOrderuserSerializer

    # 결제 전 핸드폰 인증
    @action(detail=False, methods=['POST'])
    def send_sms(self, request):
        try:
            # DB 접근할 cursor
            cursor = connection.cursor()

            # POST 메소드로 날라온 Request의 데이터 각각 추출
            unickname = request.data['unickname']
            ophone = request.data['ophone']

            # SQL 쿼리문 작성
            strsql = "SELECT uphone FROM skdevsec_user where unickname='" + unickname + "'"

            # DB에 명령문 전송
            cursor.execute(strsql)
            uphone = cursor.fetchone()

            # 회원 번호와 입력 번호가 일치하면 문자 전송
            if uphone[0] == ophone:
                rand_num = sms_send(ophone)
            # 안하면 프론트엔드에 0 전송
            else:
                return Response(0)

            # DB와 접속 종료
            connection.commit()
            connection.close()

        # 에러가 발생했을 경우 백엔드에 에러 내용 출력 및 프론트엔드에 0 전송
        except Exception as e:
            connection.rollback()
            print(f"send_sms 에러: {e}")
            return Response(0)
        # 성공 했을 시, 전송했던 인증 번호를 프론트엔드에 전달
        else:
            return Response(rand_num)

    # 인증 번호 확인
    @action(detail=False, methods=['POST'])
    def sms_check(self, request):
        try:
            # POST 메소드로 날라온 Request의 데이터 각각 추출
            check_num = request.data('check_num')
            input_num = request.data('input_num')

            # 인증번호와 입력 번호가 다르면 프론트엔드에 0 전송
            if check_num != input_num:
                return Response(0)

        # 에러가 발생했을 경우 백엔드에 에러 내용 출력 및 프론트엔드에 0 전송
        except Exception as e:
            print(f"sms_check 에러: {e}")
            return Response(0)
        # 성공 했을 시, 프론트 엔드에 1 전송
        else:
            return Response(1)

    # sql 인젝션 되는 코드
    # 결제 기능
    @action(detail=False, methods=['POST'])
    def kakaopay(self, request):
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
            connection.commit()

            # SQL 쿼리문 작성
            strsql1 = "SELECT oid FROM skdevsec_orderuser ORDER BY order_date DESC"

            # DB에 명령문 전송
            cursor.execute(strsql1)
            oid = cursor.fetchone()

            # Kakao Pay 결제 API
            url = "https://kapi.kakao.com"
            headers = {
                'Authorization': "KakaoAK " + "28743e8e95f287447491df3d2ea26c22",
                'Content-type': 'application/x-www-form-urlencoded;charset=utf-8',
            }
            params = {
                'cid': "TC0ONETIME",
                'partner_order_id': oid[0],
                'partner_user_id': oname,
                'item_name': '결제 상품(들)',
                'quantity': 1,
                'total_amount': oprice,
                'vat_amount': 0,
                'tax_free_amount': 0,
                'approval_url': 'http://10.60.15.210:8000/',
                'fail_url': 'http://10.60.15.210:8000/',
                'cancel_url': 'http://10.60.15.210:8000/',
            }
            response = requests.post(url + "/v1/payment/ready", params=params, headers=headers)
            response = json.loads(response.text)

            # DB와 접속 종료
            connection.commit()
            connection.close()

        # 에러가 발생했을 경우 백엔드에 에러 내용 출력 및 프론트엔드에 0 전송
        except Exception as e:
            connection.rollback()
            print(f"kakaopay 에러: {e}")
            return Response(0)

        # 성공 했을 시, 프론트엔드에 데이터 전송
        else:
            return Response(response)

    # sql 인젝션 되는 코드
    # 결제 결과 출력
    @action(detail=False, methods=['POST'])
    def user_paid_output(self, request):
        # 데이터 저장을 위한 리스트 선언
        new_data = list()
        try:
            # DB 접근할 cursor
            cursor = connection.cursor()

            # POST 메소드로 날라온 Request의 데이터 각각 추출
            opage = request.data['opage']
            opage = int(opage)

            # SQL 쿼리문 작성
            strsql = "SELECT COUNT(*) FROM skdevsec_orderuser"

            # DB에 명령문 전송
            cursor.execute(strsql)
            datas = cursor.fetchone()

            # 주문 내역 갯수 저장
            new_data.append({"order_count": datas[0]})

            # SQL 쿼리문 작성
            strsql1 = "SELECT oid, uid, oname, ophone, oaddress, order_date, oprice FROM skdevsec_orderuser order by oid desc limit " + str(opage * 10 - 10) + ", 10"

            # DB에 명령문 전송
            cursor.execute(strsql1)
            datas = cursor.fetchone()

            # 데이터가 있으면
            if len(datas) != 0:
                # 데이터 수만큼 반복
                while datas:
                    new_data_in = dict()
                    new_data_in['oid'] = datas[0]
                    new_data_in['uid'] = datas[1]
                    new_data_in['oname'] = datas[2]
                    new_data_in['ophone'] = datas[3]
                    new_data_in['oaddress'] = datas[4]
                    new_data_in['order_date'] = datas[5]
                    new_data_in['oprice'] = datas[6]
                    new_data.append(new_data_in)
                    datas = cursor.fetchone()
            # 데이터가 없으면
            else:
                # DB와 접속 종료
                connection.commit()
                connection.close()
                # 프론트엔드에 0 전송
                return Response(0)

            # DB와 접속 종료
            connection.commit()
            connection.close()

        # 에러가 발생했을 경우 백엔드에 에러 내용 출력 및 프론트엔드에 0 전송
        except Exception as e:
            connection.rollback()
            print(f"pay_result_output 에러: {e}")
            return Response(0)

        # 성공 했을 시, 프론트엔드에 데이터 전송
        else:
            return Response(new_data)


# 결제 내역 테이블
# 결제 내역 저장
class SkdevsecOrderproductViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = SkdevsecOrderproduct.objects.all()
    serializer_class = SkdevsecOrderproductSerializer

    # sql 인젝션 되는 코드
    # 결제 내역 저장
    @action(detail=False, methods=['POST'])
    def pay_result_add(self, request):
        # 데이터 저장을 위한 변수 선언
        pname, pcate, pprice = '', '', ''
        try:
            # DB 접근할 cursor
            cursor = connection.cursor()

            # POST 메소드로 날라온 Request의 데이터 각각 추출
            oid = request.data['oid']
            pid = request.data['pid']
            bcount = request.data['bcount']

            # SQL 쿼리문 작성
            strsql = "SELECT pname, pcate, pprice FROM skdevsec_product WHERE pid='" + pid + "'"

            # DB에 명령문 전송
            cursor.execute(strsql)
            datas = cursor.fetchall()

            # 데이터가 있으면
            if len(datas) != 0:
                for data in datas:
                    pname = data[0]
                    pcate = data[1]
                    pprice = data[2]
            # 데이터가 없으면
            else:
                # DB와 접속 종료
                connection.commit()
                connection.close()
                # 프론트엔드로 0 전송
                return Response(0)

            # SQL 쿼리문 작성
            strsql1 = "INSERT INTO skdevsec_orderproduct(oid, pname, pcate, pprice, pcount) VALUES('" + oid + "', '" + pname + "', '" + pcate + "', '" + pprice + "', '" + bcount + "')"

            # DB에 명령문 전송
            cursor.execute(strsql1)

            # DB와 접속 종료
            connection.commit()
            connection.close()

        # 에러가 발생했을 경우 백엔드에 에러 내용 출력 및 프론트엔드로 0 전송
        except Exception as e:
            connection.rollback()
            print(f"pay_result_add 에러: {e}")
            return Response(0)

        # 성공 했을 시, 1 전송
        else:
            return Response(1)
