# 필요한 모듈 임포트
import os
import re

from django.db import connection
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from DBConnect.serializers import *


# 게시판 관련 테이블
class SkdevsecBoardViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = SkdevsecBoard.objects.all()
    serializer_class = SkdevsecBoardSerializer

    # 게시판 출력
    @action(detail=False, methods=['POST'])
    def board_output(self, request):
        # 데이터 저장을 위한 리스트 선언
        new_data = list()
        try:
            # DB 접근할 cursor
            cursor = connection.cursor()

            # POST 메소드로 날라온 Request의 데이터 각각 추출
            bcate = request.data['bcate']
            bpage = int(request.data['bpage'])

            # SQL 쿼리문 작성
            sql_query_1 = "SELECT COUNT(*) FROM skdevsec_board WHERE bcate=%s"

            # DB에 명령문 전송
            cursor.execute(sql_query_1, (bcate,))
            count = cursor.fetchone()

            if count is not None:
                # 게시물 갯수 저장
                new_data.append({"board_count": count[0]})
                # SQL 쿼리문 작성
                sql_query_2 = "SELECT * FROM skdevsec_board where bcate=%s order by bid desc limit %s, 10"

                # DB에 명령문 전송
                cursor.execute(sql_query_2, (bcate, bpage*10-10,))
                data = cursor.fetchone()

                # 있는 만큼 반복
                while data:
                    # 게시물 정보를 딕셔너리에 저장 후 리스트에 추가
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

            # DB와 접속 종료
            connection.close()

        # 에러가 발생했을 경우 백엔드에 에러 내용 출력 및 프론트엔드에 0 전송
        except Exception as e:
            connection.rollback()
            print(f"에러: {e}")
            return Response(0)

        # 데이터가 저장 됐으면, 프론트엔드에 데이터 전송
        else:
            return Response(new_data)

    # 게시물 상세 보기
    @action(detail=False, methods=['POST'])
    def board_inside(self, request):
        # 데이터 저장을 위한 딕셔너리 선언
        new_data = dict()
        try:
            # DB 접근할 cursor
            cursor = connection.cursor()

            # POST 메소드로 날라온 Request의 데이터 각각 추출
            bid = int(request.data['bid'])

            # SQL 쿼리문 작성
            sql_query_1 = "UPDATE skdevsec_board SET bview = bview+1 WHERE bid=%s"

            # DB에 명령문 전송
            cursor.execute(sql_query_1, (bid,))
            connection.commit()

            # SQL 쿼리문 작성
            sql_query_2 = "SELECT * FROM skdevsec_board WHERE bid=%s"

            # DB에 명령문 전송
            cursor.execute(sql_query_2, (bid,))
            data = cursor.fetchone()

            # 게시물 정보 대입
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

            # DB와 접속 종료
            connection.close()

        # 에러가 발생했을 경우 백엔드에 에러 내용 출력 및 프론트엔드에 0 전송
        except Exception as e:
            connection.rollback()
            print(f"에러: {e}")
            return Response(0)

        # 데이터를 저장했으면, 프론트엔드에 데이터 전송
        else:
            return Response(new_data)

    # 게시물 등록
    @action(detail=False, methods=['POST'])
    def board_upload(self, request):
        new_data = dict()
        try:
            # POST 메소드로 날라온 Request의 데이터 각각 추출
            new_data['btitle'] = request.data['btitle']
            new_data['btext'] = request.data['btext']
            new_data['bfile'] = request.data['bfile']
            new_data['bview'] = int(request.data['bview'])
            new_data['bcomment'] = int(request.data['bcomment'])
            new_data['unickname'] = request.data['unickname']
            new_data['bcreate_date'] = request.data['bcreate_date']
            new_data['bcate'] = request.data['bcate']
            new_data['b_lock'] = request.data['b_lock']

            # 업로드할 파일이 없으면
            if new_data['bfile'] == "0":
                # DB 접근할 cursor
                cursor = connection.cursor()

                # SQL 쿼리문 작성
                sql_query = "INSERT INTO skdevsec_board(btitle, btext, bfile, bview, bcomment, unickname, " \
                            "bcreate_date, bcate, b_lock) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s) "

                # DB에 명령문 전송
                cursor.execute(sql_query, (new_data['btitle'], new_data['btext'], new_data['bfile'], new_data['bview'],
                                           new_data['bcomment'], new_data['unickname'], new_data['bcreate_date'],
                                           new_data['bcate'], new_data['b_lock'],))

                # DB와 접속 종료
                connection.commit()
                connection.close()
            # 업로드할 파일이 있으면
            else:
                # DB에 저장하기 위해 시리얼라이저 함수 사용
                file_serializer = SkdevsecBoardSerializer(data=new_data)

                # 저장이 가능한 상태면 저장
                if file_serializer.is_valid():
                    file_serializer.save()

                # 저장이 불가능하면 백엔드에 에러 알림 및 프론트엔드에 0 전송
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

    # 게시물 수정
    @action(detail=False, methods=['POST'])
    def change_board(self, request):
        # 데이터 저장을 위한 딕셔너리 선언
        new_data = dict()
        try:
            # DB 접근할 cursor
            cursor = connection.cursor()

            # 수정할 게시물 번호를 받아서 해당 DB를 저장
            data_check = SkdevsecBoard.objects.get(bid=int(request.data['bid']))

            # POST 메소드로 날라온 Request의 데이터 각각 추출
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

            # SQL 쿼리문 작성
            sql_query_1 = "SELECT bfile FROM skdevsec_board WHERE bid=%s"

            # DB에 명령문 전송
            cursor.execute(sql_query_1, (bid,))
            data = cursor.fetchone()

            if new_data['bfile'] == "0":
                sql_query_2 = "UPDATE skdevsec_board SET btitle=%s, btext=%s, bfile=%s, bcate=%s, b_lock=%s WHERE bid=%s"

                # DB에 명령문 전송
                cursor.execute(sql_query_2, (new_data['btitle'], new_data['btext'], new_data['bfile'],
                                             new_data['bcate'], new_data['b_lock'], bid))
                connection.commit()
            else:
                if data is not None:
                    image_path = data[0]
                else:
                    return Response(0)

                if new_data['bfile'] != image_path:
                    # DB에 저장하기 위해 시리얼라이저 함수 사용
                    file_serializer = SkdevsecBoardSerializer(data_check, data=new_data)

                    # 수정할 데이터를 업데이트함
                    if file_serializer.is_valid():
                        file_serializer.update(data_check, file_serializer.validated_data)

                        # 게시물 기존 파일이 존재하면 삭제
                        if data[0] != "0":
                            os.remove(data[0])


                    # 업데이트 불가능하면 백엔드에 에러 알림 및 프론트엔드에 0 전송
                    else:
                        print(f"에러: {file_serializer.errors}")
                        return Response(0)
                else:
                    sql_query_3 = "UPDATE skdevsec_board SET btitle=%s, btext=%s, bcate=%s, b_lock=%s WHERE bid=%s"

                    # DB에 명령문 전송
                    cursor.execute(sql_query_3, (new_data['btitle'], new_data['btext'], new_data['bcate'],
                                                 new_data['b_lock'], bid))

            connection.commit()
            connection.close()

        # 에러가 발생했을 경우 벡엔드에 에러 내용 출력 및 프론트엔드에 0 전송
        except Exception as e:
            connection.rollback()
            print(f"에러: {e}")
            return Response(0)

        # 수정된 게시물 정보를 프론트엔드에 전송
        else:
            return Response(1)

    # 게시물 삭제
    @action(detail=False, methods=['POST'])
    def board_delete(self, request):
        try:
            # DB 접근할 cursor
            cursor = connection.cursor()

            # POST 메소드로 날라온 Request의 데이터 각각 추출
            bid = int(request.data['bid'])

            # SQL 쿼리문 작성
            sql_query_1 = "SELECT bfile FROM skdevsec_board WHERE bid=%s"

            # DB에 명령문 전송
            cursor.execute(sql_query_1, (bid,))
            data = cursor.fetchone()

            # 파일이 존재하면 삭제
            if data is not None:
                if data[0] != "0":
                    os.remove(data[0])

            # SQL 쿼리문 작성
            sql_query_2 = "DELETE FROM skdevsec_board WHERE bid=%s"

            # DB에 명령문 전송
            cursor.execute(sql_query_2, (bid,))

            # DB와 접속 종료
            connection.commit()
            connection.close()

        # 에러가 발생했을 경우 백엔드에 에러 내용 출력 및 프론트엔드에 0 전송
        except Exception as e:
            connection.rollback()
            print(f"에러: {e}")
            return Response(0)

        # 삭제되면, 프론트엔드에 1 전송
        else:
            return Response(1)

    # 파일 삭제
    @action(detail=False, methods=['POST'])
    def file_delete(self, request):
        try:
            # DB 접근할 cursor
            cursor = connection.cursor()

            # POST 메소드로 날라온 Request의 데이터 각각 추출
            bid = int(request.data['bid'])

            # SQL 쿼리문 작성
            sql_query_1 = "SELECT bfile FROM skdevsec_board WHERE bid=%s"

            # DB에 명령문 전송
            cursor.execute(sql_query_1, (bid,))
            data = cursor.fetchone()

            # 파일 삭제
            if data is not None:
                if data[0] != "0":
                    os.remove(data[0])

            # SQL 쿼리문 작성
            sql_query_2 = "UPDATE skdevsec_board SET bfile=0 WHERE bid=%s"

            # DB에 명령문 전송
            cursor.execute(sql_query_2, (bid,))

            # DB와 접속 종료
            connection.commit()
            connection.close()

        # 에러가 발생했을 경우 백엔드에 에러 내용 출력 및 프론트엔드에 0 전송
        except Exception as e:
            connection.rollback()
            print(f"에러: {e}")
            return Response(0)

        # 성공 했을 시, 프론트엔드에 1 전송송
        else:
            return Response(1)

    # 게시물 검색
    @action(detail=False, methods=['POST'])
    def board_search(self, request):
        # 데이터 저장을 위한 리스트 선언
        new_data = list()
        try:
            # DB 접근할 cursor
            cursor = connection.cursor()

            # POST 메소드로 날라온 Request의 데이터 각각 추출
            bcode = int(request.data['bcode'])
            bcate = request.data['bcate']
            bsearch = request.data['bsearch']
            bpage = int(request.data['bpage'])

            p = re.compile('[\{\}\[\]\/?.,;:|\)*~`!@^\-+<>\#$%&\\\=\(\'\"]')

            m = p.search(bsearch)

            if m:
                return Response(0)
            else:
                # 검색 조건 코드 분류
                # 전체 0, 제목 1, 내용 2, 작성자 3, 제목 + 내용 4
                # SQL 쿼리문 작성
                if bcode == 0:
                    sql_query_1 = "SELECT * FROM skdevsec_board WHERE (btitle LIKE %s OR btext LIKE %s OR unickname LIKE " \
                                  "%s) AND b_lock=0 AND bcate=%s ORDER BY bid DESC limit %s, 10 "
                    sql_query_2 = "SELECT COUNT(*) FROM skdevsec_board WHERE (btitle LIKE %s OR btext LIKE %s OR " \
                                  "unickname LIKE %s) AND b_lock=0 AND bcate=%s ORDER BY bid DESC "

                    cursor.execute(sql_query_2, ('%' + bsearch + '%', '%' + bsearch + '%', '%' + bsearch + '%', bcate,))
                    count = cursor.fetchone()

                    if count is not None:
                        # DB에 명령문 전송
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
                        # DB에 명령문 전송
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
                        # DB에 명령문 전송
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
                        # DB에 명령문 전송
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
                        # DB에 명령문 전송
                        cursor.execute(sql_query_1, ('%' + bsearch + '%', '%' + bsearch + '%', bcate, bpage*10-10,))
                        data = cursor.fetchone()
                    else:
                        connection.close()
                        return Response({"board_count": 0})

                else:
                    return Response(0)

                # 데이터만큼 반복
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

    # 내 게시물 보기(마이페이지)
    @action(detail=False, methods=['POST'])
    def my_board(self, request):
        # 데이터 저장하기 위한 리스트 선언
        new_data = list()
        try:
            # DB 접근할 cursor
            cursor = connection.cursor()

            # POST 메소드로 날라온 Request의 데이타 각각 추출
            unickname = request.data['unickname']
            bpage = int(request.data['bpage'])

            # SQL 쿼리문 작성
            sql_query_1 = "SELECT COUNT(*) FROM skdevsec_board WHERE unickname=%s"

            # DB에 명령문 전송
            cursor.execute(sql_query_1, (unickname, ))
            count = cursor.fetchone()

            if count is not None:
                # 게시물 갯수 저장
                new_data.append({"board_count": count[0]})

                # SQL 쿼리문 작성
                sql_query_2 = "SELECT * FROM skdevsec_board where unickname=%s order by bcreate_date desc limit %s, 10"

                # DB에 명령문 전송
                cursor.execute(sql_query_2, (unickname, bpage*10-10,))
                data = cursor.fetchone()

                # 데이터 갯수만큼 반복
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

    # 게시물 검색
    @action(detail=False, methods=['POST'])
    def my_board_search(self, request):
        # 데이터 저장을 위한 리스트 선언
        new_data = list()
        try:
            # DB 접근할 cursor
            cursor = connection.cursor()

            # POST 메소드로 날라온 Request의 데이터 각각 추출
            unickname = request.data['unickname']
            bsearch = request.data['bsearch']
            bpage = int(request.data['bpage'])

            p = re.compile('[\{\}\[\]\/?.,;:|\)*~`!@^\-+<>\#$%&\\\=\(\'\"]')

            m = p.search(bsearch)

            if m:
                return Response(0)
            else:
                # SQL 쿼리문 작성
                sql_query_1 = "SELECT * FROM skdevsec_board WHERE (btitle LIKE %s OR btext LIKE %s) AND unickname=%s " \
                              "ORDER BY bid DESC limit %s, 10 "
                sql_query_2 = "SELECT COUNT(*) FROM skdevsec_board WHERE (btitle LIKE %s OR btext LIKE %s) AND unickname=%s"

                # DB에 명령문 전송
                cursor.execute(sql_query_2, ('%' + bsearch + '%', '%' + bsearch + '%', unickname,))
                count = cursor.fetchone()

                # DB에 명령문 전송
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
            return Response(new_data)
