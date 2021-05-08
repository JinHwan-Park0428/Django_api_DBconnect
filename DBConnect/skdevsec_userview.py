# 필요한 모듈 임포트
from random import *
from django.core.mail import send_mail
from django.db import connection
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from DBConnect.serializers import *
from DBtest.settings import EMAIL_HOST_USER
from . import sms_send


# 회원 정보 관련 테이블
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
                if datas is not None:
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
            count = 0
            try:
                # POST 메소드로 날라온 Request의 데이터 각각 추출
                ucode = request.data['ucode']
                usearch = request.data['usearch']
                upage = request.data['upage']
                upage = int(upage)
                ucode = int(ucode)

                # DB 접근할 cursor
                cursor = connection.cursor()

                # SQL 쿼리문 작성
                # 0: 전체 검색 / 1 : 이름 / 2 : 닉네임 / 3 : 아이디 / 4 : 이메일
                if ucode == 0:
                    strsql = "SELECT * FROM skdevsec_user where (uname LIKE '%" + usearch + "%' OR unickname LIKE '%" + usearch + "%' OR uid LIKE '%" + usearch + "%' OR umail LIKE '%" + usearch + "%') order by ucreate_date desc limit " + str(upage * 10 - 10) + ", 10"
                elif ucode == 1:
                    strsql = "SELECT * FROM skdevsec_user where uname LIKE '%" + usearch + "%' order by ucreate_date desc limit " + str(upage * 10 - 10) + ", 10"
                elif ucode == 2:
                    strsql = "SELECT * FROM skdevsec_user where unickname LIKE '%" + usearch + "%' order by ucreate_date desc limit " + str(upage * 10 - 10) + ", 10"
                elif ucode == 3:
                    strsql = "SELECT * FROM skdevsec_user where uid LIKE '%" + usearch + "%' order by ucreate_date desc limit " + str(upage * 10 - 10) + ", 10"
                elif ucode == 4:
                    strsql = "SELECT * FROM skdevsec_user where umail LIKE '%" + usearch + "%' order by ucreate_date desc limit " + str(upage * 10 - 10) + ", 10"
                else:
                    return Response("코드 값 잘못 보냄!!")

                # DB에 명령문 전송
                cursor.execute(strsql)
                datas = cursor.fetchone()

                # 데이터가 있으면
                if datas is not None:
                    # 데이터 만큼 반복
                    while datas:
                        count += 1
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
                    # DB와 접속 종료
                    connection.commit()
                    connection.close()
                    # 프론트엔드에 0 전송
                    return Response(0)

                new_data.append({"user_count": count})

                # DB와 접속 종료
                connection.commit()
                connection.close()

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

    # sql 인젝션 되는 코드
    # 아이디 찾기 전 이메일 인증
    @action(detail=False, methods=['POST'])
    def find_id_email(self, request):
        try:
            # DB 접근할 cursor
            cursor = connection.cursor()

            # POST 메소드로 날라온 Request의 데이터 각각 추출
            uname = request.data['uname']
            umail = request.data['umail']

            # SQL 쿼리문 작성
            strsql = "SELECT * FROM skdevsec_user WHERE umail='" + umail + "' AND uname='" + uname + "'"

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

        # 데이터가 존재하지않으면 프론트엔드에 0을 전송 아니면 이메일 전송 작업 시작
        else:
            if len(datas) == 0:
                return Response(0)
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
    # 아이디 찾기
    @action(detail=False, methods=['POST'])
    def find_id(self, request):
        try:
            # DB 접근할 cursor
            cursor = connection.cursor()

            # POST 메소드로 날라온 Request의 데이터 각각 추출
            uname = request.data['uname']
            umail = request.data['umail']

            # SQL 쿼리문 작성
            strsql = "SELECT uid FROM skdevsec_user WHERE umail='" + umail + "' AND uname='" + uname + "'"

            # DB에 명령문 전송
            cursor.execute(strsql)
            uid = cursor.fetchall()

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
            if len(uid) != 0:
                return Response(uid[0][0])
            else:
                return Response(0)

    # sql 인젝션 되는 코드
    # 결제 전 핸드폰 인증
    @action(detail=False, methods=['POST'])
    def find_pwd_sms(self, request):
        try:
            # DB 접근할 cursor
            cursor = connection.cursor()

            # POST 메소드로 날라온 Request의 데이터 각각 추출
            uid = request.data['uid']
            uname = request.data['uname']

            strsql = "SELECT uphone FROM skedevsec_user WHERE uid='" + uid + "' AND uname='" + uname + "'"

            # DB에 명령문 전송
            cursor.execute(strsql)
            uphone = cursor.fetchall()
            # 문자 전송
            rand_num = sms_send(uphone[0][0])

            # DB와 접속 종료
            connection.commit()
            connection.close()

        # 에러가 발생했을 경우 백엔드에 에러 내용 출력 및 프론트엔드에 0 전송
        except Exception as e:
            connection.rollback()
            print(f"find_pwd_sms 에러: {e}")
            return Response(0)
        # 성공 했을 시, 전송했던 인증 번호를 프론트엔드에 전달
        else:
            return Response(rand_num)

    # sql 인젝션 되는 코드
    # 결제 전 핸드폰 인증
    @action(detail=False, methods=['POST'])
    def find_pwd(self, request):
        try:
            # DB 접근할 cursor
            cursor = connection.cursor()

            # POST 메소드로 날라온 Request의 데이터 각각 추출
            uid = request.data['uid']
            upwd = request.data['upwd']

            strsql = "UPDATE skedevsec_user SET upwd='" + upwd + "' WHERE uid='" + uid + "'"

            # DB에 명령문 전송
            cursor.execute(strsql)

            # DB와 접속 종료
            connection.commit()
            connection.close()

        # 에러가 발생했을 경우 백엔드에 에러 내용 출력 및 프론트엔드에 0 전송
        except Exception as e:
            connection.rollback()
            print(f"find_pwd 에러: {e}")
            return Response(0)
        # 성공 했을 시, 프론트에 1 전달
        else:
            return Response(1)
