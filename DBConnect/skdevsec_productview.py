import os
import re
from django.db import connection
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from . import check_file
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
            cursor = connection.cursor()

            ppage = int(request.data['ppage'])

            sql_query_1 = "SELECT COUNT(*) FROM skdevsec_product"
            cursor.execute(sql_query_1)
            count = cursor.fetchone()

            if count is not None:
                new_data.append({"product_count": count[0]})

                sql_query_2 = "SELECT * FROM skdevsec_product order by pid desc limit %s, 8"
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

            connection.close()

        except Exception as e:
            connection.rollback()
            print(f"에러: {e}")
            return Response(0)

        else:
            return Response(new_data)

    # 상품상세 페이지 출력
    @action(detail=False, methods=['POST'])
    def product_inside(self, request):
        new_data = list()
        try:
            cursor = connection.cursor()

            pid = int(request.data['pid'])

            sql_query = "SELECT * FROM skdevsec_product WHERE pid=%s"
            cursor.execute(sql_query, (pid, ))
            data = cursor.fetchone()

            if data is not None:
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

    # 상품 등록
    @action(detail=False, methods=['POST'])
    def product_upload(self, request):
        new_data = dict()

        try:
            new_data['pname'] = request.data['pname']
            new_data['pcate'] = request.data['pcate']
            new_data['pimage'] = request.data['pimage']
            new_data['ptext'] = request.data['ptext']
            new_data['pprice'] = int(request.data['pprice'])
            new_data['pcreate_date'] = request.data['pcreate_date']
            new_data['preview'] = request.data['preview']
            new_data['preview_avg'] = float(request.data['preview_avg'])
            new_data['pcount'] = int(request.data['pcount'])

            if check_file(new_data['pimage']):
                file_serializer = SkdevsecProductSerializer(data=new_data)

                if file_serializer.is_valid():
                    file_serializer.save()
                else:
                    print(f"에러: {file_serializer.errors}")
                    return Response(0)

            else:
                return Response(0)

        except Exception as e:
            connection.rollback()
            print(f"에러: {e}")
            return Response(0)

        else:
            return Response(1)

    # 상품 수정
    @action(detail=False, methods=['POST'])
    def change_product(self, request):
        new_data = dict()

        try:
            cursor = connection.cursor()

            data_check = SkdevsecProduct.objects.get(pid=int(request.data['pid']))

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

            sql_query_1 = "SELECT * FROM skdevsec_product WHERE pid=%s"
            cursor.execute(sql_query_1, (pid, ))
            data = cursor.fetchone()

            if data is not None:
                image_path = data[3]
            else:
                return Response(0)

            file_serializer = SkdevsecProductSerializer(data_check, data=new_data)

            if new_data['pimage'] != image_path:
                if check_file(new_data['pimage']):
                    if file_serializer.is_valid():
                        file_serializer.update(data_check, file_serializer.validated_data)

                        if data[3] != "0":
                            os.remove(data[3])

                    else:
                        print(f"에러: {file_serializer.errors}")
                        return Response(0)

                else:
                    return Response(0)

            else:
                sql_query_2 = "UPDATE skdevsec_product SET pname=%s, pcate=%s, ptext=%s, pprice=%s, pcount=%s WHERE " \
                              "pid=%s "
                cursor.execute(sql_query_2, (new_data['pname'], new_data['pcate'], new_data['ptext'],
                                             new_data['pprice'], new_data['pcount'], pid,))

            connection.commit()
            connection.close()

        except Exception as e:
            connection.rollback()
            print(f"에러: {e}")
            return Response(0)

        else:
            return Response(1)

    # 상품 삭제
    @action(detail=False, methods=['POST'])
    def product_delete(self, request):
        try:
            cursor = connection.cursor()

            pid = int(request.data['pid'])

            sql_query_1 = "SELECT * FROM skdevsec_product WHERE pid=%s"
            cursor.execute(sql_query_1, (pid, ))
            data = cursor.fetchone()

            if data is not None:
                if data[3] != "0":
                    os.remove(data[3])

            else:
                return Response(0)

            sql_query_2 = "DELETE FROM skdevsec_product WHERE pid=%s"
            cursor.execute(sql_query_2, (pid, ))

            connection.commit()
            connection.close()

        except Exception as e:
            connection.rollback()
            print(f"에러: {e}")
            return Response(0)

        else:
            return Response(1)

    # 상품 검색
    @action(detail=False, methods=['POST'])
    def product_search(self, request):
        new_data = list()

        try:
            cursor = connection.cursor()

            psearch = request.data

            p = re.compile('[\{\}\[\]\/?.,;:|\)*~`!@^\-+<>\#$%&\\\=\(\'\"]')
            m = p.search(psearch[1])

            if m:
                return Response(0)
            else:
                # psearch = ["페이지", "검색단어", "카테고리", "카테고리", ...]
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
                cursor.execute(sql_query2, ('%' + psearch[1] + '%', ))
                count = cursor.fetchone()

                cursor.execute(sql_query1, ('%' + psearch[1] + '%', int(psearch[0])*8-8,))
                data = cursor.fetchone()

                if count is not None:
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

                connection.close()

        except Exception as e:
            connection.rollback()
            print(f"에러: {e}")
            return Response(0)

        else:
            return Response(new_data)

    # 메인에서 최신순 상품 리스트 출력
    @action(detail=False, methods=['POST'])
    def latest_item_list(self, request):
        new_data = list()

        try:
            cursor = connection.cursor()

            ppage = int(request.data['ppage'])

            sql_query_1 = "SELECT COUNT(*) FROM skdevsec_product ORDER BY pcreate_date DESC limit %s, 8"
            cursor.execute(sql_query_1, (ppage*8-8, ))
            count = cursor.fetchone()

            if count is not None:
                new_data.append({"product_count": count[0]})

                sql_query_2 = "SELECT * FROM skdevsec_product order by pcreate_date desc limit %s, 8"
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

            connection.close()

        except Exception as e:
            connection.rollback()
            print(f"에러: {e}")
            return Response(0)

        else:
            return Response(new_data)

    # 메인에서 가격높은순 상품 리스트 출력
    @action(detail=False, methods=['POST'])
    def highest_item_list(self, request):
        new_data = list()

        try:
            cursor = connection.cursor()

            ppage = int(request.data['ppage'])

            sql_query_1 = "SELECT COUNT(*) FROM skdevsec_product ORDER BY pprice DESC limit %s, 8"
            cursor.execute(sql_query_1, (ppage*8-8, ))
            count = cursor.fetchone()

            if count is not None:
                new_data.append({"product_count": count[0]})

                sql_query_2 = "SELECT * FROM skdevsec_product order by pprice desc limit %s, 8"
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
                connection.close({"product_count": 0})

            connection.close()

        except Exception as e:
            connection.rollback()
            print(f"에러:{e}")
            return Response(0)

        else:
            return Response(new_data)

    # 메인에서 가격낮은순 상품 리스트 출력
    @action(detail=False, methods=['POST'])
    def rowest_item_list(self, request):
        new_data = list()

        try:
            cursor = connection.cursor()

            ppage = int(request.data['ppage'])

            sql_query_1 = "SELECT COUNT(*) FROM skdevsec_product ORDER BY pprice DESC limit %s, 8"
            cursor.execute(sql_query_1, (ppage*8-8, ))
            count = cursor.fetchone()

            if count is not None:
                new_data.append({"product_count": count[0]})

                sql_query_2 = "SELECT * FROM skdevsec_product order by pprice asc limit 8"
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

            connection.close()

        except Exception as e:
            connection.rollback()
            print(f"에러: {e}")
            return Response(0)

        else:
            return Response(new_data)

    # 메인에서 인기순 상품 리스트 출력
    @action(detail=False, methods=['POST'])
    def best_item_list(self, request):
        new_data = list()

        try:
            cursor = connection.cursor()

            ppage = int(request.data['ppage'])

            sql_query_1 = "SELECT COUNT(*) FROM skdevsec_product order by preview DESC, preview_avg DESC limit %s, 8"
            cursor.execute(sql_query_1, (ppage*8-8, ))
            count = cursor.fetchone()

            if count is not None:
                new_data.append({"product_count": count[0]})

                sql_query_2 = "SELECT * FROM skdevsec_product order by preview DESC, preview_avg DESC LIMIT 8"
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

            connection.close()

        except Exception as e:
            connection.rollback()
            print(f"에러: {e}")
            return Response(0)

        else:
            return Response(new_data)

    # 관리자 상품 검색
    @action(detail=False, methods=['POST'])
    def admin_product_search(self, request):
        new_data = list()

        try:
            cursor = connection.cursor()

            psearch = request.data['psearch']
            ppage = int(request.data['ppage'])
            pcode = int(request.data['pcode'])

            p = re.compile('[\{\}\[\]\/?.,;:|\)*~`!@^\-+<>\#$%&\\\=\(\'\"]')
            m = p.search(psearch)

            if m:
                return Response(0)
            else:
                # 0 : 전체 검색 / 1 : 상품 명 검색 / 2 : 카테고리 검색
                if pcode == 0:
                    sql_query_1 = "SELECT * FROM skdevsec_product WHERE (pname LIKE %s OR pcate LIKE %s) ORDER BY pid " \
                                  "DESC limit %s, 8 "
                    sql_query_2 = "SELECT COUNT(*) FROM skdevsec_product WHERE (pname LIKE %s OR pcate LIKE %s)"
                    cursor.execute(sql_query_2, ('%' + psearch + '%', '%' + psearch + '%',))
                    count = cursor.fetchone()

                    cursor.execute(sql_query_1, ('%' + psearch + '%', '%' + psearch + '%', ppage*8-8,))
                    data = cursor.fetchone()

                elif pcode == 1:
                    sql_query_1 = "SELECT * FROM skdevsec_product WHERE pname LIKE %s ORDER BY pid DESC limit %s, 8"
                    sql_query_2 = "SELECT COUNT(*) FROM skdevsec_product WHERE pname LIKE %s"
                    cursor.execute(sql_query_2, ('%' + psearch + '%', ))
                    count = cursor.fetchone()

                    cursor.execute(sql_query_1, ('%' + psearch + '%', ppage*8-8,))
                    data = cursor.fetchone()

                elif pcode == 2:
                    sql_query_1 = "SELECT * FROM skdevsec_product WHERE pcate LIKE %s ORDER BY pid DESC limit %s, 8"
                    sql_query_2 = "SELECT COUNT(*) FROM skdevsec_product WHERE pcate LIKE %s"
                    cursor.execute(sql_query_2, ('%' + psearch.upper() + '%',))
                    count = cursor.fetchone()

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

                connection.close()

        except Exception as e:
            connection.rollback()
            print(f"에러: {e}")
            return Response(0)

        else:
            return Response(new_data)

    # 관리자 상품 중복 검사
    @action(detail=False, methods=['POST'])
    def product_check(self, request):
        try:
            cursor = connection.cursor()

            pname = request.data['pname']

            sql_query = "SELECT * FROM skdevsec_product WHERE pname=%s"
            cursor.execute(sql_query, (pname, ))
            data = cursor.fetchone()

            connection.close()

        except Exception as e:
            connection.rollback()
            print(f"에러: {e}")
            return Response(0)

        else:
            if data is not None:
                return Response(0)
            else:
                return Response(1)
