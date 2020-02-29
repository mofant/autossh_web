from rest_framework import serializers
from interface.models.server import ProxyService


class ProxyServiceSerializer(serializers.ModelSerializer):

    server_name = serializers.SerializerMethodField(read_only=True)
    service_name = serializers.SerializerMethodField(read_only=True)

    def get_service_name(self, proxy):
        return proxy.service.name

    def get_server_name(self, proxy):
        return proxy.proxy_server.name

    class Meta:
        model = ProxyService
        fields = '__all__'
