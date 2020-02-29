"""
autossh 或者是supervisor状态监控
"""
from .client import create_connect
from proxy_port.autossh import AutosshStatus, AutosshInit, RAutosshCtl
from proxy_port.supervisor.status import SupervisorStatus
from proxy_port.supervisor.control import SupervisorCtl
from proxy_port.common import AutosshConfiger, general_autossh_cmd


class AutosshState:

    def __init__(self, conn):
        self.conn = conn

    def get_autossh_stete(self, task_name, task_type="supervisor"):
        """
        获取autossh状态
        参数：
        task_name:
            1、如果是采用supervisor部署的，请使用supervisor中的task_name
            2、如果是直接autossh的，请传递autossh的命令，如下：
        task_type:
            说明task的类型，如autossh或者是supervisor
        """
        if task_type.lower() == "autossh":
            autossh_stater = AutosshStatus(self.conn)
            pid = autossh_stater.get_autossh_state(task_name)
            if pid:
                state = {"state": "RUNNING", "pid": pid}
            else:
                state = {"state": "STOPPED", "pid": pid}
        elif task_type.lower() == "supervisor":
            supervisor_stater = SupervisorStatus(self.conn)
            state = supervisor_stater.get_task_state(task_name)
        return state


class AutosshCtl:
    """
    autossh 管理控制类
    """

    def __init__(self, conn):
        self.conn = conn

    def _supervisor_start(self,
                          service_port=None,
                          listing_port=None,
                          proxy_port=None,
                          proxy_host=None,
                          username=None,
                          password=None,
                          supervisor_task_name=None,
                          create=False,):
        """
        利用supervisor启动
        """
        supervisor_stater = SupervisorStatus(self.conn)
        is_existed = supervisor_stater.get_task_state(supervisor_task_name)

        super_ctl = SupervisorCtl(self.conn)
        if is_existed and is_existed['state'] == "RUNNING":
            return True
        elif is_existed and is_existed['state'] != "RUNNING":
            #kill and restart
            autossh_stater = AutosshStatus(self.conn)
            super_ctl.stop_task(supervisor_task_name, autossh_stater)
            return super_ctl.start_task(supervisor_task_name)
        elif not is_existed and create:
            configer = AutosshConfiger(
                service_port, proxy_port, listing_port, proxy_host, username, password)
            conf_content = configer.general_supservisor_config(
                supervisor_task_name)
            if super_ctl.deploy_ssh(conf_content, supervisor_task_name):
                return super_ctl.reload_task()
        raise ValueError("task is not created")

    def _autossh_start(self,
                       service_port=None,
                       listing_port=None,
                       proxy_port=None,
                       proxy_host=None,
                       username=None,
                       password=None,
                       supervisor_task_name=None,
                       create=False):
        autossh_cmd = general_autossh_cmd(service_port,
                                          listing_port,
                                          proxy_port,
                                          proxy_host,
                                          username)
        autossh_stater = AutosshStatus(self.conn)
        pid = autossh_stater.get_autossh_state(autossh_cmd)
        if pid:
            return True

        autossh_init = AutosshInit(self.conn)
        if not autossh_init.is_inited():
            raise ValueError("not init autossh env")

        autossh_configer = AutosshConfiger(
            service_port, proxy_port, listing_port, proxy_host, username, password)
        rautossh_ctl = RAutosshCtl(self.conn)
        return rautossh_ctl.start_autossh(autossh_configer.general_autossh_command())

    def start_autossh(self,
                      service_port=None,
                      listing_port=None,
                      proxy_port=None,
                      proxy_host=None,
                      username=None,
                      password=None,
                      supervisor_task_name=None,
                      create=False,
                      ):
        """
        启动autossh。
        启动方式分为利用supervisor和直接利用autossh
        1、supervisor启动，需要给定supervisor_task_name
        参数：
            service_port: 需要代理的端口
            listing_port: autossh 监听的端口
            proxy_port: 代理的端口
            proxy_host: 代理服务器ip
            username: 代理服务器的用户名
            password: 代理服务器的密码
            supervisor_task_name: 利用supervisor启动的supervisor taskname
            create: 如果任务不存在，是否创建（只针对supervisor）
        """
        if supervisor_task_name:
            return self._supervisor_start(service_port,
                                          listing_port,
                                          proxy_port,
                                          proxy_host,
                                          username,
                                          password,
                                          supervisor_task_name,
                                          create)
        else:
            return self._autossh_start(service_port,
                                       listing_port,
                                       proxy_port,
                                       proxy_host,
                                       username,
                                       password)

    def stop_autossh(self,
                     service_port=None,
                     listing_port=None,
                     proxy_port=None,
                     proxy_host=None,
                     username=None,
                     password=None,
                     supervisor_task_name=None,
                     create=False,):

        if supervisor_task_name:
            super_ctl = SupervisorCtl(self.conn)
            autossh_stater = AutosshStatus(self.conn)
            return super_ctl.stop_task(supervisor_task_name, autossh_stater)
        else:
            autossh_cmd_str = general_autossh_cmd(
                service_port, listing_port, proxy_port, proxy_host, username)
            rautossh_ctl = RAutosshCtl(self.conn)
            return rautossh_ctl.stop_autossh(autossh_cmd_str)

    def delete_autossh(self,
                       service_port=None,
                       listing_port=None,
                       proxy_port=None,
                       proxy_host=None,
                       username=None,
                       supervisor_task_name=None
                       ):
        if supervisor_task_name:
            super_ctl = SupervisorCtl(self.conn)
            autossh_stater = AutosshStatus(self.conn)
            super_ctl.stop_task(supervisor_task_name, autossh_stater)
            super_ctl.delete_task(supervisor_task_name)
            return True
        else:
            return self.stop_autossh(service_port,
                                     listing_port,
                                     proxy_port,
                                     proxy_host,
                                     username)
