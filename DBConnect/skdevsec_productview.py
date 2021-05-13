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

            if datas is not None:
                # 상품 갯수 저장
                new_data.append({"product_count": datas[0]})
            else:
                new_data.append({"product_count": 0})

            # SQL 쿼리문 작성
            strsql1 = "SELECT * FROM skdevsec_product order by pid desc limit " + str(ppage * 8 - 8) + ", 8"

            # DB에 명령문 전송
            cursor.execute(strsql1)
            datas = cursor.fetchone()

            # 데이터가 있으면
            if datas is not None:
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
            if datas is not None:
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
                print(file_serializer.errors)
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
            datas = cursor.fetchone()

            if datas is not None:
                image_path = datas[0]
                image_name = image_path.split("/")[1]
            else:
                return Response(0)

            # DB에 저장하기 위해 시리얼라이저 함수 사용
            file_serializer = SkdevsecProductSerializer(data_check, data=new_data)

            # 수정할 데이터를 업데이트함
            if new_data['pimage'] != image_name:
                if file_serializer.is_valid():
                    file_serializer.update(data_check, file_serializer.validated_data)
                    # 파일이 존재하면 삭제
                    if datas[0] != "0":
                        os.remove(datas[0])
                # 불가능한 상태면 에러 알림 및 프론트엔드에 0 전송
                else:
                    print("serializer 에러")
                    return Response(0)
            else:
                strsql1 = "UPDATE skdevsec_product SET pname='" + new_data['pname'] + "', pcate='" + new_data['pcate'] + \
                          "', ptext='" + new_data['ptext'] + "', pprice='" + new_data['pprice'] + "', pcount='" + \
                          new_data['pcount'] + \
                          "' WHERE pid='" + pid + "'"

                # DB에 명령문 전송
                cursor.execute(strsql1)

            connection.commit()
            connection.close()
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
            datas = cursor.fetchone()

            if datas is not None:
                # 파일이 존재하면 삭제
                if datas[0] != "0":
                    os.remove(datas[0])
            else:
                return Response(0)

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
            psearch = request.data

            # psearch = ["페이지", "검색단어", "카테고리", "카테고리", ...]
            # SQL 쿼리문 작성
            strsql = "SELECT pid, pcate, pimage, pname, pprice, preview, preview_avg FROM skdevsec_product WHERE (pname LIKE '%" + \
                     psearch[1] + "%')"
            strsql1 = "SELECT COUNT(*) FROM skdevsec_product WHERE (pname LIKE '%" + \
                      psearch[1] + "%')"
            if len(psearch) >= 3:
                if psearch[2] == "":
                    strsql = "SELECT pid, pcate, pimage, pname, pprice, preview, preview_avg FROM skdevsec_product WHERE (pname LIKE '%" + \
                             psearch[1] + "%')"
                    strsql1 = "SELECT COUNT(*) FROM skdevsec_product WHERE (pname LIKE '%" + \
                              psearch[1] + "%')"
                else:
                    strsql = strsql + " AND (pcate='"
                    strsql1 = strsql1 + " AND (pcate='"
                    for pcate in psearch[1:]:
                        strsql = strsql + pcate + "' OR pcate='"
                        strsql1 = strsql1 + pcate + "' OR pcate='"
                    strsql = strsql + "')"
                    strsql1 = strsql1 + "')"
            strsql = strsql + " ORDER BY pid DESC limit " + str(int(psearch[0]) * 8 - 8) + ", 8"

            # DB에 명령문 전송
            cursor.execute(strsql1)
            count = cursor.fetchone()

            # DB에 명령문 전송
            cursor.execute(strsql)
            datas = cursor.fetchone()

            # 데이터가 있으면
            if datas is not None:
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
                if count is not None:
                    new_data.append({"product_count": count[0]})
                else:
                    new_data.append({"product_count": 0})
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

    # sql 인젝션 되는 코드
    # 메인에서 최신순 상품 리스트 출력
    @action(detail=False, methods=['POST'])
    def latest_item_list(self, request):
        # 데이터 저장을 위한 리스트 선언
        new_data = list()
        try:
            # DB 접근할 cursor
            cursor = connection.cursor()

            ppage = request.data['ppage']
            ppage = int(ppage)

            strsql = "SELECT COUNT(*) FROM skdevsec_product ORDER BY pcreate_date DESC limit " + str(
                ppage * 8 - 8) + ", 8"

            # DB에 명령문 전송
            cursor.execute(strsql)
            count = cursor.fetchone()

            if count is not None:
                new_data.append({"product_count": count[0]})
            else:
                new_data.append({"product_count": 0})

            # SQL 쿼리문 작성
            strsql1 = "SELECT * FROM skdevsec_product order by pcreate_date desc limit " + str(ppage * 8 - 8) + ", 8"

            # DB에 명령문 전송
            cursor.execute(strsql1)
            datas = cursor.fetchone()

            # 데이터가 있으면
            if datas is not None:
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
                # 프론트엔드로 0 전송
                return Response(0)

            # DB와 접속 종료
            connection.commit()
            connection.close()

            # 에러가 발생했을 경우 에러 내용 출력
        except Exception as e:
            connection.rollback()
            print(f"latest_item_list 에러: {e}")
            return Response(0)

        # 성공 했을 시, 프론트엔드로 데이터 전송
        else:
            return Response(new_data)

    # sql 인젝션 되는 코드
    # 메인에서 가격높은순 상품 리스트 출력
    @action(detail=False, methods=['POST'])
    def highest_item_list(self, request):
        # 데이터 저장을 위한 리스트 선언
        new_data = list()
        try:
            # DB 접근할 cursor
            cursor = connection.cursor()

            ppage = request.data['ppage']
            ppage = int(ppage)

            strsql = "SELECT COUNT(*) FROM skdevsec_product ORDER BY pprice DESC limit " + str(
                ppage * 8 - 8) + ", 8"

            # DB에 명령문 전송
            cursor.execute(strsql)
            count = cursor.fetchone()
            if count is not None:
                new_data.append({"product_count": count[0]})
            else:
                new_data.append({"product_count": 0})

            # SQL 쿼리문 작성
            strsql1 = "SELECT * FROM skdevsec_product order by pprice desc limit " + str(ppage * 8 - 8) + ", 8"

            # DB에 명령문 전송
            cursor.execute(strsql1)
            datas = cursor.fetchone()

            # 데이터가 있으면
            if datas is not None:
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
                # 프론트엔드로 0 전송
                return Response(0)

            # DB와 접속 종료
            connection.commit()
            connection.close()

        # 에러가 발생했을 경우 백엔드에 에러 내용 출력 및 프론트엔드에 0 전송
        except Exception as e:
            connection.rollback()
            print(f"highest_item_list 에러:{e}")
            return Response(0)

        # 성공 했을 시, 프론트엔드에 데이터 전송
        else:
            return Response(new_data)

    # sql 인젝션 되는 코드
    # 메인에서 가격낮은순 상품 리스트 출력
    @action(detail=False, methods=['POST'])
    def rowest_item_list(self, request):
        # 데이터 저장을 위한 리스트 선언
        new_data = list()
        try:
            # DB 접근할 cursor
            cursor = connection.cursor()

            ppage = request.data['ppage']
            ppage = int(ppage)

            strsql = "SELECT COUNT(*) FROM skdevsec_product ORDER BY pprice DESC limit " + str(
                ppage * 8 - 8) + ", 8"

            # DB에 명령문 전송
            cursor.execute(strsql)
            count = cursor.fetchone()
            if count is not None:
                new_data.append({"product_count": count[0]})
            else:
                new_data.append({"product_count": 0})

            # SQL 쿼리문 작성
            strsql1 = "SELECT * FROM skdevsec_product order by pprice asc limit 8"

            # DB에 명령문 전송
            cursor.execute(strsql1)
            datas = cursor.fetchone()

            # 데이터가 있으면
            if datas is not None:
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
                # 프론트엔드로 0 전송
                return Response(0)

            # DB와 접속 종료
            connection.commit()
            connection.close()

        # 에러가 발생했을 경우 백엔드에 에러 내용 출력 및 프론트엔드에 0 전송
        except Exception as e:
            connection.rollback()
            print(f"rowest_item_list 에러: {e}")
            return Response(0)

        # 성공 했을 시, 프론트엔드에 데이터 전송
        else:
            return Response(new_data)

    # sql 인젝션 되는 코드
    # 메인에서 인기순 상품 리스트 출력
    @action(detail=False, methods=['POST'])
    def best_item_list(self, request):
        # 데이터 저장을 위한 리스트 선언
        new_data = list()
        try:
            # DB 접근할 cursor
            cursor = connection.cursor()

            ppage = request.data['ppage']
            ppage = int(ppage)

            strsql = "SELECT COUNT(*) FROM skdevsec_product order by preview DESC, preview_avg DESC limit " + str(
                ppage * 8 - 8) + ", 8"

            # DB에 명령문 전송
            cursor.execute(strsql)
            count = cursor.fetchone()

            if count is not None:
                new_data.append({"product_count": count[0]})
            else:
                new_data.append({"product_count": 0})

            # SQL 쿼리문 작성
            strsql = "SELECT * FROM skdevsec_product order by preview DESC, preview_avg DESC LIMIT 8"

            # DB에 명령문 전송
            cursor.execute(strsql)
            datas = cursor.fetchone()

            # 데이터가 있으면
            if datas is not None:
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
            print(f"best_item_list 에러: {e}")
            return Response(0)

        # 성공 했을 시, 프론트엔드에 데이터 전송
        else:
            return Response(new_data)

    # sql 인젝션 되는 코드
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
            ppage = request.data['ppage']
            pcode = request.data['pcode']
            pcode = int(pcode)
            ppage = int(ppage)

            # SQL 쿼리문 작성
            # 0 : 전체 검색 / 1 : 상품 명 검색 / 2 : 카테고리 검색
            if pcode == 0:
                strsql = "SELECT * FROM skdevsec_product WHERE (pname LIKE '%" + psearch + "%' OR pcate LIKE '%" + psearch + "%') ORDER BY pid DESC limit " + str(
                    ppage * 8 - 8) + ", 8"
                strsql1 = "SELECT COUNT(*) FROM skdevsec_product WHERE (pname LIKE '%" + psearch + "%' OR pcate LIKE '%" + psearch + "%')"
            elif pcode == 1:
                strsql = "SELECT * FROM skdevsec_product WHERE pname LIKE '%" + psearch + "%' ORDER BY pid DESC limit " + str(
                    ppage * 8 - 8) + ", 8"
                strsql1 = "SELECT COUNT(*) FROM skdevsec_product WHERE pname LIKE '%" + psearch + "%'"
            elif pcode == 2:
                strsql = "SELECT * FROM skdevsec_product WHERE pcate LIKE '%" + psearch.upper() + "%' ORDER BY pid DESC limit " + str(
                    ppage * 8 - 8) + ", 8"
                strsql1 = "SELECT COUNT(*) FROM skdevsec_product WHERE pcate LIKE '%" + psearch.upper() + "%'"
            else:
                return Response(0)

            # DB에 명령문 전송
            cursor.execute(strsql)
            count = cursor.fetchone()

            # DB에 명령문 전송
            cursor.execute(strsql)
            datas = cursor.fetchone()

            # 데이터가 있으면
            if datas is not None:
                # 데이터만큼 반복
                while datas:
                    count += 1
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
            if count is not None:
                new_data.append({"product_count": count[0]})
            else:
                new_data.append({"product_count": 0})

            # DB와 접속 종료
            connection.commit()
            connection.close()

        # 에러가 발생했을 경우 백엔드에 에러 내용 출력 및 프론트엔드에 0 전송
        except Exception as e:
            connection.rollback()
            print(f"admin_product_search 에러: {e}")
            return Response(0)

        # 성공 했을 시, 프론트엔드에 데이터 전송
        else:
            return Response(new_data)

    # sql 인젝션 되는 코드
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
            strsql = "SELECT * FROM skdevsec_product WHERE pname='" + pname + "'"

            # DB에 명령문 전송
            cursor.execute(strsql)
            datas = cursor.fetchall()

            # DB와 접속 종료
            connection.commit()
            connection.close()

        # 에러가 발생했을 경우 백엔드에 에러 내용 출력 및 프론트엔드에 0 전송
        except Exception as e:
            connection.rollback()
            print(f"product_check 에러: {e}")
            return Response(0)

        # 성공 했을 시, 프론트엔드에 데이터 전송
        else:
            if len(datas) != 0:
                return Response(0)
            else:
                return Response(1)
