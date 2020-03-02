from django.db.models.signals import pre_delete
from django.dispatch import receiver
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import mixins
from rest_framework import generics
from interface.serializer.server import (
    ServiceSerializer,
    ServiceProxyListSerializer,
    ProxyServiceSerializer
)
from interface.models.server import Service, ProxyService, ProxyTask
from .proxy_ctl import ProxyServiceCtlView


def delete_deploy_proxy_by_service(service):
    # if isinstance(service, Service):

    proxy_services = service.proxy_list.all()
    for proxy_service in proxy_services:
        proxy_task = ProxyTask.objects.get(proxy_service=proxy_service)
        res = ProxyServiceCtlView.delete_deploy_proxy(proxy_service, proxy_task)
        print("#####asdfasdfasdfasdfasdf####")    
    # else:
    print("not asdfasdfasd")


@receiver(pre_delete, sender=Service)
def handle_delete_service(sender, instance, **kwargs):
    """
    当联结删除Service的时候，把已经部署的相关服务给卸载掉。
    """
    delete_deploy_proxy_by_service(instance)

class ServiceListView(mixins.ListModelMixin,
                      mixins.CreateModelMixin,
                      generics.GenericAPIView):

    queryset = Service.objects.all()
    serializer_class = ServiceSerializer

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class ServiceDetailView(mixins.RetrieveModelMixin,
                        mixins.UpdateModelMixin,
                        mixins.DestroyModelMixin,
                        generics.GenericAPIView):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


class ServiceProxyView(mixins.ListModelMixin,
                       mixins.CreateModelMixin,
                       generics.GenericAPIView):

    queryset = ProxyService.objects.all()
    serializer_class = ServiceSerializer

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)
