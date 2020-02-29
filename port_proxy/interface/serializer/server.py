from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
from django.conf import settings
from interface.models.server import Server, Service, ProxyService
from utils import AESCrypt


class PasswordField(serializers.Field):
    """
    Color objects are serialized into 'rgb(#, #, #)' notation.
    Password object are serializerd into '******' notation
    """

    def to_representation(self, value):
        # return "rgb(%d, %d, %d)" % (value.red, value.green, value.blue)
        return "******"

    def to_internal_value(self, data):
        aes_crpyter = AESCrypt(settings.AES_KEY)
        return aes_crpyter.aesencrypt(data)


class ServerSerializer(ModelSerializer):

    password = PasswordField()

    class Meta:
        model = Server
        fields = '__all__'


class ServiceSerializer(ModelSerializer):

    # dep_server = ServerSerializer()
    #server_name = serializers.CharField(read_only=True)
    server_name = serializers.SerializerMethodField(read_only=True)

    def get_server_name(self, service):
        return service.dep_server.name

    class Meta:
        model = Service
        fields = "__all__"


class ProxyServiceSerializer(ModelSerializer):

    class Meta:
        model = ProxyService
        fields = "__all__"


class ServerServiceListSerializer(ModelSerializer):

    service_list = ServiceSerializer(many=True)

    class Meta:
        model = Server
        fields = ("id", "service_list", "name", "host", "port",
                  "username", "server_type")


class ProxyServiceSerializer(serializers.ModelSerializer):

    class Meta:
        model = ProxyService
        fields = '__all__'


class ServiceProxyListSerializer(serializers.ModelSerializer):

    proxy_list = ProxyServiceSerializer(many=True)

    class Meta:
        model = Service
        fields = '__all__'
