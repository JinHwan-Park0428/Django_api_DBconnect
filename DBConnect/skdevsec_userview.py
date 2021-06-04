import json
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
import bcrypt
from datetime import datetime
from DBConnect.security import *
from urllib import parse
import base64


# 회원 정보 관련 테이블
class SkdevsecUserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = SkdevsecUser.objects.all()
    serializer_class = SkdevsecUserSerializer

    # 관리자 페이지 (회원 정보 보기)
    @action(detail=False, methods=['POST'])
    def admin_user_info(self, request):
        if request.data['authority'] == '1' and request.data['unickname'] == 'admin':
            new_data = list()

            try:
                upage = int(request.data['upage'])

                cursor = connection.cursor()

                sql_query_1 = "SELECT COUNT(*) FROM skdevsec_user"
                cursor.execute(sql_query_1)
                count = cursor.fetchone()

                if count is not None:
                    new_data.append({"user_count": count[0]})
                else:
                    new_data.append({"user_count": 0})

                strsql = "SELECT * FROM skdevsec_user order by ucreate_date desc limit %s, 10 "
                cursor.execute(strsql, (upage * 10 - 10,))
                data = cursor.fetchone()

                if data is not None:
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
                else:
                    connection.close()
                    return Response(0)

                connection.close()

            except Exception as e:
                connection.rollback()
                print(f"에러: {e}")
                return Response(0)

            else:
                return Response(new_data)

        else:
            return Response(0)

    # 관리자 페이지 (회원 정보 검색)
    @action(detail=False, methods=['POST'])
    def admin_user_search(self, request):
        if request.data['authority'] == '1' and request.data['unickname'] == 'admin':
            new_data = list()
            try:
                ucode = int(request.data['ucode'])
                usearch = request.data['usearch']
                upage = int(request.data['upage'])

                p = re.compile('[\{\}\[\]\/?.,;:|\)*~`!@^\-+<>\#$%&\\\=\(\'\"]')
                m = p.search(usearch)

                if m:
                    return Response(0)
                else:
                    cursor_count = connection.cursor()
                    cursor_data = connection.cursor()

                    # 0: 전체 검색 / 1 : 이름 / 2 : 닉네임 / 3 : 아이디 / 4 : 이메일
                    if ucode == 0:
                        sql_query_1 = "SELECT * FROM skdevsec_user where (uname LIKE %s OR unickname LIKE %s OR uid LIKE " \
                                      "%s OR umail LIKE %s) order by ucreate_date desc limit %s, 10"
                        sql_query_2 = "SELECT COUNT(*) FROM skdevsec_user where (uname LIKE %s OR unickname LIKE %s OR " \
                                      "uid LIKE %s OR umail LIKE %s)"
                        cursor_count.execute(sql_query_2,
                                             ('%' + usearch + '%', '%' + usearch + '%', '%' + usearch + '%',
                                              '%' + usearch + '%',))
                        count = cursor_count.fetchone()

                        cursor_data.execute(sql_query_1,
                                            ('%' + usearch + '%', '%' + usearch + '%', '%' + usearch + '%', '%'
                                             + usearch + '%', upage * 10 - 10,))
                        data = cursor_data.fetchone()

                    elif ucode == 1:
                        sql_query_1 = "SELECT * FROM skdevsec_user where uname LIKE %s order by ucreate_date desc limit " \
                                      "%s, 10 "
                        sql_query_2 = "SELECT COUNT(*) FROM skdevsec_user where uname LIKE %s"
                        cursor_count.execute(sql_query_2, ('%' + usearch + '%',))
                        count = cursor_count.fetchone()

                        cursor_data.execute(sql_query_1, ('%' + usearch + '%', upage * 10 - 10,))
                        data = cursor_data.fetchone()

                    elif ucode == 2:
                        sql_query_1 = "SELECT * FROM skdevsec_user where unickname LIKE %s order by ucreate_date desc " \
                                      "limit %s, 10 "
                        sql_query_2 = "SELECT COUNT(*) FROM skdevsec_user where unickname LIKE %s"
                        cursor_count.execute(sql_query_2, ('%' + usearch + '%',))
                        count = cursor_count.fetchone()

                        cursor_data.execute(sql_query_1, ('%' + usearch + '%', upage * 10 - 10,))
                        data = cursor_data.fetchone()

                    elif ucode == 3:
                        sql_query_1 = "SELECT * FROM skdevsec_user where uid LIKE %s order by ucreate_date desc limit %s, " \
                                      "10 "
                        sql_query_2 = "SELECT COUNT(*) FROM skdevsec_user where uid LIKE %s"
                        cursor_count.execute(sql_query_2, ('%' + usearch + '%',))
                        count = cursor_count.fetchone()

                        cursor_data.execute(sql_query_1, ('%' + usearch + '%', upage * 10 - 10,))
                        data = cursor_data.fetchone()

                    elif ucode == 4:
                        sql_query_1 = "SELECT * FROM skdevsec_user where umail LIKE %s order by ucreate_date desc limit " \
                                      "%s, 10 "
                        sql_query_2 = "SELECT COUNT(*) FROM skdevsec_user where umail LIKE %s"
                        cursor_count.execute(sql_query_2, ('%' + usearch + '%',))
                        count = cursor_count.fetchone()

                        cursor_data.execute(sql_query_1, ('%' + usearch + '%', upage * 10 - 10,))
                        data = cursor_data.fetchone()

                    else:
                        return Response(0)

                    if data is not None:
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
                    else:
                        connection.close()
                        return Response(0)

                    if count is not None:
                        new_data.append({"user_count": count[0]})
                    else:
                        new_data.append({"user_count": 0})

                    connection.close()

            except Exception as e:
                connection.rollback()
                print(f"에러: {e}")
                return Response(0)

            else:
                return Response(new_data)

        else:
            return Response(0)

    # 회원가입 함수
    @action(detail=False, methods=['POST'])
    def create_user(self, request):
        try:
            cursor = connection.cursor()

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
            m_pwd_1 = p_pwd_1.search(upwd)
            m_pwd_2 = p_pwd_2.search(upwd)
            m_mail = p_mail.search(umail)
            m_nickname = p_nickname.search(unickname)
            m_phone = p_phone.search(uphone)

            if m_name:
                return Response(0)
            elif not m_id:
                return Response(0)
            elif not m_pwd_1:
                return Response(0)
            elif not m_pwd_2:
                return Response(0)
            elif m_mail:
                return Response(0)
            elif m_nickname:
                return Response(0)
            elif not m_phone:
                return Response(0)
            else:

                hashed_password = bcrypt.hashpw(upwd.encode('utf-8'), bcrypt.gensalt())

                sql_query = "INSERT INTO skdevsec_user VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
                cursor.execute(sql_query,
                               (uid, hashed_password, unickname, uname, umail, uphone, ucreate_date, authority, 0))

                connection.commit()
                connection.close()

        except Exception as e:
            connection.rollback()
            print(f"에러: {e}")
            return Response(0)

        else:
            return Response(1)

    # 아이디 중복
    @action(detail=False, methods=['POST'])
    def id_check(self, request):
        try:
            cursor = connection.cursor()

            uid = request.data['uid']

            p_id = re.compile('^[a-zA-Z0-9]*$')
            m_id = p_id.search(uid)

            if not m_id:
                return Response(1)
            else:
                sql_query = "SELECT * FROM skdevsec_user WHERE uid=%s"
                cursor.execute(sql_query, (uid,))
                data = cursor.fetchone()

                connection.close()

        except Exception as e:
            connection.rollback()
            print(f"id_check 에러: {e}")
            return Response(0)

        else:
            if data is not None:
                return Response(1)
            else:
                return Response(0)

    # 닉네임 중복
    @action(detail=False, methods=['POST'])
    def nickname_check(self, request):
        try:
            cursor = connection.cursor()

            unickname = request.data['unickname']

            p = re.compile('[~!@#$%^&*()_+|<>?:{}=,/`;-]')
            m = p.search(unickname)

            if m:
                return Response(1)
            else:
                sql_query = "SELECT * FROM skdevsec_user WHERE unickname=%s"

                cursor.execute(sql_query, (unickname,))
                data = cursor.fetchone()

                connection.close()

        except Exception as e:
            connection.rollback()
            print(f"에러: {e}")
            return Response(0)

        else:
            if data is not None:
                return Response(1)
            else:
                return Response(0)

    # 이메일 중복 체크 및 인증 메일 전송
    @action(detail=False, methods=['POST'])
    def email_check(self, request):
        try:
            cursor = connection.cursor()

            umail = request.data['umail']

            p = re.compile('[~!#$%^&*()+|<>?:{}=,/`;-]')
            m = p.search(umail)

            if m:
                return Response(1)
            else:
                sql_query = "SELECT * FROM skdevsec_user WHERE umail=%s"
                cursor.execute(sql_query, (umail,))
                data = cursor.fetchone()

                connection.close()

        except Exception as e:
            connection.rollback()
            print(f"에러: {e}")
            return Response(0)

        else:
            if data is not None:
                return Response(1)
            else:
                try:
                    pw_candidate = string.ascii_lowercase + string.digits
                    authentication_number = ''

                    for i in range(8):
                        authentication_number += random.choice(pw_candidate)

                    send_mail("이메일 인증을 완료해주십시오.", f"인증번호 : {authentication_number}", EMAIL_HOST_USER, [umail],
                              fail_silently=False)

                    return Response(authentication_number)

                except Exception as e:
                    connection.rollback()
                    print(f"에러: {e}")
                    return Response(0)

    # 로그인
    @action(detail=False, methods=['POST'])
    def login(self, request):
        new_data = dict()
        string_key = '000000000@fsadqega#fkdlsaiqu1235'

        try:

            cursor = connection.cursor()

            decrypted_data = decrypt(request.data[0], string_key)
            decrypted_data = json.loads(decrypted_data)

            print(decrypted_data)

            uid = decrypted_data[0]['uid']
            upwd = decrypted_data[0]['upwd']

            sql_query_1 = "SELECT * FROM skdevsec_user WHERE uid=%s"
            cursor.execute(sql_query_1, (uid,))
            data = cursor.fetchone()

            print(data)

            if data is not None:
                if bcrypt.checkpw(upwd.encode('utf-8'), data[1].encode('utf-8')):
                    if uid == 'admin':
                        rnd = random.randint(100, 1000)
                    else:
                        rnd = random.randint(1000, 10000)

                    # token_data = json.dumps({'unickname': data[2],
                    #                          'level': str(rnd),
                    #                          'login_date': str(
                    #                              datetime.today().strftime("%Y%m%d%H%M"))})
                    # token = encrypt(token_data, string_key)

                    connection.close()

                    new_data['unickname'] = data[2]
                    new_data['authority'] = data[7]
                    new_data['ulock'] = data[8]

                    if new_data['authority'] == 1:
                        new_data['login_check'] = 2
                        token_data = json.dumps({'unickname': new_data['unickname'],
                                                 'login_check': new_data['login_check'], 'ulock': new_data['ulock']})

                        token = encrypt(token_data, string_key)

                        try:
                            sql_query_2 = "UPDATE skdevsec_user SET ulock=0 WHERE uid=%s"
                            cursor.execute(sql_query_2, (uid,))

                        except Exception as e:
                            connection.rollback()
                            print(f"에러: {e}")

                            error_num = '0'
                            error = encrypt(error_num, string_key)
                            return Response(error)

                        return Response(token.decode('utf-8'))

                    else:
                        new_data['login_check'] = 1
                        token_data = json.dumps({'unickname': new_data['unickname'],
                                                 'login_check': new_data['login_check'], 'ulock': new_data['ulock']})
                        token = encrypt(token_data, string_key)

                        try:
                            sql_query_2 = "UPDATE skdevsec_user SET ulock=0 WHERE uid=%s"
                            cursor.execute(sql_query_2, (uid,))

                        except Exception as e:
                            connection.rollback()
                            print(f"에러: {e}")

                            error_num = '0'
                            error = encrypt(error_num, string_key)
                            return Response(error)

                        return Response(token.decode('utf-8'))

                else:
                    try:
                        sql_query_3 = "UPDATE skdevsec_user SET ulock=ulock+1 WHERE uid=%s"
                        cursor.execute(sql_query_3, (uid,))

                    except Exception as e:
                        connection.rollback()
                        print(f"에러: {e}")

                        error_num = '0'
                        error = encrypt(error_num, string_key)
                        return Response(error)

                    else:
                        connection.commit()
                        connection.close()

                        error_num = '0'
                        error = encrypt(error_num, string_key)
                        return Response(error)
            else:
                error_num = '0'
                error = encrypt(error_num, string_key)
                return Response(error)

        except Exception as e:
            connection.rollback()
            print(f"에러: {e}")

            error_num = '0'
            error = encrypt(error_num, string_key)
            return Response(error)

    # 내 정보 보기
    @action(detail=False, methods=['POST'])
    def view_info(self, request):
        new_data = dict()

        try:
            cursor = connection.cursor()

            unickname = request.data['unickname']

            sql_query = "SELECT * FROM skdevsec_user WHERE unickname=%s"
            cursor.execute(sql_query, (unickname,))
            data = cursor.fetchone()

            connection.close()

            if data is not None:
                new_data['uid'] = data[0]
                new_data['unickname'] = data[2]
                new_data['uname'] = data[3]
                new_data['umail'] = data[4]
                new_data['uphone'] = data[5]
                new_data['ucreate_date'] = data[6]
            else:
                return Response(0)

        except Exception as e:
            connection.rollback()
            print(f"에러: {e}")
            return Response(0)

        else:
            return Response(new_data)

    # 회원 정보 수정 인증
    @action(detail=False, methods=['POST'])
    def before_change(self, request):
        try:
            cursor = connection.cursor()

            unickname = request.data['unickname']
            upwd = request.data['upwd']

            sql_query = "SELECT * FROM skdevsec_user WHERE unickname=%s and upwd =%s"

            cursor.execute(sql_query, (unickname, upwd,))
            data = cursor.fetchone()

            connection.close()

        except Exception as e:
            connection.rollback()
            print(f"에러: {e}")
            return Response(0)

        else:
            if data is not None:
                return Response(1)
            else:
                return Response(0)

    # 내 정보 수정하기
    @action(detail=False, methods=['POST'])
    def change_info(self, request):
        try:
            cursor = connection.cursor()

            uid = request.data['uid']
            unickname = request.data['unickname']
            umail = request.data['umail']
            uphone = request.data['uphone']

            p_nickname = re.compile('[~!@#$%^&*()_+|<>?:{}=,/`;-]')
            p_mail = re.compile('[~!#$%^&*()+|<>?:{}=,/`;-]')
            p_phone = re.compile('^[0-9]*$')

            m_nickname = p_nickname.search(unickname)
            m_mail = p_mail.search(umail)
            m_phone = p_phone.search(uphone)

            if m_nickname:
                return Response(0)
            elif m_mail:
                return Response(0)
            elif not m_phone:
                return Response(0)
            else:
                sql_query = "UPDATE skdevsec_user SET unickname=%s, umail=%s, uphone=%s WHERE uid=%s"
                cursor.execute(sql_query, (unickname, umail, uphone, uid))

                connection.commit()
                connection.close()

        except Exception as e:
            connection.rollback()
            print(f"에러: {e}")
            return Response(0)

        else:
            return Response(1)

    # 비밀번호 변경
    @action(detail=False, methods=['POST'])
    def change_pwd(self, request):
        try:
            cursor = connection.cursor()

            unickname = request.data['unickname']
            upwd = request.data['upwd']

            p_pwd_1 = re.compile('(?=.*[0-9])(?=.*[a-z])(?=.*[A-Z]).*$')
            p_pwd_2 = re.compile('[~!@#$%^&*()_+|<>?:{}=,/`;-]')

            m_pwd_1 = p_pwd_1.search(upwd)
            m_pwd_2 = p_pwd_2.search(upwd)

            if not m_pwd_1:
                return Response(0)
            elif not m_pwd_2:
                return Response(0)
            else:
                sql_query = "UPDATE skdevsec_user SET upwd=%s WHERE unickname=%s"
                cursor.execute(sql_query, (upwd, unickname,))

                connection.commit()
                connection.close()

        except Exception as e:
            connection.rollback()
            print(f"에러: {e}")
            return Response(0)

        else:
            return Response(1)

    # 회원 탈퇴
    @action(detail=False, methods=['POST'])
    def delete_user(self, request):
        try:
            cursor = connection.cursor()

            unickname = request.data['unickname']

            sql_query = "DELETE FROM skdevsec_user WHERE unickname=%s"
            cursor.execute(sql_query, (unickname,))

            connection.commit()
            connection.close()

        except Exception as e:
            connection.rollback()
            print(f"에러: {e}")
            return Response(0)

        else:
            return Response(1)

    # 아이디 찾기 전 이메일 인증
    @action(detail=False, methods=['POST'])
    def find_id_email(self, request):
        try:
            cursor = connection.cursor()

            uname = request.data['uname']
            umail = request.data['umail']

            # SQL 쿼리문 작성
            sql_query = "SELECT * FROM skdevsec_user WHERE umail=%s AND uname=%s"

            cursor.execute(sql_query, (umail, uname))
            data = cursor.fetchone()

            connection.close()

        except Exception as e:
            connection.rollback()
            print(f"에러: {e}")
            return Response(0)

        else:
            if data is None:
                return Response(0)
            else:
                try:
                    pw_candidate = string.ascii_lowercase + string.digits
                    authentication_number = ''

                    for i in range(8):
                        authentication_number += random.choice(pw_candidate)

                    send_mail("이메일 인증을 완료해주십시오.", f"인증번호 : {authentication_number}", EMAIL_HOST_USER, [umail],
                              fail_silently=False)

                    return Response(authentication_number)

                except Exception as e:
                    connection.rollback()
                    print(f"에러: {e}")
                    return Response(0)

    # 아이디 찾기
    @action(detail=False, methods=['POST'])
    def find_id(self, request):
        try:
            cursor = connection.cursor()

            uname = request.data['uname']
            umail = request.data['umail']

            sql_query = "SELECT * FROM skdevsec_user WHERE umail=%s AND uname=%s"
            cursor.execute(sql_query, (umail, uname))
            data = cursor.fetchone()

            connection.close()

        except Exception as e:
            connection.rollback()
            print(f"에러: {e}")
            return Response(0)

        else:
            if data is not None:
                return Response(data[0])
            else:
                return Response(0)

    # 비밀번호 찾기 전 핸드폰 인증
    @action(detail=False, methods=['POST'])
    def find_pwd_sms(self, request):
        try:
            cursor = connection.cursor()

            uid = request.data['uid']
            uname = request.data['uname']

            sql_query = "SELECT * FROM skdevsec_user WHERE uid=%s AND uname=%s"
            cursor.execute(sql_query, (uid, uname,))
            data = cursor.fetchone()

            if data is not None:
                authentication_number = sms_send(data[5])
            else:
                return Response(0)

            connection.close()

        except Exception as e:
            connection.rollback()
            print(f"에러: {e}")
            return Response(0)

        else:
            return Response(authentication_number)

    # 비밀번호 교체
    @action(detail=False, methods=['POST'])
    def find_pwd(self, request):
        try:
            cursor = connection.cursor()

            uid = request.data['uid']
            upwd = request.data['upwd']

            p_pwd_1 = re.compile('(?=.*[0-9])(?=.*[a-z])(?=.*[A-Z]).*$')
            p_pwd_2 = re.compile('[~!@#$%^&*()_+|<>?:{}=,/`;-]')

            m_pwd_1 = p_pwd_1.search(upwd)
            m_pwd_2 = p_pwd_2.search(upwd)

            if not m_pwd_1:
                return Response(0)
            elif not m_pwd_2:
                return Response(0)
            else:
                sql_query = "UPDATE skdevsec_user SET upwd=%s WHERE uid=%s"
                cursor.execute(sql_query, (upwd, uid,))

                connection.commit()
                connection.close()

        except Exception as e:
            connection.rollback()
            print(f"에러: {e}")
            return Response(0)

        else:
            return Response(1)
