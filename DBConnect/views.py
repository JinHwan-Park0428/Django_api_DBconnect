from rest_framework import viewsets
from rest_framework import permissions
from DBConnect.models import Djangotest
from DBConnect.serializers import DjangotestSerializer
# from django.db import connection

from rest_framework.decorators import action
from rest_framework.response import Response


# Create your views here.
class DjangotestViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Djangotest.objects.all()
    serializer_class = DjangotestSerializer

    permission_classes = [permissions.IsAuthenticated]

    # /my_topic_MyProjectWeather/search?q=test5
    @action(detail=False, methods=['GET'])
    def search(self, request):
        q = request.query_params.get('q', None)

        qs = self.get_queryset().filter(userkey=q)
        serializer = self.get_serializer(qs, many=True)
        print(serializer.data)

        return Response(serializer.data)


