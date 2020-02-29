from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import mixins
from rest_framework import generics
from interface.serializer.proxy import (
    ProxyServiceSerializer
)
from interface.models.server import (
    Service,
    ProxyService,
    ProxyTask,
)
from proxy_port import AutosshState, AutosshCtl, create_connect
from utils import AESCrypt
from django.conf import settings
from proxy_port.common import general_autossh_cmd


class ProxyServiceCtlView(APIView):

    def _get_proxy_service(self, pk):
        proxy_service = ProxyService.objects.get(id=pk)
        if not proxy_service:
            raise Http404
        return proxy_service

    def _get_proxy_task(self, proxy_service):
        return ProxyTask.objects.get(proxy_service=proxy_service)

    @classmethod
    def get_proxy_connection(cls, server):
        password = AESCrypt(settings.AES_KEY).aesdecrypt(server.password)
        conn = create_connect(host=server.host, port=server.port,
                              user=server.username, password=password)
        return conn

    def _get_autossh_state(self, fabric_conn, proxy_task, proxy_server):
        """
        获取autossh 的state
        """
        autossh_state = AutosshState(fabric_conn)
        task_type = 'autossh' if not proxy_task.supervisor_task_name else "supervisor"
        if task_type == 'autossh':
            task_name = general_autossh_cmd(
                service_port=proxy_task.service_port,
                listing_port=proxy_task.listing_port,
                proxy_port=proxy_task.proxy_port,
                proxy_host=proxy_server.host,
                username=proxy_server.username
            )
        else:
            task_name = proxy_task.supervisor_task_name
        state = autossh_state.get_autossh_stete(task_name, task_type)
        return state

    def get(self, request, pk):
        """
        获取proxy service的运行状态
        通过目标服务器查询其端口或者supervisor返回的结果
        """
        proxy_sercice = self._get_proxy_service(pk)
        if proxy_sercice.state == "CREATED":
            return Response("该代理还没有部署")
        proxy_task = self._get_proxy_task(proxy_sercice)
        if not proxy_task:
            return Response("该代理没有部署成功，请重新部署")

        service_server = proxy_sercice.service.dep_server
        fabric_conn = self.get_proxy_connection(service_server)
        state = self._get_autossh_state(
            fabric_conn, proxy_task, proxy_task.proxy_server)
        return Response(state)

    def post(self, request, pk):
        """
        启动proxy service
        设置了supervisor的使用
        """
        proxy_sercice = self._get_proxy_service(pk)
        if proxy_sercice.state == "CREATED":
            return Response("该代理还没有部署")

        proxy_task = self._get_proxy_task(proxy_sercice)
        if not proxy_task:
            return Response("该代理没有部署成功，请重新部署")

        service_server = proxy_sercice.service.dep_server
        fabric_conn = self.get_proxy_connection(service_server)
        ctl = AutosshCtl(fabric_conn)
        try:
            proxy_server = proxy_task.proxy_server
            password = AESCrypt(settings.AES_KEY).aesdecrypt(
                proxy_server.password)
            res = ctl.start_autossh(
                supervisor_task_name=proxy_task.supervisor_task_name,
                create=True,
                service_port=proxy_task.service_port,
                listing_port=proxy_task.listing_port,
                proxy_port=proxy_task.proxy_port,
                proxy_host=proxy_server.host,
                username=proxy_server.username,
                password=password)
            if res:
                state = self._get_autossh_state(
                    fabric_conn, proxy_task, proxy_server)
                return Response(state)
        except ValueError as e:
            return Response("任务没有创建")

    def put(self, request, pk):
        """
        停止服务
        分为super和autossh
        """
        proxy_sercice = self._get_proxy_service(pk)
        if proxy_sercice.state == "CREATED":
            return Response("该代理还没有部署")

        proxy_task = self._get_proxy_task(proxy_sercice)
        if not proxy_task:
            return Response("该代理没有部署成功，请重新部署")

        service_server = proxy_sercice.service.dep_server
        fabric_conn = self.get_proxy_connection(service_server)
        proxy_server = proxy_task.proxy_server
        ctl = AutosshCtl(fabric_conn)
        res = ctl.stop_autossh(
            supervisor_task_name=proxy_task.supervisor_task_name,
            service_port=proxy_task.service_port,
            listing_port=proxy_task.listing_port,
            proxy_port=proxy_task.proxy_port,
            proxy_host=proxy_server.host,
            username=proxy_server.username)
        if res:
            state = self._get_autossh_state(
                fabric_conn, proxy_task, proxy_server)
            return Response(state)
        return Response("任务停止失败")

    def delete(self, request, pk):
        """
        删除服务 
        """
        proxy_sercice = self._get_proxy_service(pk)
        if proxy_sercice.state == "CREATED":
            return Response("该代理还没有部署")

        proxy_task = self._get_proxy_task(proxy_sercice)
        if not proxy_task:
            return Response("该代理没有部署成功，请重新部署")

        service_server = proxy_sercice.service.dep_server
        fabric_conn = self.get_proxy_connection(service_server)
        ctl = AutosshCtl(fabric_conn)
        if proxy_task.dep_type == "AUTOSSH":
            proxy_server = proxy_task.proxy_server
            res = ctl.delete_autossh(service_port=proxy_task.service_port,
                                     listing_port=proxy_task.listing_port,
                                     proxy_port=proxy_task.proxy_port,
                                     proxy_host=proxy_server.host,
                                     username=proxy_server.username)
        else:
            res = ctl.delete_autossh(
                supervisor_task_name=proxy_task.supervisor_task_name)
        if res:
            return Response({"msg": "删除部署成功"})
        return Response("删除部署失败")
