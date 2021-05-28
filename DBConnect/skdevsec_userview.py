# 필요한 모듈 임포트
import random
import re
import string
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

    # 관리자 페이지 (회원 정보 보기)
    @action(detail=False, methods=['POST'])
    def admin_user_info(self, request):
        # 권한이 1 이고 닉네임이 admin일 시
        if request.data['authority'] == '1' and request.data['unickname'] == 'admin':
            # 데이터 저장을 위한 리스트 선언
            new_data = list()
            try:
                # POST 메소드로 날라온 Request의 데이터 각각 추출
                upage = int(request.data['upage'])

                # DB 접근할 cursor
                cursor = connection.cursor()

                # SQL 쿼리문 작성
                sql_query_1 = "SELECT COUNT(*) FROM skdevsec_user"

                # DB에 명령문 전송
                cursor.execute(sql_query_1)
                count = cursor.fetchone()

                if count is not None:
                    # 전체 유저 수를 저장
                    new_data.append({"user_count": count[0]})
                else:
                    new_data.append({"user_count": 0})

                # SQL 쿼리문 작성
                strsql = "SELECT * FROM skdevsec_user order by ucreate_date desc limit %s, 10 "

                # DB에 명령문 전송
                cursor.execute(strsql, (upage*10-10,))
                data = cursor.fetchone()

                # 데이터가 존재 한다면
                if data is not None:
                    # 데이터 갯수 만큼 반복
                    # 데이터를 딕셔너리 형태로 저장 후, 리스트에 추가
                    while data:
                        new_data_in = dict()
                        new_data_in['uid'] = data[0]
                        new_data_in['unickname'] = data[2]
                        new_data_in['uname'] = data[3]
                        new_data_in['umail'] = data[4]
                        new_data_in['uphone'] = data[5]
                        new_data_in['ucreate_date'] = data[6]
                        new_data_in['authority'] = int(data[7])
                        new_data.append(new_data_in)
                        data = cursor.fetchone()
                # 데이터가 존재 하지 않는 다면
                else:
                    # DB와 접속 종료 후 프론트엔드에 0 전송
                    connection.close()
                    return Response(0)

                # DB와 접속 종료
                connection.close()

            # 에러가 발생했을 경우 백엔드에 에러 출력 및 프론트엔드에 0 전송
            except Exception as e:
                connection.rollback()
                print(f"에러: {e}")
                return Response(0)

            # 데이터 처리가 끝났으면 프론트엔드에 데이터 전송
            else:
                return Response(new_data)
        # 관리자가 아니면 프론트엔드에 0 전송
        else:
            return Response(0)

    # 관리자 페이지 (회원 정보 검색)
    @action(detail=False, methods=['POST'])
    def admin_user_search(self, request):
        # 권한이 1 이고 닉네임이 admin일 시
        if request.data['authority'] == '1' and request.data['unickname'] == 'admin':
            # 데이터 저장을 위한 리스트 선언
            new_data = list()
            try:
                # POST 메소드로 날라온 Request의 데이터 각각 추출
                ucode = int(request.data['ucode'])
                usearch = request.data['usearch']
                upage = int(request.data['upage'])

                p = re.compile('[\{\}\[\]\/?.,;:|\)*~`!@^\-+<>\#$%&\\\=\(\'\"]')

                m = p.search(usearch)

                if m:
                    return Response(0)
                else:
                    # DB 접근할 cursor
                    cursor_count = connection.cursor()
                    cursor_data = connection.cursor()

                    # SQL 쿼리문 작성
                    # 0: 전체 검색 / 1 : 이름 / 2 : 닉네임 / 3 : 아이디 / 4 : 이메일
                    if ucode == 0:
                        sql_query_1 = "SELECT * FROM skdevsec_user where (uname LIKE %s OR unickname LIKE %s OR uid LIKE " \
                                      "%s OR umail LIKE %s) order by ucreate_date desc limit %s, 10"
                        sql_query_2 = "SELECT COUNT(*) FROM skdevsec_user where (uname LIKE %s OR unickname LIKE %s OR " \
                                      "uid LIKE %s OR umail LIKE %s)"
                        # DB에 명령문 전송
                        cursor_count.execute(sql_query_2, ('%' + usearch + '%', '%' + usearch + '%', '%' + usearch + '%',
                                                           '%' + usearch + '%',))
                        count = cursor_count.fetchone()

                        cursor_data.execute(sql_query_1, ('%' + usearch + '%', '%' + usearch + '%', '%' + usearch + '%', '%'
                                                          + usearch + '%', upage*10-10,))
                        data = cursor_data.fetchone()

                    elif ucode == 1:
                        sql_query_1 = "SELECT * FROM skdevsec_user where uname LIKE %s order by ucreate_date desc limit " \
                                      "%s, 10 "
                        sql_query_2 = "SELECT COUNT(*) FROM skdevsec_user where uname LIKE %s"

                        # DB에 명령문 전송
                        cursor_count.execute(sql_query_2, ('%' + usearch + '%',))
                        count = cursor_count.fetchone()

                        cursor_data.execute(sql_query_1, ('%' + usearch + '%', upage*10-10,))
                        data = cursor_data.fetchone()

                    elif ucode == 2:
                        sql_query_1 = "SELECT * FROM skdevsec_user where unickname LIKE %s order by ucreate_date desc " \
                                      "limit %s, 10 "
                        sql_query_2 = "SELECT COUNT(*) FROM skdevsec_user where unickname LIKE %s"

                        # DB에 명령문 전송
                        cursor_count.execute(sql_query_2, ('%' + usearch + '%',))
                        count = cursor_count.fetchone()

                        cursor_data.execute(sql_query_1, ('%' + usearch + '%', upage*10-10,))
                        data = cursor_data.fetchone()

                    elif ucode == 3:
                        sql_query_1 = "SELECT * FROM skdevsec_user where uid LIKE %s order by ucreate_date desc limit %s, " \
                                      "10 "
                        sql_query_2 = "SELECT COUNT(*) FROM skdevsec_user where uid LIKE %s"

                        # DB에 명령문 전송
                        cursor_count.execute(sql_query_2, ('%' + usearch + '%',))
                        count = cursor_count.fetchone()

                        cursor_data.execute(sql_query_1, ('%' + usearch + '%', upage*10-10,))
                        data = cursor_data.fetchone()

                    elif ucode == 4:
                        sql_query_1 = "SELECT * FROM skdevsec_user where umail LIKE %s order by ucreate_date desc limit " \
                                      "%s, 10 "
                        sql_query_2 = "SELECT COUNT(*) FROM skdevsec_user where umail LIKE %s"

                        # DB에 명령문 전송
                        cursor_count.execute(sql_query_2, ('%' + usearch + '%',))
                        count = cursor_count.fetchone()

                        cursor_data.execute(sql_query_1, ('%' + usearch + '%', upage*10-10,))
                        data = cursor_data.fetchone()

                    else:
                        return Response(0)

                    # 데이터가 있으면
                    if data is not None:
                        # 데이터 만큼 반복
                        while data:
                            new_data_in = dict()
                            new_data_in['uid'] = data[0]
                            new_data_in['unickname'] = data[2]
                            new_data_in['uname'] = data[3]
                            new_data_in['umail'] = data[4]
                            new_data_in['uphone'] = data[5]
                            new_data_in['ucreate_date'] = data[6]
                            new_data_in['authority'] = int(data[7])
                            new_data.append(new_data_in)
                            data = cursor_data.fetchone()
                    # 데이터가 없으면
                    else:
                        # DB와 접속 종료
                        connection.close()
                        # 프론트엔드에 0 전송
                        return Response(0)

                    if count is not None:
                        new_data.append({"user_count": count[0]})
                    else:
                        new_data.append({"user_count": 0})

                    # DB와 접속 종료
                    connection.close()

            # 에러가 발생했을 경우 백엔드에 에러 내용 출력 및 프론트엔드에 0 전송
            except Exception as e:
                connection.rollback()
                print(f"에러: {e}")
                return Response(0)

            # 데이터 저장 완료 시, 프론트엔드에 데이터 전송
            else:
                return Response(new_data)
        # 관리자가 아니면 프론트엔드에 0 전송
        else:
            return Response(0)

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
            authority = int(request.data['authority'])

            p_name = re.compile('[~!@#$%^&*()_+|<>?:{}=,/`;-]')
            p_id = re.compile('^[a-zA-Z0-9]*$')
            p_pwd_1 = re.compile('(?=.*[0-9])(?=.*[a-z])(?=.*[A-Z]).*$')
            p_pwd_2 = re.compile('[~!@#$%^&*()_+|<>?:{}=,/`;-]')
            p_mail = re.compile('[~!#$%^&*()+|<>?:{}=,/`;-]')
            p_nickname = re.compile('[~!@#$%^&*()_+|<>?:{}=,/`;-]')
            p_phone = re.compile('^[0-9]*$')

            m_name = p_name.search(uname)
            m_id = p_id.search(uid)
            m_pwd_1 = p_pwd_1(upwd)
            m_pwd_2 = p_pwd_2(upwd)
            m_mail = p_mail(umail)
            m_nickname = p_nickname(unickname)
            m_phone = p_phone(uphone)

            if m_name:
                return Response(0)
            elif not m_id:
                return Response(0)
            elif m_pwd_1:
                return Response(0)
            elif m_pwd_2:
                return Response(0)
            elif m_mail:
                return Response(0)
            elif m_nickname:
                return Response(0)
            elif not m_phone:
                return Response(0)
            else:
                # SQL 쿼리문 작성
                sql_query = "INSERT INTO skdevsec_user VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"

                # DB에 명령문 전송
                cursor.execute(sql_query, (uid, upwd, unickname, uname, umail, uphone, ucreate_date, authority))

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

    # 아이디 중복
    @action(detail=False, methods=['POST'])
    def id_check(self, request):
        try:
            # DB 접근할 cursor
            cursor = connection.cursor()

            # POST 메소드로 날라온 Request의 데이터 각각 추출
            uid = request.data['uid']

            p_id = re.compile('^[a-zA-Z0-9]*$')

            m_id = p_id.search(uid)

            if not m_id:
                return Response(1)
            else:
                # SQL 쿼리문 작성
                sql_query = "SELECT * FROM skdevsec_user WHERE uid=%s"

                # DB에 명령문 전송
                cursor.execute(sql_query, (uid, ))
                data = cursor.fetchone()

                # DB와 접속 종료
                connection.close()

        # 에러가 발생했을 경우 백엔드에 에러 내용 출력 및 프론트엔드에 0 전송
        except Exception as e:
            connection.rollback()
            print(f"id_check 에러: {e}")
            return Response(0)

        # 데이터가 존재하면(중복이면) 프론트엔드 1을 전송 아니면 0을 전송
        else:
            if data is not None:
                return Response(1)
            else:
                return Response(0)

    # 닉네임 중복
    @action(detail=False, methods=['POST'])
    def nickname_check(self, request):
        try:
            # DB 접근할 cursor
            cursor = connection.cursor()

            # POST 메소드로 날라온 Request의 데이터 각각 추출:
            unickname = request.data['unickname']

            p = re.compile('[~!@#$%^&*()_+|<>?:{}=,/`;-]')
            m = p.search(unickname)

            if m:
                return Response(1)
            else:
                # SQL 쿼리문 작성
                sql_query = "SELECT * FROM skdevsec_user WHERE unickname=%s"

                # DB에 명령문 전송
                cursor.execute(sql_query, (unickname, ))
                data = cursor.fetchone()

                # DB와 접속 종료
                connection.close()

        # 에러가 발생했을 경우 백엔드 에러 내용 출력 및 프론트엔드에 0 전송
        except Exception as e:
            connection.rollback()
            print(f"에러: {e}")
            return Response(0)

        # 데이터가 존재하면(중복이면) 프론트엔드에 1을 전송 아니면 0을 전송
        else:
            if data is not None:
                return Response(1)
            else:
                return Response(0)

    # 이메일 중복 체크 및 인증 메일 전송
    @action(detail=False, methods=['POST'])
    def email_check(self, request):
        try:
            # DB 접근할 cursor
            cursor = connection.cursor()

            # POST 메소드로 날라온 Request의 데이터 각각 추출
            umail = request.data['umail']
            print(umail)

            p = re.compile('[~!#$%^&*()+|<>?:{}=,/`;-]')

            m = p.search(umail)

            print(m)
            if m:
                return Response(1)
            else:
                # SQL 쿼리문 작성
                sql_query = "SELECT * FROM skdevsec_user WHERE umail=%s"

                # DB에 명령문 전송
                cursor.execute(sql_query, (umail, ))
                data = cursor.fetchone()

                # DB와 접속 종료
                connection.close()

        # 에러가 발생했을 경우 백엔드에 에러 내용 출력 및 프론트엔드에 0 전송
        except Exception as e:
            connection.rollback()
            print(f"에러: {e}")
            return Response(0)

        # 데이터가 존재하면(중복이면) 프론트엔드에 1을 전송 아니면 이메일 전송 작업 시작
        else:
            if data is not None:
                return Response(1)
            else:
                try:
                    pw_candidate = string.ascii_lowercase + string.digits
                    authentication_number = ''

                    for i in range(8):
                        authentication_number += random.choice(pw_candidate)

                    # 이메일 제목, 내용, 보내는 사람, 받을 사람, 옵션 순서
                    send_mail("이메일 인증을 완료해주십시오.", f"인증번호 : {authentication_number}", EMAIL_HOST_USER, [umail], fail_silently=False)

                    # 프론트 엔드에 인증번호 전송
                    return Response(authentication_number)

                # 에러가 발생했을 경우 백엔드에 에러 내용 출력 및 프론트엔드에 0 전송
                except Exception as e:
                    connection.rollback()
                    print(f"에러: {e}")
                    return Response(0)

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
            sql_query_1 = "SELECT * FROM skdevsec_user WHERE uid=%s and upwd=%s"

            # DB에 명령문 전송
            cursor.execute(sql_query_1, (uid, upwd))
            data = cursor.fetchone()

            # 불러온 데이터를 딕셔너리 형태로 저장
            if data is not None:
                new_data['unickname'] = data[2]
                new_data['authority'] = int(data[7])
            else:
                try:
                    sql_query_2 = "UPDATE skdevsec_user SET ulock=ulock+1 WHERE uid=%s"
                    cursor.execute(sql_query_2, (uid, ))
                    connection.commit()
                    connection.close()

                except Exception as e:
                    connection.rollback()
                    print(f"에러: {e}")
                    return Response(0)

                return Response(0)

            # DB와 접속 종료
            connection.close()

        # 에러가 발생했을 경우 백엔드에 에러 내용 출력 및 프론트엔드에 0 전송
        except Exception as e:
            connection.rollback()
            print(f"에러: {e}")
            return Response(0)

        # 관리자 로그인이면 2 일반 사용자이면 1 로그인 실패면 0을 프론트엔드에 전송
        else:
            if new_data['authority'] == 1:
                new_data['login_check'] = 2
                return Response({'unickname': new_data['unickname'], 'login_check': new_data['login_check']})
            else:
                new_data['login_check'] = 1
                return Response({'unickname': new_data['unickname'], 'login_check': new_data['login_check']})

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
            sql_query = "SELECT * FROM skdevsec_user WHERE unickname=%s"

            # DB에 명령문 전송
            cursor.execute(sql_query, (unickname, ))
            data = cursor.fetchone()

            # DB와 접속 종료
            connection.close()

            # 정보를 딕셔너리 형태로 저장
            if data is not None:
                new_data['uid'] = data[0]
                new_data['unickname'] = data[2]
                new_data['uname'] = data[3]
                new_data['umail'] = data[4]
                new_data['uphone'] = data[5]
                new_data['ucreate_date'] = data[6]
            else:
                return Response(0)

        # 에러가 발생했을 경우 백엔드에 에러 내용 출력 및 프론트엔드에 0 전송
        except Exception as e:
            connection.rollback()
            print(f"에러: {e}")
            return Response(0)

        # 데이터가 있으면 프론트엔드에 데이터 전송 없으면 0 전송
        else:
            return Response(new_data)

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
            sql_query = "SELECT * FROM skdevsec_user WHERE unickname=%s and upwd =%s"

            # DB에 명령문 전송
            cursor.execute(sql_query, (unickname, upwd,))
            data = cursor.fetchone()

            # DB와 접속 종료
            connection.close()

        # 에러가 발생했을 경우 백엔드에 에러 내용 출력 및 프론트엔드에 0 전송
        except Exception as e:
            connection.rollback()
            print(f"에러: {e}")
            return Response(0)

        # 데이터가 존재하면 1, 없으면 0을 프론트엔드에 전송
        else:
            if data is not None:
                return Response(1)
            else:
                return Response(0)

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

            p_nickname = re.compile('[~!@#$%^&*()_+|<>?:{}=,/`;-]')
            p_mail = re.compile('[~!#$%^&*()+|<>?:{}=,/`;-]')
            p_phone = re.compile('^[0-9]*$')

            m_nickname = p_nickname(unickname)
            m_mail = p_mail(umail)
            m_phone = p_phone(uphone)

            if m_nickname:
                return Response(0)
            elif m_mail:
                return Response(0)
            elif m_phone:
                return Response(0)
            else:
                # SQL 쿼리문 작성
                sql_query = "UPDATE skdevsec_user SET unickname=%s, umail=%s, uphone=%s WHERE uid=%s"

                # DB에 명령문 전송
                cursor.execute(sql_query, (unickname, umail, uphone, uid))

                # DB와 접속 종료
                connection.commit()
                connection.close()

        # 에러가 발생했을 경우 백엔드에 에러 내용 출력 및 프론트엔드에 0 전송
        except Exception as e:
            connection.rollback()
            print(f"에러: {e}")
            return Response(0)

        # 성공하면 프론트엔드에 0 전송
        else:
            return Response(1)

    # 비밀번호 변경
    @action(detail=False, methods=['POST'])
    def change_pwd(self, request):
        try:
            # DB 접근할 cursor
            cursor = connection.cursor()

            # POST 메소드로 날라온 Request의 데이터 각각 추출
            unickname = request.data['unickname']
            upwd = request.data['upwd']

            p_pwd_1 = re.compile('(?=.*[0-9])(?=.*[a-z])(?=.*[A-Z]).*$')
            p_pwd_2 = re.compile('[~!@#$%^&*()_+|<>?:{}=,/`;-]')

            m_pwd_1 = p_pwd_1(upwd)
            m_pwd_2 = p_pwd_2(upwd)

            if m_pwd_1:
                return Response(0)
            elif m_pwd_2:
                return Response(0)
            else:
                # SQL 쿼리문 작성
                sql_query = "UPDATE skdevsec_user SET upwd=%s WHERE unickname=%s"

                # DB에 명령문 전송
                cursor.execute(sql_query, (upwd, unickname, ))

                # DB와 접속 종료
                connection.commit()
                connection.close()

        # 에러가 발생했을 경우 백엔드에 에러 내용 출력 및 프론트엔드에 0 전송
        except Exception as e:
            connection.rollback()
            print(f"에러: {e}")
            return Response(0)

        # 변경 완료 되면 프론트엔드에 1 전송
        else:
            return Response(1)

    # 회원 탈퇴
    @action(detail=False, methods=['POST'])
    def delete_user(self, request):
        try:
            # DB 접근할 cursor
            cursor = connection.cursor()

            # POST 메소드로 날라온 Request의 데이터 각각 추출
            unickname = request.data['unickname']

            # SQL 쿼리문 작성
            sql_query = "DELETE FROM skdevsec_user WHERE unickname=%s"

            # DB에 명령문 전송
            cursor.execute(sql_query, (unickname, ))

            # DB와 접속 종료
            connection.commit()
            connection.close()

        # 에러가 발생했을 경우 백엔드에 에러 내용 출력 및 프론트엔드에 0 전송
        except Exception as e:
            connection.rollback()
            print(f"에러: {e}")
            return Response(0)

        # 삭제 되면 프론트엔드에 1 전송
        else:
            return Response(1)

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
            sql_query = "SELECT * FROM skdevsec_user WHERE umail=%s AND uname=%s"

            # DB에 명령문 전송
            cursor.execute(sql_query, (umail, uname))
            data = cursor.fetchone()

            # DB와 접속 종료
            connection.close()

        # 에러가 발생했을 경우 백엔드에 에러 내용 출력 및 프론트엔드에 0 전송
        except Exception as e:
            connection.rollback()
            print(f"에러: {e}")
            return Response(0)

        # 데이터가 존재하지않으면 프론트엔드에 0을 전송 아니면 이메일 전송 작업 시작
        else:
            if data is None:
                return Response(0)
            else:
                try:
                    pw_candidate = string.ascii_lowercase + string.digits
                    authentication_number = ''

                    for i in range(8):
                        authentication_number += random.choice(pw_candidate)

                    # 이메일 제목, 내용, 보내는 사람, 받을 사람, 옵션 순서
                    send_mail("이메일 인증을 완료해주십시오.", f"인증번호 : {authentication_number}", EMAIL_HOST_USER, [umail],
                              fail_silently=False)

                    # 프론트 엔드에 인증번호 전송
                    return Response(authentication_number)

                    # 에러가 발생했을 경우 백엔드에 에러 내용 출력 및 프론트엔드에 0 전송
                except Exception as e:
                    connection.rollback()
                    print(f"에러: {e}")
                    return Response(0)

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
            sql_query = "SELECT * FROM skdevsec_user WHERE umail=%s AND uname=%s"

            # DB에 명령문 전송
            cursor.execute(sql_query, (umail, uname))
            data = cursor.fetchone()

            # DB와 접속 종료
            connection.close()

        # 에러가 발생했을 경우 백엔드에 에러 내용 출력 및 프론트엔드에 0 전송
        except Exception as e:
            connection.rollback()
            print(f"에러: {e}")
            return Response(0)

        # 데이터가 존재하면(중복이면) 프론트엔드에 1을 전송 아니면 이메일 전송 작업 시작
        else:
            if data is not None:
                return Response(data[0])
            else:
                return Response(0)

    # 비밀번호 찾기 전 핸드폰 인증
    @action(detail=False, methods=['POST'])
    def find_pwd_sms(self, request):
        try:
            # DB 접근할 cursor
            cursor = connection.cursor()

            # POST 메소드로 날라온 Request의 데이터 각각 추출
            uid = request.data['uid']
            uname = request.data['uname']

            sql_query = "SELECT * FROM skdevsec_user WHERE uid=%s AND uname=%s"

            # DB에 명령문 전송
            cursor.execute(sql_query, (uid, uname, ))
            data = cursor.fetchone()

            if data is not None:
                # 문자 전송
                authentication_number = sms_send(data[5])
            else:
                return Response(0)

            # DB와 접속 종료
            connection.close()

        # 에러가 발생했을 경우 백엔드에 에러 내용 출력 및 프론트엔드에 0 전송
        except Exception as e:
            connection.rollback()
            print(f"에러: {e}")
            return Response(0)
        # 성공 했을 시, 전송했던 인증 번호를 프론트엔드에 전달
        else:
            return Response(authentication_number)

    # 비밀번호 교체
    @action(detail=False, methods=['POST'])
    def find_pwd(self, request):
        try:
            # DB 접근할 cursor
            cursor = connection.cursor()

            # POST 메소드로 날라온 Request의 데이터 각각 추출
            uid = request.data['uid']
            upwd = request.data['upwd']

            p_pwd_1 = re.compile('(?=.*[0-9])(?=.*[a-z])(?=.*[A-Z]).*$')
            p_pwd_2 = re.compile('[~!@#$%^&*()_+|<>?:{}=,/`;-]')

            m_pwd_1 = p_pwd_1(upwd)
            m_pwd_2 = p_pwd_2(upwd)

            if m_pwd_1:
                return Response(0)
            elif m_pwd_2:
                return Response(0)
            else:
                sql_query = "UPDATE skdevsec_user SET upwd=%s WHERE uid=%s"

                # DB에 명령문 전송
                cursor.execute(sql_query, (upwd, uid, ))

                # DB와 접속 종료
                connection.commit()
                connection.close()

        # 에러가 발생했을 경우 백엔드에 에러 내용 출력 및 프론트엔드에 0 전송
        except Exception as e:
            connection.rollback()
            print(f"에러: {e}")
            return Response(0)
        # 성공 했을 시, 프론트에 1 전달
        else:
            return Response(1)
