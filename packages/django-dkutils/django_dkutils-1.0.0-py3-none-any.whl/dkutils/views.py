from re import S
from tkinter import SW
from django.utils.decorators import method_decorator

from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets
from rest_framework.renderers import JSONRenderer
from waffle.models import Switch

from .serializers import SwitchSerializer


@method_decorator(name='retrieve', decorator=swagger_auto_schema(auto_schema=None))
@method_decorator(name='list', decorator=swagger_auto_schema(auto_schema=None))
@method_decorator(name='create', decorator=swagger_auto_schema(auto_schema=None))
@method_decorator(name='update', decorator=swagger_auto_schema(auto_schema=None))
@method_decorator(name='partial_update', decorator=swagger_auto_schema(auto_schema=None))
@method_decorator(name='destroy', decorator=swagger_auto_schema(auto_schema=None))
class SwitchViewSet(viewsets.ModelViewSet):
    queryset = Switch.objects.all()
    serializer_class = SwitchSerializer
    renderer_classes = [JSONRenderer]
