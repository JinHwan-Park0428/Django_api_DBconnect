# 필요한 모듈 임포트
import os
from django.db import connection
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from DBConnect.serializers import *


# 게시판 관련 테이블
class SkdevsecBoardViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = SkdevsecBoard.objects.all()
    serializer_class = SkdevsecBoardSerializer

    # sql 인젝션 되는 코드
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
            bpage = request.data['bpage']
            bpage = int(bpage)

            # SQL 쿼리문 작성
            strsql1 = "SELECT COUNT(*) FROM skdevsec_board WHERE bcate='" + bcate + "'"

            # DB에 명령문 전송
            cursor.execute(strsql1)
            datas = cursor.fetchone()

            # 게시물 갯수 저장
            new_data.append({"board_count": datas[0]})

            # SQL 쿼리문 작성
            strsql = "SELECT bid, btitle ,bfile, bview, bcomment, unickname, bcreate_date, b_lock FROM skdevsec_board where bcate='" + bcate + "' order by bid desc limit " + str(bpage * 10 - 10) + ", 10"

            # DB에 명령문 전송
            cursor.execute(strsql)
            datas = cursor.fetchone()

            # 데이터가 있으면
            if len(datas) != 0:
                # 있는 만큼 반복
                while datas:
                    # 게시물 정보를 딕셔너리에 저장 후 리스트에 추가
                    new_data_in = dict()
                    new_data_in['bid'] = datas[0]
                    new_data_in['btitle'] = datas[1]
                    new_data_in['bfile'] = datas[2]
                    new_data_in['bview'] = datas[3]
                    new_data_in['bcomment'] = datas[4]
                    new_data_in['unickname'] = datas[5]
                    new_data_in['bcreate_date'] = datas[6]
                    new_data_in['b_lock'] = datas[7]
                    new_data.append(new_data_in)
                    datas = cursor.fetchone()
            # 데이터가 없으면
            else:
                # DB와 접속 종료 및 프론트엔드에 0 전송
                connection.commit()
                connection.close()
                return Response(0)

            # DB와 접속 종료
            connection.commit()
            connection.close()

        # 에러가 발생했을 경우 백엔드에 에러 내용 출력 및 프론트엔드에 0 전송
        except Exception as e:
            connection.rollback()
            print(f"board_output 에러: {e}")
            return Response(0)

        # 데이터가 저장 됐으면, 프론트엔드에 데이터 전송
        else:
            return Response(new_data)

    # sql 인젝션 되는 코드
    # 게시물 상세 보기
    @action(detail=False, methods=['POST'])
    def board_inside(self, request):
        # 데이터 저장을 위한 딕셔너리 선언
        new_data = dict()
        try:
            # DB 접근할 cursor
            cursor = connection.cursor()

            # POST 메소드로 날라온 Request의 데이터 각각 추출
            bid = request.data['bid']

            # SQL 쿼리문 작성
            strsql1 = "UPDATE skdevsec_board SET bview = bview+1 WHERE bid='" + bid + "'"

            # DB에 명령문 전송
            cursor.execute(strsql1)

            # SQL 쿼리문 작성
            strsql2 = "SELECT * FROM skdevsec_board WHERE bid='" + bid + "'"

            # DB에 명령문 전송
            cursor.execute(strsql2)
            datas = cursor.fetchall()

            # DB와 접속 종료
            connection.commit()
            connection.close()

            # 게시물 정보 대입
            for data in datas:
                new_data['bid'] = data[0]
                new_data['btitle'] = data[1]
                new_data['btext'] = data[2]
                new_data['bfile'] = data[3]
                new_data['bview'] = data[4]
                new_data['bcomment'] = data[5]
                new_data['unickname'] = data[6]
                new_data['bcreate_date'] = data[7]
                new_data['b_lock'] = data[8]

        # 에러가 발생했을 경우 백엔드에 에러 내용 출력 및 프론트엔드에 0 전송
        except Exception as e:
            connection.rollback()
            print(f"board_inside 에러: {e}")
            return Response(0)

        # 데이터를 저장했으면, 프론트엔드에 데이터 전송
        else:
            if len(new_data) != 0:
                return Response(new_data)
            else:
                return Response(0)

    # sql 인젝션 되는 코드
    # 게시물 등록
    @action(detail=False, methods=['POST'])
    def board_upload(self, request):
        new_data = dict()
        try:
            # POST 메소드로 날라온 Request의 데이터 각각 추출
            new_data['btitle'] = request.data['btitle']
            new_data['btext'] = request.data['btext']
            new_data['bfile'] = request.data['bfile']
            new_data['bview'] = request.data['bview']
            new_data['bcomment'] = request.data['bcomment']
            new_data['unickname'] = request.data['unickname']
            new_data['bcreate_date'] = request.data['bcreate_date']
            new_data['bcate'] = request.data['bcate']
            new_data['b_lock'] = request.data['b_lock']

            # 업로드할 파일이 없으면
            if new_data['bfile'] == "0":
                # DB 접근할 cursor
                cursor = connection.cursor()

                # SQL 쿼리문 작성
                strsql = "INSERT INTO skdevsec_board(btitle, btext, bfile, bview, bcomment, unickname, bcreate_date, bcate, b_lock) VALUES('" + \
                         new_data['btitle'] + "', '" + new_data['btext'] + "', '" + new_data['bfile'] + "', '" + \
                         new_data['bview'] + "', '" + new_data['bcomment'] + "', '" + new_data['unickname'] + "', '" + \
                         new_data['bcreate_date'] + "', '" + new_data['bcate'] + "', '" + new_data['b_lock'] + "')"

                # DB에 명령문 전송
                cursor.execute(strsql)

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
                    print("serializer 에러")
                    return Response(0)

        # 에러가 발생했을 경우 백엔드에 에러 내용 출력 및 프론트엔드에 0 전송
        except Exception as e:
            connection.rollback()
            print(f"board_upload 에러: {e}")
            return Response(0)

        # 성공 했을 시, 프론트엔드에 1 전송
        else:
            return Response(1)

    # sql 인젝션 되는 코드
    # 게시물 수정
    @action(detail=False, methods=['POST'])
    def change_board(self, request):
        # 데이터 저장을 위한 딕셔너리 선언
        new_data = dict()
        new_data1 = dict()
        try:
            # DB 접근할 cursor
            cursor = connection.cursor()

            # 수정할 게시물 번호를 받아서 해당 DB를 저장
            data_check = SkdevsecBoard.objects.get(bid=request.data['bid'])

            # POST 메소드로 날라온 Request의 데이터 각각 추출
            bid = request.data['bid']
            new_data['btitle'] = request.data['btitle']
            new_data['btext'] = request.data['btext']
            new_data['bfile'] = request.data['bfile']
            new_data['bview'] = request.data['bview']
            new_data['bcomment'] = request.data['bcomment']
            new_data['unickname'] = request.data['unickname']
            new_data['bcreate_date'] = request.data['bcreate_date']
            new_data['bcate'] = request.data['bcate']
            new_data['b_lock'] = request.data['b_lock']

            # SQL 쿼리문 작성
            strsql = "SELECT bfile FROM skdevsec_board WHERE bid='" + bid + "'"

            # DB에 명령문 전송
            cursor.execute(strsql)
            datas = cursor.fetchall()

            # 게시물 기존 파일이 존재하면 삭제
            if datas[0][0] != "0":
                os.remove(datas[0][0])

            # DB에 저장하기 위해 시리얼라이저 함수 사용
            file_serializer = SkdevsecBoardSerializer(data_check, data=new_data)

            # 수정할 데이터를 업데이트함
            if file_serializer.is_valid():
                file_serializer.update(data_check, file_serializer.validated_data)
            # 업데이트 불가능하면 백엔드에 에러 알림 및 프론트엔드에 0 전송
            else:
                print("serializer 에러")
                return Response(0)

            # SQL 쿼리문 작성
            strsql1 = "SELECT * FROM skdevsec_board WHERE bid='" + bid + "'"

            # DB에 명령문 전송
            cursor.execute(strsql1)
            datas = cursor.fetchall()

            # DB와 접속 종료
            connection.commit()
            connection.close()

            # 게시물 정보 대입
            for data in datas:
                new_data1['bid'] = data[0]
                new_data1['btitle'] = data[1]
                new_data1['btext'] = data[2]
                new_data1['bfile'] = data[3]
                new_data1['bview'] = data[4]
                new_data1['bcomment'] = data[5]
                new_data1['unickname'] = data[6]
                new_data1['bcreate_date'] = data[7]
                new_data1['b_lock'] = data[8]

        # 에러가 발생했을 경우 벡엔드에 에러 내용 출력 및 프론트엔드에 0 전송
        except Exception as e:
            connection.rollback()
            print(f"change_board 에러: {e}")
            return Response(0)

        # 수정된 게시물 정보를 프론트엔드에 전송
        else:
            return Response(new_data1)

    # sql 인젝션 되는 코드
    # 게시물 삭제
    @action(detail=False, methods=['POST'])
    def board_delete(self, request):
        try:
            # DB 접근할 cursor
            cursor = connection.cursor()

            # POST 메소드로 날라온 Request의 데이터 각각 추출
            bid = request.data['bid']

            # SQL 쿼리문 작성
            strsql = "SELECT bfile FROM skdevsec_board WHERE bid='" + bid + "'"

            # DB에 명령문 전송
            cursor.execute(strsql)
            datas = cursor.fetchall()

            # 파일이 존재하면 삭제
            if datas[0][0] != "0":
                os.remove(datas[0][0])

            # SQL 쿼리문 작성
            strsql1 = "DELETE FROM skdevsec_board WHERE bid='" + bid + "'"

            # DB에 명령문 전송
            cursor.execute(strsql1)

            # DB와 접속 종료
            connection.commit()
            connection.close()

        # 에러가 발생했을 경우 백엔드에 에러 내용 출력 및 프론트엔드에 0 전송
        except Exception as e:
            connection.rollback()
            print(f"board_delete 에러: {e}")
            return Response(0)

        # 삭제되면, 프론트엔드에 1 전송
        else:
            return Response(1)

    # sql 인젝션 되는 코드
    # 파일 삭제
    @action(detail=False, methods=['POST'])
    def file_delete(self, request):
        try:
            # DB 접근할 cursor
            cursor = connection.cursor()

            # POST 메소드로 날라온 Request의 데이터 각각 추출
            bid = request.data['bid']

            # SQL 쿼리문 작성
            strsql = "SELECT bfile FROM skdevsec_board WHERE bid='" + bid + "'"

            # DB에 명령문 전송
            cursor.execute(strsql)
            datas = cursor.fetchall()

            # 파일 삭제
            if datas[0][0] != "0":
                os.remove(datas[0][0])

            # SQL 쿼리문 작성
            strsql1 = "UPDATE skdevsec_board SET bfile=0 WHERE bid='" + bid + "'"

            # DB에 명령문 전송
            cursor.execute(strsql1)

            # DB와 접속 종료
            connection.commit()
            connection.close()

        # 에러가 발생했을 경우 백엔드에 에러 내용 출력 및 프론트엔드에 0 전송
        except Exception as e:
            connection.rollback()
            print(f"file_delete 에러: {e}")
            return Response(0)

        # 성공 했을 시, 프론트엔드에 1 전송송
        else:
            return Response(1)

    # sql 인젝션 되는 코드
    # 게시물 검색
    @action(detail=False, methods=['POST'])
    def board_search(self, request):
        # 데이터 저장을 위한 리스트 선언
        new_data = list()
        count = 0
        try:
            # DB 접근할 cursor
            cursor = connection.cursor()

            # POST 메소드로 날라온 Request의 데이터 각각 추출
            bcode = request.data['bcode']
            bcate = request.data['bcate']
            bsearch = request.data['bsearch']
            bpage = request.data['bpage']
            bcode = int(bcode)
            bpage = int(bpage)

            # 검색 조건 코드 분류
            # 전체 0, 제목 1, 내용 2, 작성자 3, 제목 + 내용 4
            # SQL 쿼리문 작성
            if bcode == 0:
                strsql = "SELECT bid, btitle, bfile, bview, bcomment, unickname, bcreate_date FROM skdevsec_board WHERE (btitle LIKE '%" + bsearch + "%' OR btext LIKE '%" + bsearch + "%' OR unickname LIKE '%" + bsearch + "%') AND b_lock=0 AND bcate='" + bcate + "' ORDER BY bid DESC limit " + str(
                    bpage * 10 - 10) + ", 10"
            elif bcode == 1:
                strsql = "SELECT bid, btitle, bfile, bview, bcomment, unickname, bcreate_date FROM skdevsec_board WHERE (btitle LIKE '%" + bsearch + "%') AND b_lock=0 AND bcate='" + bcate + "' ORDER BY bid DESC limit " + str(
                    bpage * 10 - 10) + ", 10"
            elif bcode == 2:
                strsql = "SELECT bid, btitle, bfile, bview, bcomment, unickname, bcreate_date FROM skdevsec_board WHERE (btext LIKE '%" + bsearch + "%') AND b_lock=0 AND bcate='" + bcate + "' ORDER BY bid DESC limit " + str(
                    bpage * 10 - 10) + ", 10"
            elif bcode == 3:
                strsql = "SELECT bid, btitle, bfile, bview, bcomment, unickname, bcreate_date FROM skdevsec_board WHERE (unickname LIKE '%" + bsearch + "%') AND b_lock=0 AND bcate='" + bcate + "' ORDER BY bid DESC limit " + str(
                    bpage * 10 - 10) + ", 10"
            elif bcode == 4:
                strsql = "SELECT bid, btitle, bfile, bview, bcomment, unickname, bcreate_date FROM skdevsec_board WHERE (btitle LIKE '%" + bsearch + "%' OR btext LIKE '%" + bsearch + "%') AND b_lock=0 AND bcate='" + bcate + "' ORDER BY bid DESC limit " + str(
                    bpage * 10 - 10) + ", 10"
            else:
                return Response("코드 값 잘못 보냄!!")

            # DB에 명령문 전송
            cursor.execute(strsql)
            datas = cursor.fetchone()

            # 데이터가 있으면
            if datas is not None:
                # 데이터만큼 반복
                while datas:
                    count += 1
                    new_data_in = dict()
                    new_data_in['bid'] = datas[0]
                    new_data_in['btitle'] = datas[1]
                    new_data_in['bfile'] = datas[2]
                    new_data_in['bview'] = datas[3]
                    new_data_in['bcomment'] = datas[4]
                    new_data_in['unickname'] = datas[5]
                    new_data_in['bcreate_date'] = datas[6]
                    new_data_in['b_lock'] = 0
                    new_data.append(new_data_in)
                    datas = cursor.fetchone()
            # 데이터가 없으면
            else:
                # DB와 접속 종료
                connection.commit()
                connection.close()
                # 프론트엔드에 0 전송
                return Response(0)

            new_data.append({"board_count": count})

            # DB와 접속 종료
            connection.commit()
            connection.close()

        # 에러가 발생했을 경우 백엔드에 에러 내용 출력 및 프론트엔드에 0 전송
        except Exception as e:
            connection.rollback()
            print(f"board_search 에러: {e}")
            return Response(0)

        # 성공 했을 시, 프론트엔드에 데이터 전송
        else:
            return Response(new_data)

    # sql 인젝션 되는 코드
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
            bpage = request.data['bpage']
            bpage = int(bpage)

            # SQL 쿼리문 작성
            strsql = "SELECT COUNT(*) FROM skdevsec_board WHERE unickname='" + unickname + "'"

            # DB에 명령문 전송
            cursor.execute(strsql)
            datas = cursor.fetchone()

            # 게시물 갯수 저장
            new_data.append({"board_count": datas[0]})

            # SQL 쿼리문 작성
            strsql1 = "SELECT bid, btitle ,bfile, bview, bcomment, unickname, bcreate_date, bcate, b_lock FROM skdevsec_board where unickname='" + unickname + "' order by bcreate_date desc limit " + str(
                bpage * 10 - 10) + ", 10"

            # DB에 명령문 전송
            cursor.execute(strsql1)
            datas = cursor.fetchone()

            # 데이터가 있으면
            if len(datas) != 0:
                # 데이터 갯수만큼 반복
                while datas:
                    new_data_in = dict()
                    new_data_in['bid'] = datas[0]
                    new_data_in['btitle'] = datas[1]
                    new_data_in['bfile'] = datas[2]
                    new_data_in['bview'] = datas[3]
                    new_data_in['bcomment'] = datas[4]
                    new_data_in['unickname'] = datas[5]
                    new_data_in['bcreate_date'] = datas[6]
                    new_data_in['bcate'] = datas[7]
                    new_data_in['b_lock'] = datas[8]
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
            print(f"my_board 에러: {e}")
            return Response(0)

        # 성공 했을 시, 프론트엔드에 데이터 전송
        else:
            return Response(new_data)

    # sql 인젝션 되는 코드
    # 게시물 검색
    @action(detail=False, methods=['POST'])
    def my_board_search(self, request):
        # 데이터 저장을 위한 리스트 선언
        new_data = list()
        count = 0
        try:
            # DB 접근할 cursor
            cursor = connection.cursor()

            # POST 메소드로 날라온 Request의 데이터 각각 추출
            unickname = request.data['unickname']
            bsearch = request.data['bsearch']
            bpage = request.data['bpage']
            bpage = int(bpage)

            # SQL 쿼리문 작성
            strsql = "SELECT bid, btitle, bfile, bview, bcomment, unickname, bcreate_date FROM skdevsec_board WHERE (btitle LIKE '%" + bsearch + "%' OR btext LIKE '%" + bsearch + "%') AND unickname='" + unickname + "' ORDER BY bid DESC limit " + str(
                bpage * 10 - 10) + ", 10"

            # DB에 명령문 전송
            cursor.execute(strsql)
            datas = cursor.fetchone()

            # 데이터가 있으면
            if datas is not None:
                # 데이터만큼 반복
                while datas:
                    count += 1
                    new_data_in = dict()
                    new_data_in['bid'] = datas[0]
                    new_data_in['btitle'] = datas[1]
                    new_data_in['bfile'] = datas[2]
                    new_data_in['bview'] = datas[3]
                    new_data_in['bcomment'] = datas[4]
                    new_data_in['unickname'] = datas[5]
                    new_data_in['bcreate_date'] = datas[6]
                    new_data_in['b_lock'] = 0
                    new_data.append(new_data_in)
                    datas = cursor.fetchone()
            # 데이터가 없으면
            else:
                # DB와 접속 종료
                connection.commit()
                connection.close()
                # 프론트엔드에 0 전송
                return Response(0)

            new_data.append({"board_count": count})

            # DB와 접속 종료
            connection.commit()
            connection.close()

        # 에러가 발생했을 경우 백엔드에 에러 내용 출력 및 프론트엔드에 0 전송
        except Exception as e:
            connection.rollback()
            print(f"board_search 에러: {e}")
            return Response(0)

        # 성공 했을 시, 프론트엔드에 데이터 전송
        else:
            return Response(new_data)