# 필요한 모듈 임포트
from django.db import connection
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from DBConnect.serializers import *


# 장바구니 테이블
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

            if uid is not None:
                # SQL 쿼리문 작성
                strsql1 = "SELECT bag_id, pid, bcount FROM skdevsec_bag where uid='" + uid[0] + "'"

                # DB에 명령문 전송
                cursor.execute(strsql1)
                datas = cursor.fetchall()

            else:
                return Response(0)

            # 장바구니 목록이 있으면
            if len(datas) != 0:
                # 장바구니 갯수만큼 반복
                for data in datas:
                    new_data_in = dict()
                    # SQL 쿼리문 작성
                    strsql2 = "SELECT pname, pcate, pimage, ptext, pprice FROM skdevsec_product WHERE pid='" + str(
                        data[1]) + "'"
                    # DB에 명령문 전송
                    cursor.execute(strsql2)
                    products = cursor.fetchone()
                    # 상품이 있으면
                    if products is not None:
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

            if uid is not None:
                # SQL 쿼리문 작성
                strsql1 = "DELETE FROM skdevsec_bag WHERE uid='" + uid[0] + "'"

                # DB에 명령문 전송
                cursor.execute(strsql1)
            else:
                return Response(0)

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

            if uid is not None:
                # SQL 쿼리문 작성
                strsql1 = "SELECT uid FROM skdevsec_bag WHERE uid='" + uid[0] + "' AND pid='" + pid + "'"

                # DB에 명령문 전송
                cursor.execute(strsql1)
                uid1 = cursor.fetchall()
            else:
                return Response(0)

            # 장바구니에 상품이 있으면
            if len(uid1) != 0:
                # SQL 쿼리문 작성
                strsql2 = "UPDATE skdevsec_bag SET bcount=bcount+'" + bcount + "' WHERE pid='" + pid + "' AND uid='" + \
                          uid1[0][0] + "'"
                # DB에 명령문 전송
                cursor.execute(strsql2)
            else:
                # SQL 쿼리문 작성
                strsql2 = "INSERT INTO skdevsec_bag(uid, pid, bcount) VALUES('" + uid[
                    0] + "', '" + pid + "', '" + bcount + "')"
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
    # 미사용 함수?
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
                # 데이터 만큼 반복
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

    # sql 인젝션 되는 코드
    # 장바구니 갯수
    @action(detail=False, methods=['POST'])
    def bag_count(self, request):
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

            if uid is not None:
                # SQL 쿼리문 작성
                strsql1 = "SELECT COUNT(*) FROM skdevsec_bag where uid='" + uid[0] + "'"

                # DB에 명령문 전송
                cursor.execute(strsql1)
                count = cursor.fetchone()
            else:
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
            return Response({"bag_count": count[0]})
