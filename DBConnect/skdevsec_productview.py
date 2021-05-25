# 필요한 모듈 임포트
import os
from django.db import connection
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from DBConnect.serializers import *


# 상품 관련 테이블
class SkdevsecProductViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = SkdevsecProduct.objects.all()
    serializer_class = SkdevsecProductSerializer

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
            sql_query_1 = "SELECT COUNT(*) FROM skdevsec_product"

            # DB에 명령문 전송
            cursor.execute(sql_query_1)
            count = cursor.fetchone()

            if count is not None:
                # 상품 갯수 저장
                new_data.append({"product_count": count[0]})
                # SQL 쿼리문 작성
                sql_query_2 = "SELECT * FROM skdevsec_product order by pid desc limit %s, 8"

                # DB에 명령문 전송
                cursor.execute(sql_query_2, (ppage*8-8, ))
                data = cursor.fetchone()

                while data:
                    new_data_in = dict()
                    new_data_in['pid'] = int(data[0])
                    new_data_in['pname'] = data[1]
                    new_data_in['pcate'] = data[2]
                    new_data_in['pimage'] = data[3]
                    new_data_in['ptext'] = data[4]
                    new_data_in['pprice'] = int(data[5])
                    new_data_in['pcreate_date'] = data[6]
                    new_data_in['preview'] = data[7]
                    new_data_in['preview_avg'] = float(data[8])
                    new_data_in['pcount'] = int(data[9])
                    new_data.append(new_data_in)
                    data = cursor.fetchone()
            else:
                connection.close()
                return Response({"product_count": 0})

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

    # 상품상세 페이지 출력
    @action(detail=False, methods=['POST'])
    def product_inside(self, request):
        new_data = list()
        try:
            # DB 접근할 cursor
            cursor = connection.cursor()

            # POST 메소드로 날라온 Request의 데이터 각각 추출
            pid = int(request.data['pid'])

            # SQL 쿼리문 작성
            sql_query = "SELECT * FROM skdevsec_product WHERE pid=%s"

            # DB에 명령문 전송
            cursor.execute(sql_query, (pid, ))
            data = cursor.fetchone()

            # 데이터가 있으면
            if data is not None:
                # 데이터 수만큼 반복
                while data:
                    new_data_in = dict()
                    new_data_in['pid'] = int(data[0])
                    new_data_in['pname'] = data[1]
                    new_data_in['pcate'] = data[2]
                    new_data_in['pimage'] = data[3]
                    new_data_in['ptext'] = data[4]
                    new_data_in['pprice'] = int(data[5])
                    new_data_in['pcreate_date'] = data[6]
                    new_data_in['preview'] = int(data[7])
                    new_data_in['preview_avg'] = float(data[8])
                    new_data_in['pcount'] = int(data[9])
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
            new_data['pprice'] = int(request.data['pprice'])
            new_data['pcreate_date'] = request.data['pcreate_date']
            new_data['preview'] = request.data['preview']
            new_data['preview_avg'] = float(request.data['preview_avg'])
            new_data['pcount'] = int(request.data['pcount'])

            # DB에 저장하기 위해 시리얼라이저 함수 사용
            file_serializer = SkdevsecProductSerializer(data=new_data)

            # 저장이 가능한 상태면 저장
            if file_serializer.is_valid():
                file_serializer.save()
            # 불가능한 상태면 에러 알림 및 프론트엔드에 0 전송
            else:
                print(f"에러: {file_serializer.errors}")
                return Response(0)

        # 에러가 발생했을 경우 백엔드에 에러 내용 출력 및 프론트엔드에 0 전송
        except Exception as e:
            connection.rollback()
            print(f"에러: {e}")
            return Response(0)

        # 성공 했을 시, 프론트엔드에 1 전송
        else:
            return Response(1)

    # 상품 수정
    @action(detail=False, methods=['POST'])
    def change_product(self, request):
        # 데이터 저장을 위한 딕셔너리 선언
        new_data = dict()
        try:
            # DB 접근할 cursor
            cursor = connection.cursor()

            # 수정할 게시물 번호를 받아서 해당 DB를 저장
            data_check = SkdevsecProduct.objects.get(pid=int(request.data['pid']))

            # POST 메소드로 날라온 Request의 데이터 각각 추출
            pid = int(request.data['pid'])
            new_data['pname'] = request.data['pname']
            new_data['pcate'] = request.data['pcate']
            new_data['pimage'] = request.data['pimage']
            new_data['ptext'] = request.data['ptext']
            new_data['pprice'] = int(request.data['pprice'])
            new_data['pcreate_date'] = request.data['pcreate_date']
            new_data['preview'] = int(request.data['preview'])
            new_data['preview_avg'] = float(request.data['preview_avg'])
            new_data['pcount'] = int(request.data['pcount'])

            # SQL 쿼리문 작성
            sql_query_1 = "SELECT * FROM skdevsec_product WHERE pid=%s"

            # DB에 명령문 전송
            cursor.execute(sql_query_1, (pid, ))
            data = cursor.fetchone()

            if data is not None:
                image_path = data[3]
            else:
                return Response(0)

            # DB에 저장하기 위해 시리얼라이저 함수 사용
            file_serializer = SkdevsecProductSerializer(data_check, data=new_data)

            # 수정할 데이터를 업데이트함
            if new_data['pimage'] != image_path:
                if file_serializer.is_valid():
                    file_serializer.update(data_check, file_serializer.validated_data)
                    # 파일이 존재하면 삭제
                    if data[3] != "0":
                        os.remove(data[3])
                # 불가능한 상태면 에러 알림 및 프론트엔드에 0 전송
                else:
                    print(f"에러: {file_serializer.errors}")
                    return Response(0)
            else:
                sql_query_2 = "UPDATE skdevsec_product SET pname=%s, pcate=%s, ptext=%s, pprice=%s, pcount=%s WHERE " \
                              "pid=%s "

                # DB에 명령문 전송
                cursor.execute(sql_query_2, (new_data['pname'], new_data['pcate'], new_data['ptext'],
                                             new_data['pprice'], new_data['pcount'], pid,))

            connection.commit()
            connection.close()

        # 에러가 발생했을 경우 백엔드에 에러 내용 출력 및 프론트엔드에 0 전송
        except Exception as e:
            connection.rollback()
            print(f"에러: {e}")
            return Response(0)

        # 성공 했을 시, 프론트엔드에 1 전송
        else:
            return Response(1)

    # 상품 삭제
    @action(detail=False, methods=['POST'])
    def product_delete(self, request):
        try:
            # DB 접근할 cursor
            cursor = connection.cursor()

            # POST 메소드로 날라온 Request의 데이터 각각 추출
            pid = int(request.data['pid'])

            # SQL 쿼리문 작성
            sql_query_1 = "SELECT * FROM skdevsec_product WHERE pid=%s"

            # DB에 명령문 전송
            cursor.execute(sql_query_1, (pid, ))
            data = cursor.fetchone()

            if data is not None:
                # 파일이 존재하면 삭제
                if data[3] != "0":
                    os.remove(data[3])
            else:
                return Response(0)

            # SQL 쿼리문 작성
            sql_query_2 = "DELETE FROM skdevsec_product WHERE pid=%s"

            # DB에 명령문 전송
            cursor.execute(sql_query_2, (pid, ))

            # DB와 접속 종료
            connection.commit()
            connection.close()

        # 에러가 발생했을 경우 백엔드에 에러 내용 출력 및 프론트엔드에 0 전송
        except Exception as e:
            connection.rollback()
            print(f"에러: {e}")
            return Response(0)

        # 성공 했을 시, 프론트엔드에 1 전송
        else:
            return Response(1)

    # 상품 검색
    @action(detail=False, methods=['POST'])
    def product_search(self, request):
        # 데이터 저장을 위한 리스트 선언
        new_data = list()
        try:
            # DB 접근할 cursor
            cursor = connection.cursor()

            # POST 메소드로 날라온 Request의 데이터 각각 추출
            psearch = request.data

            # psearch = ["페이지", "검색단어", "카테고리", "카테고리", ...]
            # SQL 쿼리문 작성
            sql_query1 = "SELECT * FROM skdevsec_product WHERE (pname LIKE %s)"
            sql_query2 = "SELECT COUNT(*) FROM skdevsec_product WHERE (pname LIKE %s)"
            if len(psearch) >= 3:
                if psearch[2] == "":
                    sql_query1 = "SELECT * FROM skdevsec_product WHERE (pname LIKE %s)"
                    sql_query2 = "SELECT COUNT(*) FROM skdevsec_product WHERE (pname LIKE %s)"
                else:
                    sql_query1 = sql_query1 + " AND (pcate='"
                    sql_query2 = sql_query2 + " AND (pcate='"
                    for pcate in psearch[2:]:
                        sql_query1 = sql_query1 + pcate + "' OR pcate='"
                        sql_query2 = sql_query2 + pcate + "' OR pcate='"
                    sql_query1 = sql_query1 + "')"
                    sql_query2 = sql_query2 + "')"
            sql_query1 = sql_query1 + " ORDER BY pid DESC limit %s, 8"

            # DB에 명령문 전송
            cursor.execute(sql_query2, ('%' + psearch[1] + '%', ))
            count = cursor.fetchone()

            # DB에 명령문 전송
            cursor.execute(sql_query1, ('%' + psearch[1] + '%', int(psearch[0])*8-8,))
            data = cursor.fetchone()

            if count is not None:
                # 데이터만큼 반복
                while data:
                    new_data_in = dict()
                    new_data_in['pid'] = int(data[0])
                    new_data_in['pname'] = data[1]
                    new_data_in['pcate'] = data[2]
                    new_data_in['pimage'] = data[3]
                    new_data_in['pprice'] = int(data[5])
                    new_data_in['preview'] = int(data[7])
                    new_data_in['preview_avg'] = float(data[8])
                    new_data.append(new_data_in)
                    data = cursor.fetchone()
                new_data.append({"product_count": count[0]})

            else:
                connection.close()
                return Response({"product_count": 0})

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

    # 메인에서 최신순 상품 리스트 출력
    @action(detail=False, methods=['POST'])
    def latest_item_list(self, request):
        # 데이터 저장을 위한 리스트 선언
        new_data = list()
        try:
            # DB 접근할 cursor
            cursor = connection.cursor()

            ppage = int(request.data['ppage'])

            sql_query_1 = "SELECT COUNT(*) FROM skdevsec_product ORDER BY pcreate_date DESC limit %s, 8"

            # DB에 명령문 전송
            cursor.execute(sql_query_1, (ppage*8-8, ))
            count = cursor.fetchone()

            if count is not None:
                new_data.append({"product_count": count[0]})

                # SQL 쿼리문 작성
                sql_query_2 = "SELECT * FROM skdevsec_product order by pcreate_date desc limit %s, 8"

                # DB에 명령문 전송
                cursor.execute(sql_query_2, (ppage*8-8, ))
                data = cursor.fetchone()

                while data:
                    new_data_in = dict()
                    new_data_in['pid'] = int(data[0])
                    new_data_in['pname'] = data[1]
                    new_data_in['pcate'] = data[2]
                    new_data_in['pimage'] = data[3]
                    new_data_in['pprice'] = int(data[5])
                    new_data_in['preview'] = int(data[7])
                    new_data_in['preview_avg'] = float(data[8])
                    new_data.append(new_data_in)
                    data = cursor.fetchone()
            else:
                connection.close()
                return Response({"product_count": 0})

            # DB와 접속 종료
            connection.close()

            # 에러가 발생했을 경우 에러 내용 출력
        except Exception as e:
            connection.rollback()
            print(f"에러: {e}")
            return Response(0)

        # 성공 했을 시, 프론트엔드로 데이터 전송
        else:
            return Response(new_data)

    # 메인에서 가격높은순 상품 리스트 출력
    @action(detail=False, methods=['POST'])
    def highest_item_list(self, request):
        # 데이터 저장을 위한 리스트 선언
        new_data = list()
        try:
            # DB 접근할 cursor
            cursor = connection.cursor()

            ppage = int(request.data['ppage'])

            sql_query_1 = "SELECT COUNT(*) FROM skdevsec_product ORDER BY pprice DESC limit %s, 8"

            # DB에 명령문 전송
            cursor.execute(sql_query_1, (ppage*8-8, ))
            count = cursor.fetchone()

            if count is not None:
                new_data.append({"product_count": count[0]})

                # SQL 쿼리문 작성
                sql_query_2 = "SELECT * FROM skdevsec_product order by pprice desc limit %s, 8"

                # DB에 명령문 전송
                cursor.execute(sql_query_2, (ppage*8-8, ))
                data = cursor.fetchone()

                # 데이터 수만큼 반복
                while data:
                    new_data_in = dict()
                    new_data_in['pid'] = int(data[0])
                    new_data_in['pname'] = data[1]
                    new_data_in['pcate'] = data[2]
                    new_data_in['pimage'] = data[3]
                    new_data_in['pprice'] = int(data[5])
                    new_data_in['preview'] = int(data[7])
                    new_data_in['preview_avg'] = float(data[8])
                    new_data.append(new_data_in)
                    data = cursor.fetchone()
            else:
                connection.close({"product_count": 0})

            # DB와 접속 종료
            connection.close()

        # 에러가 발생했을 경우 백엔드에 에러 내용 출력 및 프론트엔드에 0 전송
        except Exception as e:
            connection.rollback()
            print(f"에러:{e}")
            return Response(0)

        # 성공 했을 시, 프론트엔드에 데이터 전송
        else:
            return Response(new_data)

    # 메인에서 가격낮은순 상품 리스트 출력
    @action(detail=False, methods=['POST'])
    def rowest_item_list(self, request):
        # 데이터 저장을 위한 리스트 선언
        new_data = list()
        try:
            # DB 접근할 cursor
            cursor = connection.cursor()

            ppage = int(request.data['ppage'])

            sql_query_1 = "SELECT COUNT(*) FROM skdevsec_product ORDER BY pprice DESC limit %s, 8"

            # DB에 명령문 전송
            cursor.execute(sql_query_1, (ppage*8-8, ))
            count = cursor.fetchone()
            if count is not None:
                new_data.append({"product_count": count[0]})

                # SQL 쿼리문 작성
                sql_query_2 = "SELECT * FROM skdevsec_product order by pprice asc limit 8"

                # DB에 명령문 전송
                cursor.execute(sql_query_2)
                data = cursor.fetchone()

                # 데이터 수만큼 반복
                while data:
                    new_data_in = dict()
                    new_data_in['pid'] = int(data[0])
                    new_data_in['pname'] = data[1]
                    new_data_in['pcate'] = data[2]
                    new_data_in['pimage'] = data[3]
                    new_data_in['pprice'] = int(data[5])
                    new_data_in['preview'] = int(data[7])
                    new_data_in['preview_avg'] = float(data[8])
                    new_data.append(new_data_in)
                    data = cursor.fetchone()
            else:
                return Response({"product_count": 0})

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

    # 메인에서 인기순 상품 리스트 출력
    @action(detail=False, methods=['POST'])
    def best_item_list(self, request):
        # 데이터 저장을 위한 리스트 선언
        new_data = list()
        try:
            # DB 접근할 cursor
            cursor = connection.cursor()

            ppage = int(request.data['ppage'])

            sql_query_1 = "SELECT COUNT(*) FROM skdevsec_product order by preview DESC, preview_avg DESC limit %s, 8"

            # DB에 명령문 전송
            cursor.execute(sql_query_1, (ppage*8-8, ))
            count = cursor.fetchone()

            if count is not None:
                new_data.append({"product_count": count[0]})

                # SQL 쿼리문 작성
                sql_query_2 = "SELECT * FROM skdevsec_product order by preview DESC, preview_avg DESC LIMIT 8"

                # DB에 명령문 전송
                cursor.execute(sql_query_2)
                data = cursor.fetchone()

                while data:
                    new_data_in = dict()
                    new_data_in['pid'] = int(data[0])
                    new_data_in['pname'] = data[1]
                    new_data_in['pcate'] = data[2]
                    new_data_in['pimage'] = data[3]
                    new_data_in['pprice'] = int(data[5])
                    new_data_in['preview'] = int(data[7])
                    new_data_in['preview_avg'] = float(data[8])
                    new_data.append(new_data_in)
                    data = cursor.fetchone()

            else:
                return Response({"product_count": 0})

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

    # 관리자 상품 검색
    @action(detail=False, methods=['POST'])
    def admin_product_search(self, request):
        # 데이터 저장을 위한 리스트 선언
        new_data = list()
        try:
            # DB 접근할 cursor
            cursor = connection.cursor()

            # POST 메소드로 날라온 Request의 데이터 각각 추출
            psearch = request.data['psearch']
            ppage = int(request.data['ppage'])
            pcode = int(request.data['pcode'])

            # SQL 쿼리문 작성
            # 0 : 전체 검색 / 1 : 상품 명 검색 / 2 : 카테고리 검색
            if pcode == 0:
                sql_query_1 = "SELECT * FROM skdevsec_product WHERE (pname LIKE %s OR pcate LIKE %s) ORDER BY pid " \
                              "DESC limit %s, 8 "
                sql_query_2 = "SELECT COUNT(*) FROM skdevsec_product WHERE (pname LIKE %s OR pcate LIKE %s)"

                # DB에 명령문 전송
                cursor.execute(sql_query_2, ('%' + psearch + '%', '%' + psearch + '%',))
                count = cursor.fetchone()

                # DB에 명령문 전송
                cursor.execute(sql_query_1, ('%' + psearch + '%', '%' + psearch + '%', ppage*8-8,))
                data = cursor.fetchone()

            elif pcode == 1:
                sql_query_1 = "SELECT * FROM skdevsec_product WHERE pname LIKE %s ORDER BY pid DESC limit %s, 8"
                sql_query_2 = "SELECT COUNT(*) FROM skdevsec_product WHERE pname LIKE %s"

                # DB에 명령문 전송
                cursor.execute(sql_query_2, ('%' + psearch + '%', ))
                count = cursor.fetchone()

                # DB에 명령문 전송
                cursor.execute(sql_query_1, ('%' + psearch + '%', ppage*8-8,))
                data = cursor.fetchone()

            elif pcode == 2:
                sql_query_1 = "SELECT * FROM skdevsec_product WHERE pcate LIKE %s ORDER BY pid DESC limit %s, 8"
                sql_query_2 = "SELECT COUNT(*) FROM skdevsec_product WHERE pcate LIKE %s"

                # DB에 명령문 전송
                cursor.execute(sql_query_2, ('%' + psearch.upper() + '%',))
                count = cursor.fetchone()

                # DB에 명령문 전송
                cursor.execute(sql_query_1, ('%' + psearch.upper() + '%', ppage*8-8,))
                data = cursor.fetchone()

            else:
                return Response(0)

            if count is not None:
                while data:
                    new_data_in = dict()
                    new_data_in['pid'] = int(data[0])
                    new_data_in['pname'] = data[1]
                    new_data_in['pcate'] = data[2]
                    new_data_in['pimage'] = data[3]
                    new_data_in['pprice'] = int(data[5])
                    new_data_in['pcreate_date'] = data[6]
                    new_data_in['preview'] = int(data[7])
                    new_data_in['preview_avg'] = float(data[8])
                    new_data_in['pcount'] = int(data[9])
                    new_data.append(new_data_in)
                    data = cursor.fetchone()

                new_data.append({"product_count": count[0]})
            else:
                connection.close()
                return Response({"product_count": 0})

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

    # 관리자 상품 중복 검사
    @action(detail=False, methods=['POST'])
    def product_check(self, request):
        # 데이터 저장을 위한 리스트 선언
        try:
            # DB 접근할 cursor
            cursor = connection.cursor()

            # POST 메소드로 날라온 Request의 데이터 각각 추출
            pname = request.data['pname']

            # SQL 쿼리문 작성
            sql_query = "SELECT * FROM skdevsec_product WHERE pname=%s"

            # DB에 명령문 전송
            cursor.execute(sql_query, (pname, ))
            data = cursor.fetchone()

            # DB와 접속 종료
            connection.close()

        # 에러가 발생했을 경우 백엔드에 에러 내용 출력 및 프론트엔드에 0 전송
        except Exception as e:
            connection.rollback()
            print(f"에러: {e}")
            return Response(0)

        # 성공 했을 시, 프론트엔드에 데이터 전송
        else:
            if data is not None:
                return Response(0)
            else:
                return Response(1)
