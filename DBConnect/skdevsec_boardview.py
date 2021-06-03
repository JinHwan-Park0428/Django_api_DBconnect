import os
import re
from django.db import connection
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from . import check_file
from DBConnect.serializers import *


# 게시판 관련 테이블
class SkdevsecBoardViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = SkdevsecBoard.objects.all()
    serializer_class = SkdevsecBoardSerializer

    # 게시판 출력
    @action(detail=False, methods=['POST'])
    def board_output(self, request):
        new_data = list()

        try:
            cursor = connection.cursor()

            bcate = request.data['bcate']
            bpage = int(request.data['bpage'])

            sql_query_1 = "SELECT COUNT(*) FROM skdevsec_board WHERE bcate=%s"
            cursor.execute(sql_query_1, (bcate,))
            count = cursor.fetchone()

            if count is not None:
                new_data.append({"board_count": count[0]})

                sql_query_2 = "SELECT * FROM skdevsec_board where bcate=%s order by bid desc limit %s, 10"
                cursor.execute(sql_query_2, (bcate, bpage*10-10,))
                data = cursor.fetchone()

                while data:
                    new_data_in = dict()
                    new_data_in['bid'] = data[0]
                    new_data_in['btitle'] = data[1]
                    new_data_in['bview'] = int(data[4])
                    new_data_in['bcomment'] = int(data[5])
                    new_data_in['unickname'] = data[6]
                    new_data_in['bcreate_date'] = data[7]
                    new_data_in['b_lock'] = data[8]
                    new_data.append(new_data_in)

                    data = cursor.fetchone()
            else:
                connection.close()
                return Response({"board_count": 0})

            connection.close()

        except Exception as e:
            connection.rollback()
            print(f"에러: {e}")
            return Response(0)

        else:
            return Response(new_data)

    # 게시물 상세 보기
    @action(detail=False, methods=['POST'])
    def board_inside(self, request):
        new_data = dict()

        try:
            cursor = connection.cursor()

            bid = int(request.data['bid'])

            sql_query_1 = "UPDATE skdevsec_board SET bview = bview+1 WHERE bid=%s"
            cursor.execute(sql_query_1, (bid,))
            connection.commit()

            sql_query_2 = "SELECT * FROM skdevsec_board WHERE bid=%s"
            cursor.execute(sql_query_2, (bid,))
            data = cursor.fetchone()

            if data is not None:
                new_data['bid'] = int(data[0])
                new_data['btitle'] = data[1]
                new_data['btext'] = data[2]
                new_data['bfile'] = data[3]
                new_data['bview'] = int(data[4])
                new_data['bcomment'] = int(data[5])
                new_data['unickname'] = data[6]
                new_data['bcreate_date'] = data[7]
                new_data['bcate'] = data[8]
                new_data['b_lock'] = data[9]

            connection.close()

        except Exception as e:
            connection.rollback()
            print(f"에러: {e}")
            return Response(0)

        else:
            return Response(new_data)

    # 게시물 등록
    @action(detail=False, methods=['POST'])
    def board_upload(self, request):
        new_data = dict()

        try:
            new_data['btitle'] = request.data['btitle']
            new_data['btext'] = request.data['btext']
            new_data['bfile'] = request.data['bfile']
            new_data['bview'] = int(request.data['bview'])
            new_data['bcomment'] = int(request.data['bcomment'])
            new_data['unickname'] = request.data['unickname']
            new_data['bcreate_date'] = request.data['bcreate_date']
            new_data['bcate'] = request.data['bcate']
            new_data['b_lock'] = request.data['b_lock']

            if new_data['bfile'] == "0":
                cursor = connection.cursor()

                sql_query = "INSERT INTO skdevsec_board(btitle, btext, bfile, bview, bcomment, unickname, " \
                            "bcreate_date, bcate, b_lock) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s) "
                cursor.execute(sql_query, (new_data['btitle'], new_data['btext'], new_data['bfile'], new_data['bview'],
                                           new_data['bcomment'], new_data['unickname'], new_data['bcreate_date'],
                                           new_data['bcate'], new_data['b_lock'],))

                connection.commit()
                connection.close()
            else:
                if check_file(new_data['bfile']):
                    file_serializer = SkdevsecBoardSerializer(data=new_data)

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

    # 게시물 수정
    @action(detail=False, methods=['POST'])
    def change_board(self, request):
        new_data = dict()

        try:
            cursor = connection.cursor()

            data_check = SkdevsecBoard.objects.get(bid=int(request.data['bid']))

            bid = int(request.data['bid'])
            new_data['btitle'] = request.data['btitle']
            new_data['btext'] = request.data['btext']
            new_data['bfile'] = request.data['bfile']
            new_data['bview'] = int(request.data['bview'])
            new_data['bcomment'] = int(request.data['bcomment'])
            new_data['unickname'] = request.data['unickname']
            new_data['bcreate_date'] = request.data['bcreate_date']
            new_data['bcate'] = request.data['bcate']
            new_data['b_lock'] = request.data['b_lock']

            sql_query_1 = "SELECT bfile FROM skdevsec_board WHERE bid=%s"
            cursor.execute(sql_query_1, (bid,))
            data = cursor.fetchone()

            if new_data['bfile'] == "0":
                sql_query_2 = "UPDATE skdevsec_board SET btitle=%s, btext=%s, bfile=%s, bcate=%s, b_lock=%s WHERE bid=%s"
                cursor.execute(sql_query_2, (new_data['btitle'], new_data['btext'], new_data['bfile'],
                                             new_data['bcate'], new_data['b_lock'], bid))

                connection.commit()
            else:
                if data is not None:
                    image_path = data[0]
                else:
                    return Response(0)

                if new_data['bfile'] != image_path:
                    if check_file(new_data['bfile']):
                        file_serializer = SkdevsecBoardSerializer(data_check, data=new_data)

                        if file_serializer.is_valid():
                            file_serializer.update(data_check, file_serializer.validated_data)

                            if data[0] != "0":
                                os.remove(data[0])
                        else:
                            print(f"에러: {file_serializer.errors}")
                            return Response(0)

                    else:
                        return Response(0)

                else:
                    sql_query_3 = "UPDATE skdevsec_board SET btitle=%s, btext=%s, bcate=%s, b_lock=%s WHERE bid=%s"
                    cursor.execute(sql_query_3, (new_data['btitle'], new_data['btext'], new_data['bcate'],
                                                 new_data['b_lock'], bid))

            connection.commit()
            connection.close()

        except Exception as e:
            connection.rollback()
            print(f"에러: {e}")
            return Response(0)

        else:
            return Response(1)

    # 게시물 삭제
    @action(detail=False, methods=['POST'])
    def board_delete(self, request):
        try:
            cursor = connection.cursor()

            bid = int(request.data['bid'])

            sql_query_1 = "SELECT bfile FROM skdevsec_board WHERE bid=%s"
            cursor.execute(sql_query_1, (bid,))
            data = cursor.fetchone()

            if data is not None:
                if data[0] != "0":
                    os.remove(data[0])

            sql_query_2 = "DELETE FROM skdevsec_board WHERE bid=%s"
            cursor.execute(sql_query_2, (bid,))

            connection.commit()
            connection.close()

        except Exception as e:
            connection.rollback()
            print(f"에러: {e}")
            return Response(0)

        else:
            return Response(1)

    # 파일 삭제
    @action(detail=False, methods=['POST'])
    def file_delete(self, request):
        try:
            cursor = connection.cursor()

            bid = int(request.data['bid'])

            sql_query_1 = "SELECT bfile FROM skdevsec_board WHERE bid=%s"
            cursor.execute(sql_query_1, (bid,))
            data = cursor.fetchone()

            if data is not None:
                if data[0] != "0":
                    os.remove(data[0])

            sql_query_2 = "UPDATE skdevsec_board SET bfile=0 WHERE bid=%s"
            cursor.execute(sql_query_2, (bid,))

            connection.commit()
            connection.close()

        except Exception as e:
            connection.rollback()
            print(f"에러: {e}")
            return Response(0)

        else:
            return Response(1)

    # 게시물 검색
    @action(detail=False, methods=['POST'])
    def board_search(self, request):
        new_data = list()

        try:
            cursor = connection.cursor()

            bcode = int(request.data['bcode'])
            bcate = request.data['bcate']
            bsearch = request.data['bsearch']
            bpage = int(request.data['bpage'])

            p = re.compile('[\{\}\[\]\/?.,;:|\)*~`!@^\-+<>\#$%&\\\=\(\'\"]')
            m = p.search(bsearch)

            if m:
                return Response(0)
            else:
                # 전체 0, 제목 1, 내용 2, 작성자 3, 제목 + 내용 4
                if bcode == 0:
                    sql_query_1 = "SELECT * FROM skdevsec_board WHERE (btitle LIKE %s OR btext LIKE %s OR unickname LIKE " \
                                  "%s) AND b_lock=0 AND bcate=%s ORDER BY bid DESC limit %s, 10 "
                    sql_query_2 = "SELECT COUNT(*) FROM skdevsec_board WHERE (btitle LIKE %s OR btext LIKE %s OR " \
                                  "unickname LIKE %s) AND b_lock=0 AND bcate=%s ORDER BY bid DESC "
                    cursor.execute(sql_query_2, ('%' + bsearch + '%', '%' + bsearch + '%', '%' + bsearch + '%', bcate,))
                    count = cursor.fetchone()

                    if count is not None:
                        cursor.execute(sql_query_1, ('%' + bsearch + '%', '%' + bsearch + '%', '%' + bsearch + '%', bcate,
                                                     bpage*10-10,))
                        data = cursor.fetchone()
                    else:
                        connection.close()
                        return Response({"board_count": 0})

                elif bcode == 1:
                    sql_query_1 = "SELECT * FROM skdevsec_board WHERE (btitle LIKE %s) AND b_lock=0 AND bcate=%s ORDER BY " \
                                  "bid DESC limit %s, 10 "
                    sql_query_2 = "SELECT COUNT(*) FROM skdevsec_board WHERE (btitle LIKE %s) AND b_lock=0 AND bcate=%s " \
                                  "ORDER BY bid DESC "
                    cursor.execute(sql_query_2, ('%' + bsearch + '%', bcate,))
                    count = cursor.fetchone()

                    if count is not None:
                        cursor.execute(sql_query_1, ('%' + bsearch + '%', bcate, bpage*10-10,))
                        data = cursor.fetchone()
                    else:
                        connection.close()
                        return Response({"board_count": 0})

                elif bcode == 2:
                    sql_query_1 = "SELECT * FROM skdevsec_board WHERE (btext LIKE %s) AND b_lock=0 AND bcate=%s ORDER BY " \
                                  "bid DESC limit %s, 10 "
                    sql_query_2 = "SELECT COUNT(*) FROM skdevsec_board WHERE (btext LIKE %s) AND b_lock=0 AND bcate=%s " \
                                  "ORDER BY bid DESC "
                    cursor.execute(sql_query_2, ('%' + bsearch + '%', bcate,))
                    count = cursor.fetchone()

                    if count is not None:
                        cursor.execute(sql_query_1, ('%' + bsearch + '%', bcate, bpage*10-10,))
                        data = cursor.fetchone()
                    else:
                        connection.close()
                        return Response({"board_count": 0})

                elif bcode == 3:
                    sql_query_1 = "SELECT * FROM skdevsec_board WHERE (unickname LIKE %s) AND b_lock=0 AND bcate=%s ORDER " \
                                  "BY bid DESC limit %s, 10 "
                    sql_query_2 = "SELECT COUNT(*) FROM skdevsec_board WHERE (unickname LIKE %s) AND b_lock=0 AND " \
                                  "bcate=%s ORDER BY bid DESC "
                    cursor.execute(sql_query_2, ('%' + bsearch + '%', bcate,))
                    count = cursor.fetchone()

                    if count is not None:
                        cursor.execute(sql_query_1, ('%' + bsearch + '%', bcate, bpage*10-10,))
                        data = cursor.fetchone()
                    else:
                        connection.close()
                        return Response({"board_count": 0})

                elif bcode == 4:
                    sql_query_1 = "SELECT * FROM skdevsec_board WHERE (btitle LIKE %s OR btext LIKE %s) AND b_lock=0 AND " \
                                  "bcate=%s ORDER BY bid DESC limit %s, 10 "
                    sql_query_2 = "SELECT COUNT(*) FROM skdevsec_board WHERE (btitle LIKE %s OR btext LIKE %s) AND " \
                                  "b_lock=0 AND bcate=%s ORDER BY bid DESC "
                    cursor.execute(sql_query_2, ('%' + bsearch + '%', '%' + bsearch + '%', bcate,))
                    count = cursor.fetchone()

                    if count is not None:
                        cursor.execute(sql_query_1, ('%' + bsearch + '%', '%' + bsearch + '%', bcate, bpage*10-10,))
                        data = cursor.fetchone()
                    else:
                        connection.close()
                        return Response({"board_count": 0})

                else:
                    return Response(0)

                while data:
                    new_data_in = dict()
                    new_data_in['bid'] = int(data[0])
                    new_data_in['btitle'] = data[1]
                    new_data_in['bview'] = int(data[4])
                    new_data_in['bcomment'] = int(data[5])
                    new_data_in['unickname'] = data[6]
                    new_data_in['bcreate_date'] = data[7]
                    new_data_in['b_lock'] = data[9]
                    new_data.append(new_data_in)

                    data = cursor.fetchone()

                new_data.append({"board_count": count[0]})

                connection.close()

        except Exception as e:
            connection.rollback()
            print(f"에러: {e}")
            return Response(0)

        else:
            return Response(new_data)

    # 내 게시물 보기(마이페이지)
    @action(detail=False, methods=['POST'])
    def my_board(self, request):
        new_data = list()

        try:
            cursor = connection.cursor()

            unickname = request.data['unickname']
            bpage = int(request.data['bpage'])

            sql_query_1 = "SELECT COUNT(*) FROM skdevsec_board WHERE unickname=%s"
            cursor.execute(sql_query_1, (unickname, ))
            count = cursor.fetchone()

            if count is not None:
                new_data.append({"board_count": count[0]})

                sql_query_2 = "SELECT * FROM skdevsec_board where unickname=%s order by bcreate_date desc limit %s, 10"
                cursor.execute(sql_query_2, (unickname, bpage*10-10,))
                data = cursor.fetchone()

                while data:
                    new_data_in = dict()
                    new_data_in['bid'] = int(data[0])
                    new_data_in['btitle'] = data[1]
                    new_data_in['bview'] = int(data[4])
                    new_data_in['bcomment'] = int(data[5])
                    new_data_in['unickname'] = data[6]
                    new_data_in['bcreate_date'] = data[7]
                    new_data_in['bcate'] = data[8]
                    new_data_in['b_lock'] = data[9]
                    new_data.append(new_data_in)

                    data = cursor.fetchone()
            else:
                return Response({"board_count": 0})

            connection.close()

        except Exception as e:
            connection.rollback()
            print(f"에러: {e}")
            return Response(0)

        else:
            return Response(new_data)

    # 게시물 검색
    @action(detail=False, methods=['POST'])
    def my_board_search(self, request):
        new_data = list()

        try:
            cursor = connection.cursor()

            unickname = request.data['unickname']
            bsearch = request.data['bsearch']
            bpage = int(request.data['bpage'])

            p = re.compile('[\{\}\[\]\/?.,;:|\)*~`!@^\-+<>\#$%&\\\=\(\'\"]')
            m = p.search(bsearch)

            if m:
                return Response(0)
            else:
                sql_query_1 = "SELECT * FROM skdevsec_board WHERE (btitle LIKE %s OR btext LIKE %s) AND unickname=%s " \
                              "ORDER BY bid DESC limit %s, 10 "
                sql_query_2 = "SELECT COUNT(*) FROM skdevsec_board WHERE (btitle LIKE %s OR btext LIKE %s) AND unickname=%s"
                cursor.execute(sql_query_2, ('%' + bsearch + '%', '%' + bsearch + '%', unickname,))
                count = cursor.fetchone()

                cursor.execute(sql_query_1, ('%' + bsearch + '%', '%' + bsearch + '%', unickname, bpage*10-10))
                data = cursor.fetchone()

                if count is not None:
                    while data:
                        new_data_in = dict()
                        new_data_in['bid'] = int(data[0])
                        new_data_in['btitle'] = data[1]
                        new_data_in['bview'] = int(data[4])
                        new_data_in['bcomment'] = int(data[5])
                        new_data_in['unickname'] = data[6]
                        new_data_in['bcreate_date'] = data[7]
                        new_data_in['b_lock'] = data[9]
                        new_data.append(new_data_in)

                        data = cursor.fetchone()

                    new_data.append({"board_count": count[0]})
                else:
                    connection.close()
                    return Response({"board_count": 0})

                connection.commit()
                connection.close()

        except Exception as e:
            connection.rollback()
            print(f"에러: {e}")
            return Response(0)

        else:
            return Response(new_data)
