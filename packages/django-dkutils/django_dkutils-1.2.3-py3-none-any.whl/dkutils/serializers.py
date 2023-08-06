from rest_framework import serializers
from waffle.models import Switch


class SwitchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Switch
        fields = ('id', 'name', 'active', 'note', 'created', 'modified')
