from django.db import connection
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from DBConnect.serializers import *


class SkdevsecBagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = SkdevsecBag.objects.all()
    serializer_class = SkdevsecBagSerializer

    # 장바구니 목록 출력
    @action(detail=False, methods=['POST'])
    def bag_show(self, request):
        new_data = list()
        try:
            cursor = connection.cursor()
            cursor_product = connection.cursor()

            unickname = request.data['unickname']

            sql_query_1 = "SELECT * FROM skdevsec_user WHERE unickname=%s"
            cursor.execute(sql_query_1, (unickname, ))
            uid = cursor.fetchone()

            if uid is not None:
                sql_query_2 = "SELECT * FROM skdevsec_bag where uid=%s"
                cursor.execute(sql_query_2, (uid[0], ))
                data = cursor.fetchone()
            else:
                connection.close()
                return Response(0)

            if data is not None:
                while data:
                    new_data_in = dict()

                    sql_query_3 = "SELECT * FROM skdevsec_product WHERE pid=%s"
                    cursor_product.execute(sql_query_3, (int(data[2]), ))
                    products = cursor_product.fetchone()

                    if products is not None:
                        new_data_in['bag_id'] = data[0]
                        new_data_in['pid'] = data[2]
                        new_data_in['pname'] = products[1]
                        new_data_in['pcate'] = products[2]
                        new_data_in['pimage'] = products[3]
                        new_data_in['ptext'] = products[4]
                        new_data_in['pprice'] = products[5]
                        new_data_in['bcount'] = data[3]
                        new_data.append(new_data_in)
                    else:
                        connection.close()
                        return Response(0)

                    data = cursor.fetchone()
            else:
                connection.close()
                return Response(0)

        except Exception as e:
            connection.rollback()
            print(f"에러: {e}")
            return Response(0)

        else:
            connection.close()
            return Response(new_data)

    # 장바구니 목록 삭제
    @action(detail=False, methods=['POST'])
    def bag_delete(self, request):
        try:
            cursor = connection.cursor()

            bag_id = int(request.data['bag_id'])

            sql_query = "DELETE FROM skdevsec_bag WHERE bag_id=%s"
            cursor.execute(sql_query, (bag_id, ))

            connection.commit()
            connection.close()

        except Exception as e:
            connection.rollback()
            print(f"에러: {e}")
            return Response(0)

        else:
            return Response(1)

    # 장바구니 등록
    @action(detail=False, methods=['POST'])
    def bag_add(self, request):
        try:
            cursor = connection.cursor()

            unickname = request.data['unickname']
            pid = int(request.data['pid'])
            bcount = int(request.data['bcount'])

            sql_query_1 = "SELECT * FROM skdevsec_user WHERE unickname=%s"
            cursor.execute(sql_query_1, (unickname, ))
            uid = cursor.fetchone()

            if uid is not None:
                sql_query_2 = "SELECT * FROM skdevsec_bag WHERE uid=%s AND pid=%s"
                cursor.execute(sql_query_2, (uid[0], pid,))
                data = cursor.fetchone()
            else:
                return Response(0)

            if data is not None:
                sql_query_3 = "UPDATE skdevsec_bag SET bcount=bcount+%s WHERE pid=%s AND uid=%s"
                cursor.execute(sql_query_3, (bcount, pid, uid[0]))
            else:
                sql_query_3 = "INSERT INTO skdevsec_bag(uid, pid, bcount) VALUES(%s, %s, %s)"
                cursor.execute(sql_query_3, (uid[0], pid, bcount))

            connection.commit()
            connection.close()

        except Exception as e:
            connection.rollback()
            print(f"에러: {e}")
            return Response(0)

        else:
            return Response(1)

    # 장바구니 갯수
    @action(detail=False, methods=['POST'])
    def bag_count(self, request):
        try:
            cursor = connection.cursor()

            unickname = request.data['unickname']

            sql_query_1 = "SELECT * FROM skdevsec_user WHERE unickname=%s"
            cursor.execute(sql_query_1, (unickname, ))
            uid = cursor.fetchone()

            if uid is not None:
                sql_query_2 = "SELECT COUNT(*) FROM skdevsec_bag where uid=%s"
                cursor.execute(sql_query_2, (uid[0], ))
                count = cursor.fetchone()
            else:
                return Response(0)

        except Exception as e:
            connection.rollback()
            print(f"에러: {e}")
            return Response(0)

        else:
            if count is not None:
                connection.close()
                return Response({"bag_count": count[0]})

            else:
                connection.close()
                return Response({"bag_count": 0})
