# 필요한 모듈 임포트
from rest_framework import viewsets
from rest_framework import permissions
from DBConnect.models import *
from DBConnect.serializers import *
from django.db import connection
from rest_framework.decorators import action
from rest_framework.response import Response

import json
from .text import message
from .token import account_activation_token
from DBtest.settings import SECRET_KEY

from django.views import View
from django.http import HttpResponse, JsonResponse
from django.core.exceptions import ValidationError
from django.shortcuts import redirect
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode,urlsafe_base64_decode
from django.core.mail import EmailMessage
from django.core.mail import send_mail
from django.utils.encoding import force_bytes, force_text

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
    # 회원가입 함수
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
                    currnet_site = get_current_site(request)
                    domain = currnet_site.domain
                    # uidb64 = urlsafe_base64_encode(force_bytes(umail))
                    # token = account_activation_token(SkdevsecUser.objects.get(pk=umail))
                    message_date = message(domain)

                    mail_title = "이메일 인증을 완료해주세요"
                    mail_to = umail
                    email = EmailMessage("test", "test mail", to=[mail_to])
                    email.send()
                    return Response(0)

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
            print("들어온 request 값: ", request)
            print("들어온 data 값: ", request.data)

            # POST 메소드로 날라온 Request의 데이타 각각 추출
            uid = request.data['uid']
            upwd = request.data['upwd']
            # authority = request.data['authority']

            # SQL 쿼리문 작성
            strsql = "SELECT authority FROM skdevsec_user WHERE uid='" + uid + "' " + "and upwd='" + upwd + "'"

            # DB에 명령문 전송
            result = cursor.execute(strsql)
            datas = cursor.fetchall()

            # 데이터를 사용완료 했으면 DB와의 접속 종료(부하 방지)
            connection.commit()
            connection.close()

            for data in datas:
                new_data['authority'] = data[0]

        # 에러가 발생했을 경우 에러 내용 출력 및 로그인 실패 코드(0) 전송
        except Exception as e:
            connection.rollback()
            print(e)

        # 관리자 로그인이면 2 일반 사용자이면 1 전송
        else:
            if len(new_data) != 0:
                if new_data['authority'] == 1:
                    return Response(2)
                else:
                    return Response(1)
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
            uid = request.data['uid']

            # SQL 쿼리문 작성
            strsql = "SELECT uid, unickname, uname, umail, uphone, ucreate_date FROM skdevsec_user WHERE uid='" + uid + "'"

            # DB에 명령문 전송
            result = cursor.execute(strsql)
            datas = cursor.fetchall()

            # 데이터를 사용완료 했으면 DB와의 접속 종료(부하 방지)
            connection.commit()
            connection.close()

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
    # 내 정보 수정하기
    @action(detail=False, methods=['POST'])
    def change_info(self, request):
        try:
            # DB 접근할 cursor
            cursor = connection.cursor()

            # POST 메소드로 날라온 Request의 데이타 각각 추출
            uid = request.data['uid']
            upwd = request.data['upwd']
            unickname = request.data['unickname']
            umail = request.data['umail']
            uphone = request.data['uphone']

            # SQL 쿼리문 작성
            strsql = "UPDATE skdevsec_user SET upwd='" + upwd + "', " + "unickname='" + unickname + "', " + "umail='" + umail + "', " +"uphone='" + uphone+ "' WHERE uid='" + uid + "'"

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


class SkdevsecBagViewSet(viewsets.ReadOnlyModelViewSet):
    # 테이블 출력을 위한 최소 코드
    queryset = SkdevsecBag.objects.all()
    serializer_class = SkdevsecBagSerializer


class SkdevsecBoardViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = SkdevsecBoard.objects.all()
    serializer_class = SkdevsecBoardSerializer


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



