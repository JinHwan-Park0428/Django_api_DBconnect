from django.db import connection
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from DBConnect.serializers import *


# 상품 리뷰 관련 테이블
class SkdevsecReviewViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = SkdevsecReview.objects.all()
    serializer_class = SkdevsecReviewSerializer

    # 리뷰 출력
    @action(detail=False, methods=['POST'])
    def review_output(self, request):
        new_data = list()

        try:
            cursor = connection.cursor()

            pid = int(request.data['pid'])

            sql_query = "SELECT * FROM skdevsec_review where pid=%s order by rid desc"
            cursor.execute(sql_query, (pid,))
            data = cursor.fetchone()

            if data is not None:
                while data:
                    new_data_in = dict()
                    new_data_in['rid'] = int(data[0])
                    new_data_in['rstar'] = float(data[2])
                    new_data_in['unickname'] = data[3]
                    new_data_in['rcreate_date'] = data[4]
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

    # 리뷰 작성
    @action(detail=False, methods=['POST'])
    def review_write(self, request):
        try:
            cursor = connection.cursor()

            pid = int(request.data['pid'])
            rstar = float(request.data['rstar'])
            unickname = request.data['unickname']
            rcreate_date = request.data['rcreate_date']

            sql_query_1 = "INSERT INTO skdevsec_review(pid, rstar, unickname, rcreate_date) VALUES(%s, %s, %s, %s)"
            cursor.execute(sql_query_1, (pid, rstar, unickname, rcreate_date))
            connection.commit()

            sql_query_2 = "UPDATE skdevsec_product SET preview = (SELECT COUNT(*) FROM skdevsec_review WHERE pid=%s), " \
                          "preview_avg =(SELECT round(avg(rstar),1) FROM skdevsec_review WHERE pid=%s)  WHERE pid=%s "
            cursor.execute(sql_query_2, (pid, pid, pid))

            connection.commit()
            connection.close()

        except Exception as e:
            connection.rollback()
            print(f"에러: {e}")
            return Response(0)

        else:
            return Response(1)

    # 리뷰 삭제
    @action(detail=False, methods=['POST'])
    def comment_delete(self, request):
        try:
            cursor = connection.cursor()

            rid = int(request.data['rid'])
            pid = int(request.data['pid'])
            unickname = request.data['unickname']

            sql_query_1 = "DELETE FROM skdevsec_review WHERE rid=%s and unickname=%s"
            cursor.execute(sql_query_1, (rid, unickname,))
            connection.commit()

            sql_query_2 = "UPDATE skdevsec_product SET preview = (SELECT COUNT(*) FROM skdevsec_review WHERE pid=%s), " \
                          "preview_avg =(SELECT round(avg(rstar),1) FROM skdevsec_review WHERE pid=%s)  WHERE pid=%s "

            try:
                cursor.execute(sql_query_2, (pid, pid, pid,))

            except:
                try:
                    sql_query_3 = "UPDATE skdevsec_product SET preview = 0, preview_avg =0 WHERE pid=%s"
                    cursor.execute(sql_query_3, (pid, ))

                except Exception as e:
                    connection.rollback()
                    print(f"에러: {e}")
                    return Response(0)

            connection.commit()
            connection.close()

        except Exception as e:
            connection.rollback()
            print(f"에러: {e}")
            return Response(0)

        else:
            return Response(1)

    # 리뷰 검증
    @action(detail=False, methods=['POST'])
    def review_certified(self, request):
        try:
            pname_list = list()

            cursor = connection.cursor()
            cursor_oid = connection.cursor()

            unickname = request.data['unickname']
            pname = request.data['pname']

            sql_query_1 = "SELECT * FROM skdevsec_user WHERE unickname=%s"
            cursor.execute(sql_query_1, (unickname,))
            uid = cursor.fetchone()

            if uid is not None:
                sql_query_2 = "SELECT * FROM skdevsec_orderuser WHERE uid=%s"
                cursor_oid.execute(sql_query_2, (uid[0],))
                oid = cursor_oid.fetchone()
            else:
                return Response(1)

            if oid is not None:
                while oid:
                    sql_query_3 = "SELECT * FROM skdevsec_orderproduct WHERE oid=%s"
                    cursor.execute(sql_query_3, (int(oid[0]),))
                    _pname = cursor.fetchone()

                    pname_list.append(_pname[2])
                    oid = cursor_oid.fetchone()

                pname_count = {}

                for i in pname_list:
                    try:
                        pname_count[i] += 1
                    except:
                        pname_count[i] = 1

                if pname in pname_list:
                    sql_query_4 = "SELECT * FROM skdevsec_product WHERE pname=%s"
                    cursor.execute(sql_query_4, (pname,))
                    pid = cursor.fetchone()

                    sql_query_5 = "SELECT COUNT(*) FROM skdevsec_review WHERE pid=%s AND unickname=%s"
                    cursor.execute(sql_query_5, (int(pid[0]), unickname,))
                    review = cursor.fetchone()
                else:
                    return Response(1)

                connection.close()

            else:
                return Response(1)

        except Exception as e:
            connection.rollback()
            print(f"에러: {e}")
            return Response(0)

        else:
            if pname_count[pname] <= int(review[0]):
                return Response(1)
            else:
                return Response(0)
