from django.db import connection
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from DBConnect.serializers import *


class SkdevsecCommentViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = SkdevsecComment.objects.all()
    serializer_class = SkdevsecCommentSerializer

    # 댓글 출력
    @action(detail=False, methods=['POST'])
    def view_comment(self, request):
        new_data = list()

        try:
            cursor = connection.cursor()

            bid = int(request.data['bid'])
            cpage = int(request.data['cpage'])

            sql_query_1 = "SELECT COUNT(*) FROM skdevsec_comment WHERE bid=%s"
            cursor.execute(sql_query_1, (bid, ))
            count = cursor.fetchone()

            if count is not None:
                new_data.append({"comment_count": count[0]})

                sql_query_2 = "SELECT * FROM skdevsec_comment where bid=%s order by cid LIMIT %s, 10"
                cursor.execute(sql_query_2, (bid, cpage*10-10))
                data = cursor.fetchone()

                while data:
                    new_data_in = dict()
                    new_data_in['cid'] = int(data[0])
                    new_data_in['unickname'] = data[2]
                    new_data_in['ctext'] = data[3]
                    new_data_in['ccreate_date'] = data[4]
                    new_data_in['clock'] = data[5]
                    new_data.append(new_data_in)

                    data = cursor.fetchone()
            else:
                connection.close()
                return Response({"comment_count": 0})

            connection.close()

        except Exception as e:
            connection.rollback()
            print(f"에러: {e}")
            return Response(0)

        else:
            return Response(new_data)

    # 댓글 작성
    @action(detail=False, methods=['POST'])
    def comment_write(self, request):
        try:
            cursor = connection.cursor()

            bid = int(request.data['bid'])
            unickname = request.data['unickname']
            ctext = request.data['ctext']
            ccreate_date = request.data['ccreate_date']
            clock = request.data['clock']

            sql_query_1 = "INSERT INTO skdevsec_comment(bid, unickname, ctext, ccreate_date, clock) VALUES(%s, %s, %s, %s, %s)"
            cursor.execute(sql_query_1, (bid, unickname, ctext, ccreate_date, clock, ))
            connection.commit()

            sql_query_2 = "UPDATE skdevsec_board SET bcomment=bcomment+1 WHERE bid=%s"
            cursor.execute(sql_query_2, (bid, ))

            connection.commit()
            connection.close()

        except Exception as e:
            connection.rollback()
            print(f"에러: {e}")
            return Response(0)

        else:
            return Response(1)

    # 댓글 삭제
    @action(detail=False, methods=['POST'])
    def comment_delete(self, request):
        try:
            cursor = connection.cursor()

            bid = int(request.data['bid'])
            cid = int(request.data['cid'])

            sql_query_1 = "DELETE FROM skdevsec_comment WHERE cid=%s"
            cursor.execute(sql_query_1, (cid, ))
            connection.commit()

            sql_query_2 = "UPDATE skdevsec_board SET bcomment=bcomment-1 WHERE bid=%s"
            cursor.execute(sql_query_2, (bid, ))

            connection.commit()
            connection.close()

        except Exception as e:
            connection.rollback()
            print(f"에러: {e}")
            return Response(0)

        else:
            return Response(1)
