"""
supervisor安装命令配置和启动
"""
import os
from proxy_port.client import run_bash_cmd, is_cmd_success
from proxy_port.utils import upload_file, chmod_x_to_file
from proxy_port.bash_cmd import (
    SUPERVISORCTL_STATUS,
    SUPERVISOR_CONFIG,
    SUPERVISOR_TASK_CONFIG,
    SUPERVISOR_START
)


class SupervisorConfiger:
    """
    supervisor配置设置器
    功能是在目标主机上创建supervisor的配置信息，并启动supervisor
    """
    supervisor_upload_path = SUPERVISOR_CONFIG
    autossh_run_sh_file_upload_path = '/etc/supervisor/conf.d/run_autossh_by_super.sh'

    def __init__(self, conn):
        self.conn = conn
        self.file_dir = os.path.dirname(os.path.dirname(__file__))
        self.supervisor_conf_file = self.file_dir + "/config/supervisord.conf"
        self.autossh_run_sh_file = self.file_dir + "/config/run_autossh_by_super.sh"

    def _check_dir_exist(self, dir_name):
        res = self.conn.run(f"cd {dir_name}")
        if is_cmd_success(res):
            return True
        return False

    def _mkdir(self):
        mkdirs = ['/etc/supervisor', '/etc/supervisor/conf.d']
        for each in mkdirs:
            res = self.conn.sudo(
                f'mkdir {each}', password=self.conn.connect_kwargs['password'], warn=True)
            if not is_cmd_success(res):
                if not self._check_dir_exist(each):
                    raise RuntimeError(f"cmd: {each} faild")
        return True

    def _upload_config(self):
        """
        上传supervisor的配置文件和运行autossh的脚本文件。
        """
        if not upload_file(self.conn, self.supervisor_conf_file, self.supervisor_upload_path):
            raise RuntimeError("cannot upload supervisor config file")
        if not upload_file(self.conn, self.autossh_run_sh_file, self.autossh_run_sh_file_upload_path):
            raise RuntimeError("cannot upload run autossh config file")
        return True

    @run_bash_cmd
    def _start_spervisor(self):
        start_cmd = SUPERVISOR_START
        res = self.conn.sudo(
            start_cmd, password=self.conn.connect_kwargs['password'], warn=True)
        if res.exited != 0:
            raise RuntimeError(res.stderr)
        return res

    def supervisor_is_running(self):
        ps_cmd = "ps aux | grep supervisord"
        res = self.conn.run(ps_cmd)
        if is_cmd_success(res):
            return False
        if SUPERVISOR_START in res.stdout:
            return True
        if "/usr/bin/supervisord":
            raise RuntimeWarning("anythor supervisor is running")
        return False

    def _check_supervisor_status(self):
        supervisorctl_status_cmd = SUPERVISORCTL_STATUS
        res = self.conn.sudo(supervisorctl_status_cmd,
                             password=self.conn.connect_kwargs['password'], warn=True)
        if is_cmd_success(res):
            return True
        return False

    def _force_stop_existed_supervisor(self):
        """
        强制结束已经存在的supervisor
        kill_cmd = "ps aux | grep supervisor | awk '{print $2}' |xargs kill -9 " 无效sudo
        """
        get_pid_cmd = "ps aux | pgrep supervisor"
        kill_pid_cmd = "kill -9 "
        try:
            res = self.conn.run(get_pid_cmd)
            if is_cmd_success(res):
                res = self.conn.sudo(
                    kill_pid_cmd + res.stdout.strip(), password=self.conn.connect_kwargs['password'])
                return is_cmd_success(res)
            return True
        except Exception:
            return True

    def config_and_start(self, force=False):
        """
        参数：
            force: 是否强制安装和配置
        """
        if not self._mkdir():
            raise RuntimeError("cannot create folder")
        self._upload_config()
        chmod_x_to_file(self.conn, self.autossh_run_sh_file_upload_path)
        # 安装完supervisor后再执行kill
        if force:
            self._force_stop_existed_supervisor()
        self._start_spervisor()
        if not self._check_supervisor_status():
            raise RuntimeError("start supervisor faild")
        return True
