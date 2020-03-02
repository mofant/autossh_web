from django.db import models
from django.utils.translation import gettext_lazy as _

# Create your models here.


class Server(models.Model):
    """
    服务器信息
    """
    class ServerType(models.TextChoices):
        DEPLOY = 'DEPLOY', _("部署服务器")
        PROXY = 'PROXY', _("对外开放服务器")

    class SystemType(models.TextChoices):
        UBUNTU = 'UBUNTU', _('ubuntu')
        CENTOS = 'CENTOS', _('centos')

    name = models.CharField("服务器名称", max_length=100, null=False)
    host = models.GenericIPAddressField("服务器IP地址", null=False)
    port = models.IntegerField("ssh端口", null=False)
    username = models.CharField("用户名", max_length=100, null=False)
    password = models.CharField("服务器密码，加密", max_length=200, null=False)
    server_type = models.CharField("服务器类型",
                                   max_length=10,
                                   choices=ServerType.choices,
                                   default=ServerType.DEPLOY
                                   )
    is_dep_supervisor = models.BooleanField("是否部署了supervisor", default=False)
    is_dep_autossh = models.BooleanField("是否部署了autossh脚本", default=False)
    is_install_dep = models.BooleanField("是否安装了以来软件", default=False)
    system_type = models.CharField("系统类型",
                                   max_length=10,
                                   choices=SystemType.choices,
                                   default=SystemType.UBUNTU
                                   )


class Service(models.Model):
    """
    部署服务
    """
    name = models.CharField("服务名称", max_length=200, null=False)
    port = models.IntegerField("服务端口", null=False)
    dep_server = models.ForeignKey(
        Server, on_delete=models.CASCADE, related_name="service_list")  # "部署服务器",


class ProxyService(models.Model):
    """
    开放的代理服务 
    """
    class ProxyState(models.TextChoices):
        DEPLOYED = 'DEPLOYED', _("已经部署")
        CREATED = 'CREATED', _("已创建")

    proxy_port = models.IntegerField("代理服务端口", null=False)
    proxy_server = models.ForeignKey(
        Server, on_delete=models.CASCADE)  # "代理服务器"
    service = models.ForeignKey(
        Service, on_delete=models.CASCADE, related_name='proxy_list')  # "关联服务",
    dep_supervisor = models.BooleanField("是否采用supervisor部署", default=False)
    open_port = models.BooleanField("是否对外开放端口", default=False)
    state = models.CharField("代理状态",
                             max_length=10,
                             choices=ProxyState.choices,
                             default=ProxyState.CREATED
                             )


class ProxyTask(models.Model):
    """
    运行的代理服务信息
    """
    class DepType(models.TextChoices):
        AUTOSSH = 'AUTOSSH', _("autossh")
        SUPERVISOR = 'SUPERVISOR', _("supervisor")

    supervisor_task_name = models.CharField(
        "supervisor task name", max_length=100, blank=True, null=True)
    service_port = models.IntegerField("service port", null=False)
    proxy_port = models.IntegerField("代理端口", null=False)
    listing_port = models.IntegerField("隧道监听端口", null=False)
    proxy_service = models.ForeignKey(
        ProxyService, on_delete=models.CASCADE, related_name='proxy_task')
    proxy_server = models.ForeignKey(
        Server, on_delete=models.CASCADE, related_name='proxy_task')
    dep_type = models.CharField("部署方式",
                                max_length=10,
                                choices=DepType.choices,
                                default=DepType.AUTOSSH
                                )
