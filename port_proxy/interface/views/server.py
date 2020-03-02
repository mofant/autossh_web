from django.db.models.signals import pre_delete
from django.dispatch import receiver
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import mixins
from rest_framework import generics
from interface.serializer.server import ServerSerializer, ServerServiceListSerializer
from interface.models.server import Server
# Create your views here.
from .service import delete_deploy_proxy_by_service

@receiver(pre_delete, sender=Server)
def handle_delete_server(sender, instance, **kwargs):
    if isinstance(instance, Server):
        services = instance.service_list.all()
        for each_service in services:
            print("deleting server")
            delete_deploy_proxy_by_service(each_service)



class ServerListView(mixins.ListModelMixin,
                     mixins.CreateModelMixin,
                     generics.GenericAPIView):
    queryset = Server.objects.all()
    serializer_class = ServerSerializer

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class ServerDetailView(mixins.RetrieveModelMixin,
                       mixins.UpdateModelMixin,
                       mixins.DestroyModelMixin,
                       generics.GenericAPIView):
    queryset = Server.objects.all()
    serializer_class = ServerSerializer

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


class ServerServiceListView(mixins.ListModelMixin,
                            generics.GenericAPIView):

    queryset = Server.objects.all()
    serializer_class = ServerServiceListSerializer

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
