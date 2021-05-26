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
            authentication_number = sms_send(ophone)

        # 에러가 발생했을 경우 백엔드에 에러 내용 출력 및 프론트엔드에 0 전송
        except Exception as e:
            connection.rollback()
            print(f"에러: {e}")
            return Response(0)
        # 성공 했을 시, 전송했던 인증 번호를 프론트엔드에 전달
        else:
            return Response(authentication_number)

    # 결제 데이터 임시 저장
    @action(detail=False, methods=['POST'])
    def temp_pay_info(self, request):
        try:
            global global_product
            # POST 메소드로 날라온 Request의 데이터 각각 추출
            global_product = request.data

        # 에러가 발생했을 경우 백엔드에 에러 내용 출력 및 프론트엔드에 0 전송
        except Exception as e:
            print(f"에러: {e}")
            return Response(0)
        else:
            return Response(1)

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
            global_oprice = int(request.data['oprice'])
            global_bagcode = int(request.data['bagcode'])

            sum_product = 0

            try:
                temp_list = list()
                for temp_dict in global_product:
                    for value in temp_dict.values():
                        temp_list.append(value)
                for i in range(len(temp_list)//2):
                    sum_product += int(temp_list[i*2]) * int(temp_list[i*2+1])

                if sum_product != global_oprice:
                    return Response(0)

            except Exception as e:
                print(f"에러: {e}")
                return Response(0)

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
                'approval_url': 'http://kilhyomin.com/item/ordersuccess',
                'fail_url': 'http://kilhyomin.com/item/orderfail',
                'cancel_url': 'http://kilhyomin.com/item/orderfail',
            }
            response = requests.post(url + "/v1/payment/ready", params=params, headers=headers)
            response = json.loads(response.text)

        # 에러가 발생했을 경우 백엔드에 에러 내용 출력 및 프론트엔드에 0 전송
        except Exception as e:
            print(f"에러: {e}")
            return Response(0)

        # 성공 했을 시, 프론트엔드에 데이터 전송
        else:
            return Response(response)

    # 결제 성공
    @action(detail=False, methods=['POST'])
    def pay_success(self, request):
        try:
            # DB 접근할 cursor
            cursor = connection.cursor()

            # SQL 쿼리문 작성
            sql_query_1 = "SELECT * FROM skdevsec_user WHERE unickname=%s"

            # DB에 명령문 전송
            cursor.execute(sql_query_1, (global_unickname, ))
            uid = cursor.fetchone()

            if uid is not None:
                # SQL 쿼리문 작성
                sql_query_2 = "INSERT INTO skdevsec_orderuser(uid, oname, ophone, oaddress, order_date, oprice) " \
                              "VALUES(%s, %s, %s, %s, %s, %s) "

                # DB에 명령문 전송
                cursor.execute(sql_query_2, (uid[0], global_oname, global_ophone, global_oaddress,
                                             global_order_date, global_oprice, ))
                connection.commit()
            else:
                return Response(0)

            try:
                for temp_dict in global_product:
                    temp_list = list()
                    for value in temp_dict.values():
                        temp_list.append(value)

                    sql_query_3 = "UPDATE skdevsec_product SET pcount=pcount-%s WHERE pid=%s"

                    # DB에 명령문 전송
                    cursor.execute(sql_query_3, (temp_list[1], int(temp_list[0]), ))
                    connection.commit()

                    # SQL 쿼리문 작성
                    sql_query_4 = "SELECT * FROM skdevsec_product WHERE pid=%s"

                    # DB에 명령문 전송
                    cursor.execute(sql_query_4, (int(temp_list[0]), ))
                    data = cursor.fetchone()

                    # 데이터가 있으면
                    if data is not None:
                        pname = data[1]
                        pcate = data[2]
                        pprice = int(data[5])

                    # 데이터가 없으면
                    else:
                        # DB와 접속 종료
                        connection.close()
                        # 프론트엔드로 0 전송
                        return Response(0)

                    # SQL 쿼리문 작성
                    sql_query_5 = "SELECT * FROM skdevsec_orderuser WHERE uid=%s ORDER BY oid DESC"

                    # DB에 명령문 전송
                    cursor.execute(sql_query_5, (uid[0], ))
                    oid = cursor.fetchone()

                    # 데이터가 있으면
                    if oid is not None:
                        # SQL 쿼리문 작성
                        sql_query_6 = "INSERT INTO skdevsec_orderproduct(oid, pname, pcate, pprice, pcount) VALUES(" \
                                      "%s, %s, %s, %s, %s) "

                        # DB에 명령문 전송
                        cursor.execute(sql_query_6, (int(oid[0]), pname, pcate, pprice, int(temp_list[1]), ))

                    # 데이터가 없으면
                    else:
                        # DB와 접속 종료
                        connection.commit()
                        connection.close()
                        # 프론트엔드로 0 전송
                        return Response(0)

            except Exception as e:
                connection.rollback()
                print(f"에러: {e}")
                return Response(0)

            else:
                if global_bagcode == 1:
                    sql_query_7 = "DELETE FROM skdevsec_bag WHERE uid=%s"
                    cursor.execute(sql_query_7, (uid[0], ))

            # DB와 접속 종료
            connection.commit()
            connection.close()

        # 에러가 발생했을 경우 백엔드에 에러 내용 출력 및 프론트엔드에 0 전송
        except Exception as e:
            connection.rollback()
            print(f"에러: {e}")
            return Response(0)

        # 성공 했을 시, 프론트엔드에 데이터 전송
        else:
            return Response(1)

    # 결제 결과 전부 출력
    @action(detail=False, methods=['POST'])
    def admin_paid_output(self, request):
        # 데이터 저장을 위한 리스트 선언
        new_data = list()
        try:
            # DB 접근할 cursor
            cursor = connection.cursor()

            # POST 메소드로 날라온 Request의 데이터 각각 추출
            opage = int(request.data['opage'])

            # SQL 쿼리문 작성
            sql_query_1 = "SELECT COUNT(*) FROM skdevsec_orderuser"

            # DB에 명령문 전송
            cursor.execute(sql_query_1)
            count = cursor.fetchone()

            if count is not None:
                # 주문 내역 갯수 저장
                new_data.append({"order_count": count[0]})

                # SQL 쿼리문 작성
                sql_query_2 = "SELECT * FROM skdevsec_orderuser order by oid desc limit %s, 10"

                # DB에 명령문 전송
                cursor.execute(sql_query_2, (opage*10-10, ))
                data = cursor.fetchone()

                # 데이터 수만큼 반복
                while data:
                    new_data_in = dict()
                    new_data_in['oid'] = data[0]
                    new_data_in['uid'] = data[1]
                    new_data_in['oname'] = data[2]
                    new_data_in['ophone'] = data[3]
                    new_data_in['oaddress'] = data[4]
                    new_data_in['order_date'] = data[5]
                    new_data_in['oprice'] = data[6]
                    new_data.append(new_data_in)
                    data = cursor.fetchone()
            else:
                connection.close()
                return Response({"order_count": 0})

            # DB와 접속 종료
            connection.close()

        # 에러가 발생했을 경우 백엔드에 에러 내용 출력 및 프론트엔드에 0 전송
        except Exception as e:
            connection.rollback()
            print(f"에러: {e}")
            return Response(0)

        # 성공 했을 시, 프론트엔드에 데이터 전송
        else:
            return Response(new_data)

    # 결제 결과 검색
    @action(detail=False, methods=['POST'])
    def admin_paid_search(self, request):
        # 데이터 저장을 위한 리스트 선언
        new_data = list()
        try:
            # DB 접근할 cursor
            cursor = connection.cursor()

            # POST 메소드로 날라온 Request의 데이터 각각 추출
            ocode = int(request.data['ocode'])
            osearch = request.data['osearch']
            opage = int(request.data['opage'])

            if ocode == 0:
                # SQL 쿼리문 작성
                sql_query_1 = "SELECT * FROM skdevsec_orderuser WHERE (uid LIKE %s OR oname LIKE %s) order by oid " \
                              "desc limit %s, 10 "
                sql_query_2 = "SELECT COUNT(*) FROM skdevsec_orderuser WHERE (uid LIKE %s OR oname LIKE %s)"

                # DB에 명령문 전송
                cursor.execute(sql_query_2, ('%' + osearch + '%', '%' + osearch + '%', ))
                count = cursor.fetchone()

                # DB에 명령문 전송
                cursor.execute(sql_query_1, ('%' + osearch + '%', '%' + osearch + '%', opage*10-10))
                data = cursor.fetchone()

            elif ocode == 1:
                # SQL 쿼리문 작성
                sql_query_1 = "SELECT * FROM skdevsec_orderuser WHERE uid LIKE %s order by oid desc limit %s, 10"
                sql_query_2 = "SELECT COUNT(*) FROM skdevsec_orderuser WHERE uid LIKE %s"

                # DB에 명령문 전송
                cursor.execute(sql_query_2, ('%' + osearch + '%', ))
                count = cursor.fetchone()

                # DB에 명령문 전송
                cursor.execute(sql_query_1, ('%' + osearch + '%', opage*10-10))
                data = cursor.fetchone()

            elif ocode == 2:
                # SQL 쿼리문 작성
                sql_query_1 = "SELECT * FROM skdevsec_orderuser WHERE oname LIKE %s order by oid desc limit %s, 10"
                sql_query_2 = "SELECT COUNT(*) FROM skdevsec_orderuser WHERE oname LIKE %s"

                # DB에 명령문 전송
                cursor.execute(sql_query_2, ('%' + osearch + '%',))
                count = cursor.fetchone()

                # DB에 명령문 전송
                cursor.execute(sql_query_1, ('%' + osearch + '%', opage*10-10))
                data = cursor.fetchone()

            else:
                return Response(0)

            if count is not None:
                # 데이터 수만큼 반복
                while data:
                    new_data_in = dict()
                    new_data_in['oid'] = int(data[0])
                    new_data_in['uid'] = data[1]
                    new_data_in['oname'] = data[2]
                    new_data_in['ophone'] = data[3]
                    new_data_in['oaddress'] = data[4]
                    new_data_in['order_date'] = data[5]
                    new_data_in['oprice'] = int(data[6])
                    new_data.append(new_data_in)
                    data = cursor.fetchone()

                new_data.append({"order_count": count[0]})
            else:
                connection.close()
                return Response({"order_count": 0})

            # DB와 접속 종료
            connection.close()

        # 에러가 발생했을 경우 백엔드에 에러 내용 출력 및 프론트엔드에 0 전송
        except Exception as e:
            connection.rollback()
            print(f"에러: {e}")
            return Response(0)

        # 성공 했을 시, 프론트엔드에 데이터 전송
        else:
            return Response(new_data)

    # 결제 결과 유저꺼 출력
    @action(detail=False, methods=['POST'])
    def user_paid_output(self, request):
        # 데이터 저장을 위한 리스트 선언
        new_data = list()
        try:
            # DB 접근할 cursor
            cursor = connection.cursor()
            cursor_pname = connection.cursor()

            # POST 메소드로 날라온 Request의 데이터 각각 추출
            unickname = request.data['unickname']
            opage = int(request.data['opage'])

            # SQL 쿼리문 작성
            sql_query_1 = "SELECT uid FROM skdevsec_user where unickname=%s"

            # DB에 명령문 전송
            cursor.execute(sql_query_1, (unickname, ))
            uid = cursor.fetchone()

            if uid is not None:
                # SQL 쿼리문 작성
                sql_query_2 = "SELECT COUNT(*) FROM skdevsec_orderuser where uid=%s"

                # DB에 명령문 전송
                cursor.execute(sql_query_2, (uid[0], ))
                count = cursor.fetchone()
            else:
                return Response(0)

            if count is not None:
                # 주문 내역 갯수 저장
                new_data.append({"order_count": count[0]})

                # SQL 쿼리문 작성
                sql_query_3 = "SELECT * FROM skdevsec_orderuser WHERE uid=%s order by oid desc limit %s, 10"

                # DB에 명령문 전송
                cursor.execute(sql_query_3, (uid[0], opage*10-10, ))
                data = cursor.fetchone()

                while data:
                    sql_query_4 = "SELECT *, COUNT(pname) FROM skdevsec_orderproduct WHERE oid=%s"
                    cursor_pname.execute(sql_query_4, (int(data[0]), ))
                    pname = cursor_pname.fetchone()

                    new_data_in = dict()
                    new_data_in['pname'] = pname[2]
                    new_data_in['product_count'] = pname[6]
                    new_data_in['oid'] = int(data[0])
                    new_data_in['uid'] = data[1]
                    new_data_in['oname'] = data[2]
                    new_data_in['ophone'] = data[3]
                    new_data_in['oaddress'] = data[4]
                    new_data_in['order_date'] = data[5]
                    new_data_in['oprice'] = int(data[6])
                    new_data.append(new_data_in)
                    data = cursor.fetchone()

            else:
                connection.close()
                return Response({"order_count": 0})

            # DB와 접속 종료
            connection.close()

        # 에러가 발생했을 경우 백엔드에 에러 내용 출력 및 프론트엔드에 0 전송
        except Exception as e:
            connection.rollback()
            print(f"에러: {e}")
            return Response(0)

        # 성공 했을 시, 프론트엔드에 데이터 전송
        else:
            return Response(new_data)

    # 결제 내역 날짜 검색
    @action(detail=False, methods=['POST'])
    def user_paid_date(self, request):
        # 데이터 저장을 위한 리스트 선언
        new_data = list()
        try:
            # DB 접근할 cursor
            cursor = connection.cursor()
            cursor_pname = connection.cursor()

            # POST 메소드로 날라온 Request의 데이터 각각 추출
            unickname = request.data['unickname']
            start_date = request.data['start_date']
            end_date = request.data['end_date'] + " 23:59"
            opage = int(request.data['opage'])

            # SQL 쿼리문 작성
            sql_query_1 = "SELECT * FROM skdevsec_user where unickname=%s"

            # DB에 명령문 전송
            cursor.execute(sql_query_1, (unickname, ))
            uid = cursor.fetchone()

            # SQL 쿼리문 작성
            sql_query_2 = "SELECT COUNT(*) FROM skdevsec_orderuser where uid=%s AND (order_date BETWEEN %s AND %s)"

            # DB에 명령문 전송
            cursor.execute(sql_query_2, (uid[0], start_date, end_date, ))
            count = cursor.fetchone()

            if count is not None:
                # 주문 내역 갯수 저장
                new_data.append({"order_count": count[0]})

                # SQL 쿼리문 작성
                sql_query_3 = "SELECT * FROM skdevsec_orderuser WHERE uid=%s AND (order_date BETWEEN %s AND %s) order " \
                              "by oid desc limit %s, 10 "

                # DB에 명령문 전송
                cursor.execute(sql_query_3, (uid[0], start_date, end_date, opage*10-10, ))
                data = cursor.fetchone()

                while data:
                    sql_query_4 = "SELECT *, COUNT(pname) FROM skdevsec_orderproduct WHERE oid=%s"
                    cursor_pname.execute(sql_query_4, (int(data[0]), ))
                    pname = cursor_pname.fetchone()
                    new_data_in = dict()
                    new_data_in['pname'] = pname[2]
                    new_data_in['product_count'] = pname[6]
                    new_data_in['oid'] = int(data[0])
                    new_data_in['uid'] = data[1]
                    new_data_in['oname'] = data[2]
                    new_data_in['ophone'] = data[3]
                    new_data_in['oaddress'] = data[4]
                    new_data_in['order_date'] = data[5]
                    new_data_in['oprice'] = int(data[6])
                    new_data.append(new_data_in)
                    data = cursor.fetchone()
            else:
                connection.close()
                return Response({"order_count": 0})

            # DB와 접속 종료
            connection.close()

        # 에러가 발생했을 경우 백엔드에 에러 내용 출력 및 프론트엔드에 0 전송
        except Exception as e:
            connection.rollback()
            print(f"에러: {e}")
            return Response(0)

        # 성공 했을 시, 프론트엔드에 데이터 전송
        else:
            return Response(new_data)

    # 결제 내역 날짜 조건 검색
    @action(detail=False, methods=['POST'])
    def user_paid_date_code(self, request):
        # 데이터 저장을 위한 리스트 선언
        new_data = list()
        try:
            # DB 접근할 cursor
            cursor = connection.cursor()
            cursor_pname = connection.cursor()

            # POST 메소드로 날라온 Request의 데이터 각각 추출
            unickname = request.data['unickname']
            ocode = int(request.data['ocode'])
            opage = int(request.data['opage'])

            # SQL 쿼리문 작성
            sql_query_1 = "SELECT * FROM skdevsec_user where unickname=%s"

            # DB에 명령문 전송
            cursor.execute(sql_query_1, (unickname, ))
            uid = cursor.fetchone()

            if ocode == 1:
                # SQL 쿼리문 작성
                sql_query_2 = "SELECT COUNT(*) FROM skdevsec_orderuser where uid=%s AND (order_date BETWEEN date_add(" \
                              "now(), interval -7 day) AND NOW()) "
            elif ocode == 2:
                # SQL 쿼리문 작성
                sql_query_2 = "SELECT COUNT(*) FROM skdevsec_orderuser where uid=%s AND (order_date BETWEEN " \
                              "date_add(now(), interval -1 MONTH) AND NOW()) "
            elif ocode == 3:
                # SQL 쿼리문 작성
                sql_query_2 = "SELECT COUNT(*) FROM skdevsec_orderuser where uid=%s AND (order_date BETWEEN date_add(" \
                              "now(), interval -3 MONTH) AND NOW()) "
            elif ocode == 4:
                # SQL 쿼리문 작성
                sql_query_2 = "SELECT COUNT(*) FROM skdevsec_orderuser where uid=%s AND (order_date BETWEEN date_add(" \
                              "now(), interval -6 MONTH) AND NOW()) "
            else:
                return Response(0)

            # DB에 명령문 전송
            cursor.execute(sql_query_2, (uid[0], ))
            count = cursor.fetchone()

            if count is not None:
                # 주문 내역 갯수 저장
                new_data.append({"order_count": count[0]})

                if ocode == 1:
                    # SQL 쿼리문 작성
                    sql_query_3 = "SELECT * FROM skdevsec_orderuser WHERE uid=%s AND (order_date BETWEEN date_add(" \
                                  "now(), interval -7 day) AND NOW()) order by oid desc limit %s, 10 "
                elif ocode == 2:
                    # SQL 쿼리문 작성
                    sql_query_3 = "SELECT * FROM skdevsec_orderuser WHERE uid=%s AND (order_date BETWEEN date_add(" \
                                  "now(), interval -1 MONTH) AND NOW()) order by oid desc limit %s, 10 "
                elif ocode == 3:
                    # SQL 쿼리문 작성
                    sql_query_3 = "SELECT * FROM skdevsec_orderuser WHERE uid=%s AND (order_date BETWEEN date_add(" \
                                  "now(), interval -3 MONTH) AND NOW()) order by oid desc limit %s, 10 "
                elif ocode == 4:
                    # SQL 쿼리문 작성
                    sql_query_3 = "SELECT * FROM skdevsec_orderuser WHERE uid=%s AND (order_date BETWEEN date_add(" \
                                  "now(), interval -6 MONTH) AND NOW()) order by oid desc limit %s, 10 "
                else:
                    return Response(0)

                # DB에 명령문 전송
                cursor.execute(sql_query_3, (uid[0], opage*10-10, ))
                data = cursor.fetchone()

                # 데이터 수만큼 반복
                while data:
                    sql_query_4 = "SELECT *, COUNT(pname) FROM skdevsec_orderproduct WHERE oid=%s"
                    cursor_pname.execute(sql_query_4, (int(data[0]), ))
                    pname = cursor_pname.fetchone()
                    new_data_in = dict()
                    new_data_in['pname'] = pname[2]
                    new_data_in['product_count'] = pname[6]
                    new_data_in['oid'] = int(data[0])
                    new_data_in['uid'] = data[1]
                    new_data_in['oname'] = data[2]
                    new_data_in['ophone'] = data[3]
                    new_data_in['oaddress'] = data[4]
                    new_data_in['order_date'] = data[5]
                    new_data_in['oprice'] = int(data[6])
                    new_data.append(new_data_in)
                    data = cursor.fetchone()

            else:
                return Response({"order_count": 0})

            # DB와 접속 종료
            connection.close()

        # 에러가 발생했을 경우 백엔드에 에러 내용 출력 및 프론트엔드에 0 전송
        except Exception as e:
            connection.rollback()
            print(f"에러: {e}")
            return Response(0)

        # 성공 했을 시, 프론트엔드에 데이터 전송
        else:
            return Response(new_data)

    # 결제 결과 내역 출력
    @action(detail=False, methods=['POST'])
    def user_paid_input(self, request):
        # 데이터 저장을 위한 리스트 선언
        new_data = list()
        try:
            # DB 접근할 cursor
            cursor = connection.cursor()

            # POST 메소드로 날라온 Request의 데이터 각각 추출
            oid = int(request.data['oid'])

            # SQL 쿼리문 작성
            sql_query = "SELECT * FROM skdevsec_orderuser where oid=%s"

            # DB에 명령문 전송
            cursor.execute(sql_query, (oid, ))
            data = cursor.fetchone()

            # 데이터가 있으면
            if data is not None:
                # 데이터 수만큼 반복
                while data:
                    new_data_in = dict()
                    new_data_in['oid'] = int(data[0])
                    new_data_in['uid'] = data[1]
                    new_data_in['oname'] = data[2]
                    new_data_in['ophone'] = data[3]
                    new_data_in['oaddress'] = data[4]
                    new_data_in['order_date'] = data[5]
                    new_data_in['oprice'] = int(data[6])
                    new_data.append(new_data_in)
                    data = cursor.fetchone()
            # 데이터가 없으면
            else:
                # DB와 접속 종료
                connection.close()
                # 프론트엔드에 0 전송
                return Response(0)

            # DB와 접속 종료
            connection.close()

        # 에러가 발생했을 경우 백엔드에 에러 내용 출력 및 프론트엔드에 0 전송
        except Exception as e:
            connection.rollback()
            print(f"에러: {e}")
            return Response(0)

        # 성공 했을 시, 프론트엔드에 데이터 전송
        else:
            return Response(new_data)
