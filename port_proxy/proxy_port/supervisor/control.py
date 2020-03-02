"""
supervisor控制
"""
import os
import uuid
from proxy_port.client import is_cmd_success, run_bash_cmd
from .status import SupervisorStatus
from proxy_port.utils import kill_pid
# from utils import short_uuid
from proxy_port.bash_cmd import (
    SUPERVISORCTL_RELOAD,
    SUPERVISORCTL_START,
    SUPERVISORCTL_STOP,
    SUPERVISOR_TASK_CONFIG
)


class SupervisorCtl:

    config_file_path = SUPERVISOR_TASK_CONFIG

    def __init__(self, conn):
        self.conn = conn

    def reload_task(self):
        """
        reload配置文件。
        """
        reload_cmd = SUPERVISORCTL_RELOAD
        res = self.conn.sudo(
            reload_cmd, password=self.conn.connect_kwargs['password'], warn=True)
        if is_cmd_success(res):
            return True
        return False

    def deploy_ssh(self, config_content, task_name):
        """
        利用supervisor部署ssh服务
        1、确保run_autossh_by_super.sh在 '/etc/supervisor/conf.d/'目录中，
        2、生成一个supervisor的执行task
        """
        res = self.conn.run(
            f'echo "{config_content}" >> /tmp/{task_name}.conf')
        if not is_cmd_success(res):
            return False
        res = self.conn.sudo(
            f"mv /tmp/{task_name}.conf {self.config_file_path}{task_name}.conf", password=self.conn.connect_kwargs['password'])
        if is_cmd_success(res):
            return True
        return False

    def start_task(self, task_name):
        """
        启动task。
        部署完毕之后需要reload
        """
        start_cmd = SUPERVISORCTL_START + task_name
        res = self.conn.sudo(
            start_cmd, password=self.conn.connect_kwargs['password'], warn=True)
        if not is_cmd_success(res) and "already started" not in res.stderr:
            return False
        return True

    def stop_task(self, task_name, autossh_stater):
        """
        停止服务
        利用expect启动的话，supervisor关掉后，autossh进程还在
        参数：
            task_name: supervisor task_name
            autossh_stater: AutosshStatus instance
        """
        stop_cmd = SUPERVISORCTL_STOP + task_name
        res = self.conn.sudo(
            stop_cmd, password=self.conn.connect_kwargs['password'], warn=True)
        if not is_cmd_success(res) and "not running" not in res.stderr:
            return False
        cat_autossh_cmd = f"cat {self.config_file_path}{task_name}.conf | grep command"
        res = self.conn.run(cat_autossh_cmd, warn=True)
        if is_cmd_success(res):
            """
            autossh -M 5327 -NR 2227:127.0.0.1:22 user@172.20.51.1
            """
            infos = res.stdout.split("run_autossh_by_super.sh ")[
                1].strip().split(" ")
            autossh_cmd = f"autossh -M {infos[3]} -NR {infos[5]}:127.0.0.1:{infos[4]} {infos[1]}@{infos[0]}"
            pid = autossh_stater.get_autossh_state(autossh_cmd)
            if pid:
                kill_pid(self.conn, pid)
        return True

    def delete_task(self, task_name):
        """
        删除supervisor服务。
        必须先执行stop_task
        """
        del_cmd = f"rm -f {self.config_file_path}{task_name}.conf"
        res = self.conn.sudo(
            del_cmd, password=self.conn.connect_kwargs['password'], warn=True)
        if not is_cmd_success(res):
            raise RuntimeError("cannot del conf file")
        return self.reload_task()
