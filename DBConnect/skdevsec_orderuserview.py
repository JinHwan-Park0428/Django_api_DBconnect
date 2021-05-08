# 필요한 모듈 임포트
from random import *
from django.db import connection
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from DBConnect.serializers import *
from . import sms_send
import requests
import json

global_unickname = ''
global_oname = ''
global_ophone = ''
global_oaddress = ''
global_order_date = ''
global_oprice = ''
global_product = dict()
global_bagcode = ''


# 결제 기록 테이블
# 카카오 페이 admin key : 28743e8e95f287447491df3d2ea26c22
class SkdevsecOrderuserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = SkdevsecOrderuser.objects.all()
    serializer_class = SkdevsecOrderuserSerializer

    # 결제 전 핸드폰 인증
    @action(detail=False, methods=['POST'])
    def send_sms(self, request):
        try:
            # POST 메소드로 날라온 Request의 데이터 각각 추출
            ophone = request.data['ophone']

            # 문자 전송
            rand_num = sms_send(ophone)

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
    # 결제 데이터 임시 저장
    @action(detail=False, methods=['POST'])
    def temp_pay_info(self, request):
        try:
            global global_product
            # POST 메소드로 날라온 Request의 데이터 각각 추출
            # print(request.data)
            # temp = request.data
            # if len(temp[0].keys()) > 2 :
            global_product = request.data

        # 에러가 발생했을 경우 백엔드에 에러 내용 출력 및 프론트엔드에 0 전송
        except Exception as e:
            connection.rollback()
            print(f"temp_pay_info 에러: {e}")
            return Response(0)
        else:
            return Response(1)

    # sql 인젝션 되는 코드
    # 결제 기능
    @action(detail=False, methods=['POST'])
    def kakaopay(self, request):
        try:
            global global_unickname, global_oname, global_ophone, global_oaddress, global_order_date, global_oprice, global_bagcode

            # POST 메소드로 날라온 Request의 데이터 각각 추출
            global_unickname = request.data['unickname']
            global_oname = request.data['oname']
            global_ophone = request.data['ophone']
            global_oaddress = request.data['oaddress']
            global_order_date = request.data['order_date']
            global_oprice = request.data['oprice']
            global_bagcode = request.data['bagcode']

            # Kakao Pay 결제 API
            url = "https://kapi.kakao.com"
            headers = {
                'Authorization': "KakaoAK " + "28743e8e95f287447491df3d2ea26c22",
                'Content-type': 'application/x-www-form-urlencoded;charset=utf-8',
            }
            params = {
                'cid': "TC0ONETIME",
                'partner_order_id': randint(1, 99999999999),
                'partner_user_id': global_oname,
                'item_name': '결제 상품(들)',
                'quantity': 1,
                'total_amount': global_oprice,
                'vat_amount': 0,
                'tax_free_amount': 0,
                'approval_url': 'http://localhost:8080/item/ordersuccess',
                'fail_url': 'http://10.60.15.210:8000',
                'cancel_url': 'http://10.60.15.210:8000',
            }
            response = requests.post(url + "/v1/payment/ready", params=params, headers=headers)
            response = json.loads(response.text)

        # 에러가 발생했을 경우 백엔드에 에러 내용 출력 및 프론트엔드에 0 전송
        except Exception as e:
            print(f"kakaopay 에러: {e}")
            return Response(0)

        # 성공 했을 시, 프론트엔드에 데이터 전송
        else:
            return Response(response)

    # sql 인젝션 되는 코드
    # 결제 성공
    @action(detail=False, methods=['POST'])
    def pay_success(self, request):
        try:
            # DB 접근할 cursor
            cursor = connection.cursor()

            # SQL 쿼리문 작성
            strsql = "SELECT uid FROM skdevsec_user WHERE unickname='" + global_unickname + "'"

            # DB에 명령문 전송
            cursor.execute(strsql)
            uid = cursor.fetchone()

            # SQL 쿼리문 작성
            strsql1 = "INSERT INTO skdevsec_orderuser(uid, oname, ophone, oaddress, order_date, oprice) VALUES('" + str(
                uid[0]) + "', '" + global_oname + "', '" + str(
                global_ophone) + "', '" + global_oaddress + "', '" + global_order_date + "', '" + str(
                global_oprice) + "')"

            # DB에 명령문 전송
            cursor.execute(strsql1)
            connection.commit()

            try:
                for temp_dict in global_product:
                    temp_list = list()
                    for value in temp_dict.values():
                        temp_list.append(value)

                    strsql2 = "UPDATE skdevsec_product SET pcount=pcount-'" + str(temp_list[1]) + "' WHERE pid='" + str(
                        temp_list[0]) + "'"

                    # DB에 명령문 전송
                    cursor.execute(strsql2)
                    connection.commit()

                    pname, pcate, pprice = '', '', ''

                    # SQL 쿼리문 작성
                    strsql3 = "SELECT pname, pcate, pprice FROM skdevsec_product WHERE pid='" + str(temp_list[0]) + "'"

                    # DB에 명령문 전송
                    cursor.execute(strsql3)
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
                    strsql4 = "SELECT oid FROM skdevsec_orderuser WHERE uid='" + str(uid[0]) + "' ORDER BY oid DESC"

                    # DB에 명령문 전송
                    cursor.execute(strsql4)
                    oid = cursor.fetchall()

                    # 데이터가 있으면
                    if len(oid) != 0:
                        # SQL 쿼리문 작성
                        strsql5 = "INSERT INTO skdevsec_orderproduct(oid, pname, pcate, pprice, pcount) VALUES('" + str(
                            oid[0][0]) + "', '" + str(pname) + "', '" + str(pcate) + "', '" + str(
                            pprice) + "', '" + str(temp_list[1]) + "')"

                        # DB에 명령문 전송
                        cursor.execute(strsql5)

                    # 데이터가 없으면
                    else:
                        # DB와 접속 종료
                        connection.commit()
                        connection.close()
                        # 프론트엔드로 0 전송
                        return Response(0)

            except Exception as e:
                connection.rollback()
                print(f"pay_success 에러: {e}")
                return Response(0)

            else:
                if global_bagcode == "1":
                    strsql6 = "DELETE FROM skdevsec_bag WHERE uid='" + uid[0] + "'"
                    cursor.execute(strsql6)

            # DB와 접속 종료
            connection.commit()
            connection.close()

        # 에러가 발생했을 경우 백엔드에 에러 내용 출력 및 프론트엔드에 0 전송
        except Exception as e:
            connection.rollback()
            print(f"pay_success 에러: {e}")
            return Response(0)

        # 성공 했을 시, 프론트엔드에 데이터 전송
        else:
            return Response(1)

    # sql 인젝션 되는 코드
    # 결제 결과 전부 출력
    @action(detail=False, methods=['POST'])
    def admin_paid_output(self, request):
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
            strsql1 = "SELECT oid, uid, oname, ophone, oaddress, order_date, oprice FROM skdevsec_orderuser order by oid desc limit " + str(
                opage * 10 - 10) + ", 10"

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
            print(f"user_paid_output 에러: {e}")
            return Response(0)

        # 성공 했을 시, 프론트엔드에 데이터 전송
        else:
            return Response(new_data)

    # sql 인젝션 되는 코드
    # 결제 결과 유저꺼 출력
    @action(detail=False, methods=['POST'])
    def user_paid_output(self, request):
        # 데이터 저장을 위한 리스트 선언
        new_data = list()
        try:
            # DB 접근할 cursor
            cursor = connection.cursor()
            cursor1 = connection.cursor()

            # POST 메소드로 날라온 Request의 데이터 각각 추출
            unickname = request.data['unickname']
            opage = request.data['opage']
            opage = int(opage)

            # SQL 쿼리문 작성
            strsql = "SELECT uid FROM skdevsec_user where unickname='" + unickname + "'"

            # DB에 명령문 전송
            cursor.execute(strsql)
            uid = cursor.fetchone()

            # SQL 쿼리문 작성
            strsql1 = "SELECT COUNT(*) FROM skdevsec_orderuser where uid='" + uid[0] + "'"

            # DB에 명령문 전송
            cursor.execute(strsql1)
            count = cursor.fetchone()

            # 주문 내역 갯수 저장
            new_data.append({"order_count": count[0]})

            # SQL 쿼리문 작성
            strsql1 = "SELECT * FROM skdevsec_orderuser WHERE uid='" + uid[0] + "' order by oid desc limit " + str(opage * 10 - 10) + ", 10"

            # DB에 명령문 전송
            cursor.execute(strsql1)
            datas = cursor.fetchone()

            # 데이터가 있으면
            if datas is not None:
                # 데이터 수만큼 반복
                while datas:
                    strsql2 = "SELECT pname, COUNT(pname) FROM skdevsec_orderproduct WHERE oid='" + str(datas[0]) + "'"
                    cursor1.execute(strsql2)
                    pnames = cursor1.fetchone()
                    print(pnames)
                    new_data_in = dict()
                    new_data_in['pname'] = pnames[0]
                    new_data_in['product_count'] = pnames[1]
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
            print(f"user_paid_output 에러: {e}")
            return Response(0)

        # 성공 했을 시, 프론트엔드에 데이터 전송
        else:
            return Response(new_data)

    # sql 인젝션 되는 코드
    # 결제 내역 날짜 검색
    @action(detail=False, methods=['POST'])
    def user_paid_date(self, request):
        # 데이터 저장을 위한 리스트 선언
        new_data = list()
        try:
            # DB 접근할 cursor
            cursor = connection.cursor()
            cursor1 = connection.cursor()

            # POST 메소드로 날라온 Request의 데이터 각각 추출
            unickname = request.data['unickname']
            start_date = request.data['start_date']
            end_date = request.data['end_date'] + " 23:59"
            opage = request.data['opage']
            opage = int(opage)

            # SQL 쿼리문 작성
            strsql = "SELECT uid FROM skdevsec_user where unickname='" + unickname + "'"

            # DB에 명령문 전송
            cursor.execute(strsql)
            uid = cursor.fetchone()

            # SQL 쿼리문 작성
            strsql1 = "SELECT COUNT(*) FROM skdevsec_orderuser where uid='" + uid[0] + "' AND (order_date BETWEEN '" + start_date + "' AND '" + end_date + "')"

            print(strsql1)
            # DB에 명령문 전송
            cursor.execute(strsql1)
            count = cursor.fetchone()

            # 주문 내역 갯수 저장
            new_data.append({"order_count": count[0]})

            # SQL 쿼리문 작성
            strsql1 = "SELECT * FROM skdevsec_orderuser WHERE uid='" + uid[0] + "' AND (order_date BETWEEN '" + start_date + "' AND '" + end_date + "') order by oid desc limit " + str(opage * 10 - 10) + ", 10"

            # DB에 명령문 전송
            cursor.execute(strsql1)
            datas = cursor.fetchone()

            # 데이터가 있으면
            if datas is not None:
                # 데이터 수만큼 반복
                while datas:
                    strsql2 = "SELECT pname, COUNT(pname) FROM skdevsec_orderproduct WHERE oid='" + str(datas[0]) + "'"
                    cursor1.execute(strsql2)
                    pnames = cursor1.fetchone()
                    new_data_in = dict()
                    new_data_in['pname'] = pnames[0]
                    new_data_in['product_count'] = pnames[1]
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
            print(f"user_paid_date 에러: {e}")
            return Response(0)

        # 성공 했을 시, 프론트엔드에 데이터 전송
        else:
            return Response(new_data)

    # sql 인젝션 되는 코드
    # 결제 내역 날짜 조건 검색
    @action(detail=False, methods=['POST'])
    def user_paid_date_code(self, request):
        # 데이터 저장을 위한 리스트 선언
        new_data = list()
        try:
            # DB 접근할 cursor
            cursor = connection.cursor()
            cursor1 = connection.cursor()

            # POST 메소드로 날라온 Request의 데이터 각각 추출
            unickname = request.data['unickname']
            ocode = request.data['ocode']
            opage = request.data['opage']
            opage = int(opage)

            # SQL 쿼리문 작성
            strsql = "SELECT uid FROM skdevsec_user where unickname='" + unickname + "'"

            # DB에 명령문 전송
            cursor.execute(strsql)
            uid = cursor.fetchone()

            if ocode == "1":
                # SQL 쿼리문 작성
                strsql1 = "SELECT COUNT(*) FROM skdevsec_orderuser where uid='" + uid[
                    0] + "'AND (order_date BETWEEN date_add(now(), interval -7 day) AND NOW())"
            elif ocode == "2":
                # SQL 쿼리문 작성
                strsql1 = "SELECT COUNT(*) FROM skdevsec_orderuser where uid='" + uid[
                    0] + "'AND (order_date BETWEEN date_add(now(), interval -1 MONTH) AND NOW())"
            elif ocode == "3":
                # SQL 쿼리문 작성
                strsql1 = "SELECT COUNT(*) FROM skdevsec_orderuser where uid='" + uid[
                    0] + "'AND (order_date BETWEEN date_add(now(), interval -3 MONTH) AND NOW())"
            elif ocode == "4":
                # SQL 쿼리문 작성
                strsql1 = "SELECT COUNT(*) FROM skdevsec_orderuser where uid='" + uid[
                    0] + "'AND (order_date BETWEEN date_add(now(), interval -6 MONTH) AND NOW())"
            else:
                return Response(0)

            # DB에 명령문 전송
            cursor.execute(strsql1)
            count = cursor.fetchone()

            # 주문 내역 갯수 저장
            new_data.append({"order_count": count[0]})

            if ocode == "1":
                # SQL 쿼리문 작성
                strsql2 = "SELECT * FROM skdevsec_orderuser WHERE uid='" + uid[
                    0] + "' AND (order_date BETWEEN date_add(now(), interval -7 day) AND NOW()) order by oid desc limit " + str(
                    opage * 10 - 10) + ", 10"
            elif ocode == "2":
                # SQL 쿼리문 작성
                strsql2 = "SELECT * FROM skdevsec_orderuser WHERE uid='" + uid[
                    0] + "' AND (order_date BETWEEN date_add(now(), interval -1 MONTH) AND NOW()) order by oid desc limit " + str(
                    opage * 10 - 10) + ", 10"
            elif ocode == "3":
                # SQL 쿼리문 작성
                strsql2 = "SELECT * FROM skdevsec_orderuser WHERE uid='" + uid[
                    0] + "' AND (order_date BETWEEN date_add(now(), interval -3 MONTH) AND NOW()) order by oid desc limit " + str(
                    opage * 10 - 10) + ", 10"
            elif ocode == "4":
                # SQL 쿼리문 작성
                strsql2 = "SELECT * FROM skdevsec_orderuser WHERE uid='" + uid[
                    0] + "' AND (order_date BETWEEN date_add(now(), interval -6 MONTH) AND NOW()) order by oid desc limit " + str(
                    opage * 10 - 10) + ", 10"
            else:
                return Response(0)

            # DB에 명령문 전송
            cursor.execute(strsql2)
            datas = cursor.fetchone()

            # 데이터가 있으면
            if datas is not None:
                # 데이터 수만큼 반복
                while datas:
                    strsql3 = "SELECT pname, COUNT(pname) FROM skdevsec_orderproduct WHERE oid='" + str(
                        datas[0]) + "'"
                    cursor1.execute(strsql3)
                    pnames = cursor1.fetchone()
                    new_data_in = dict()
                    new_data_in['pname'] = pnames[0]
                    new_data_in['product_count'] = pnames[1]
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
            print(f"user_paid_date 에러: {e}")
            return Response(0)

        # 성공 했을 시, 프론트엔드에 데이터 전송
        else:
            return Response(new_data)

    # sql 인젝션 되는 코드
    # 결제 결과 내역 출력
    @action(detail=False, methods=['POST'])
    def user_paid_input(self, request):
        # 데이터 저장을 위한 리스트 선언
        new_data = list()
        try:
            # DB 접근할 cursor
            cursor = connection.cursor()

            # POST 메소드로 날라온 Request의 데이터 각각 추출
            oid = request.data['oid']

            # SQL 쿼리문 작성
            strsql = "SELECT * FROM skdevsec_orderuser where oid='" + oid + "'"

            # DB에 명령문 전송
            cursor.execute(strsql)
            datas = cursor.fetchone()

            # 데이터가 있으면
            if datas is not None:
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
            print(f"user_paid_input 에러: {e}")
            return Response(0)

        # 성공 했을 시, 프론트엔드에 데이터 전송
        else:
            return Response(new_data)