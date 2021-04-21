from rest_framework import generics
from rest_framework import mixins
from .models import djangotest
from .serializers import djangotestSerializer


class djangotestListAPI(generics.GenericAPIView, mixins.ListModelMixin):
    serializer_class = djangotestSerializer

    def get_queryset(self):
        return djangotest.objects.all().order_by('id')

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class djangotestDetailAPI(generics.GenericAPIView, mixins.RetrieveModelMixin):
    serializer_class = djangotestSerializer

    def get_queryset(self):
        return djangotest.objects.all().order_by('id')

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)