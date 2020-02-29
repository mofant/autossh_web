from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework import mixins
from rest_framework import generics
from interface.serializer.proxy import (
    ProxyServiceSerializer
)
from interface.models.server import Service, ProxyService, ProxyTask
from proxy_port import AutosshCtl
from utils import short_uuid
from proxy_port.utils import install_dependence_software, is_port_using
from .proxy_ctl import ProxyServiceCtlView
from proxy_port.supervisor.initialization import SupervisorConfiger


class ProxyListView(mixins.ListModelMixin,
                    mixins.CreateModelMixin,
                    generics.GenericAPIView):

    queryset = ProxyService.objects.all()
    serializer_class = ProxyServiceSerializer

    def _create_proxy_task(self, proxy_service, supervisor_task_name, listing_port):
        proxy_task = ProxyTask(
            supervisor_task_name=supervisor_task_name,
            service_port=proxy_service.service.port,
            proxy_port=proxy_service.proxy_port,
            listing_port=listing_port,
            proxy_service=proxy_service,
            proxy_server=proxy_service.proxy_server,
            dep_type='AUTOSSH' if not proxy_service.dep_supervisor else 'SUPERVISOR'
        )
        proxy_task.save()
        return proxy_task

    def _config_supervisor(self, conn, force=True):
        supervisor_configer = SupervisorConfiger(conn)
        res = supervisor_configer.config_and_start(True)
        if res:
            return True
        return False

    def _install_dependense(self, conn, proxy_service, server):
        """
        安装依赖软件：autossh、supervisor、expect
        """
        need_save_server = False
        if not server.is_install_dep:
            # 如果服务器没有记录部署了软件，执行部署
            install_res = install_dependence_software(
                conn, server.system_type, proxy_service.dep_supervisor)
            if install_res:
                server.is_install_dep = True
                need_save_server = True
        if server.is_install_dep and not server.is_dep_supervisor and proxy_service.dep_supervisor:
            # 若果之前没有部署supervisor, 现在要求采用supervisor部署，那么将重新配置supervisor
            server.is_dep_supervisor = self._config_supervisor(conn, True)
            need_save_server = True
        if need_save_server:
            server.save()
        return True

    def _get_usable_port(self, conn, server):
        """
        获取可用的监听端口。
        """
        used_proxy_ports = ProxyTask.objects.filter(
            proxy_server=server).values('listing_port').distinct()
        use_port_set = set(range(6100, 6200))
        use_ports = use_port_set - set(used_proxy_ports)
        for port in use_ports:
            if not is_port_using(conn, port):
                return port
        raise RuntimeError("out of range use port")

    def _check_proxy_port_usable(self, conn, server, port):
        """
        校验代理端口是否可用
        """
        is_dep_proxy_port = ProxyTask.objects.filter(
            proxy_server=server, proxy_port=port).values("proxy_port").all()
        if is_dep_proxy_port:
            return True
        return is_port_using(conn, port)

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            proxy_service = serializer.save()

            service_server = proxy_service.service.dep_server
            conn = ProxyServiceCtlView.get_proxy_connection(service_server)

            proxy_server = proxy_service.proxy_server
            # 校验端口是否被占用
            if self._check_proxy_port_usable(conn, proxy_server, proxy_service.proxy_port):
                proxy_service.delete()
                return Response("代理端口被占用")
                #raise RuntimeError("proxy_port is using")

            if not self._install_dependense(conn, proxy_service, service_server):
                proxy_service.delete()
                return Response("安装依赖软件失败")

            # 生成supervisor_task_name
            supervisor_task_name = None
            if proxy_service.dep_supervisor:
                supervisor_task_name = "port_proxy_"+short_uuid()

            proxy_conn = ProxyServiceCtlView.get_proxy_connection(proxy_server)
            listing_port = self._get_usable_port(proxy_conn, proxy_server)
            proxy_task = self._create_proxy_task(
                proxy_service, supervisor_task_name, listing_port)

            headers = self.get_success_headers(serializer.data)
            proxy_service.state = "DEPLOYED"
            proxy_service.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

        except RuntimeError as e:
            proxy_service.delete()
            return Response(str(e))
        except Exception as e:
            # proxy_service.delete()
            raise


class ProxyDetailView(mixins.RetrieveModelMixin,
                      mixins.UpdateModelMixin,
                      mixins.DestroyModelMixin,
                      generics.GenericAPIView):
    queryset = ProxyService.objects.all()
    serializer_class = ProxyServiceSerializer

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)
