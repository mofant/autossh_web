"""
本模块直接利用autossh命令执行
"""
import os
import re
from proxy_port.client import is_cmd_success
from proxy_port.utils import upload_file, install_dependence_software, kill_pid


class AutosshInit:
    """
    用户直接运行autossh的话，将把run_autossh_by_native.sh脚本上传到服务器
    上传到~/.autossh/run_autossh_by_native.sh

    """
    run_autossh_sh_file = os.path.dirname(
        __file__) + "/config/run_autossh_by_native.sh"

    def __init__(self, conn):
        self.conn = conn

    def _mkdir(self):
        """
        创建~/.autossh文件夹
        """
        res = self.conn.run("mkdir ~/.autossh", warn=True)
        if not is_cmd_success(res):
            if "File exists" in res.stderr:
                return True
            else:
                return False
        return True

    def _upload_run_sh_file(self):
        if upload_file(self.conn, self.run_autossh_sh_file, "~/.autossh/run_autossh_by_native.sh"):
            chmod_x_cmd = "chmod +x ~/.autossh/run_autossh_by_native.sh"
            res = self.conn.sudo(
                chmod_x_cmd, password=self.conn.connect_kwargs['password'], warn=True)
            return is_cmd_success(res)
        raise RuntimeError("cannot upload run_autossh_by_native.sh file")

    def _run_autossh_cmd(self, run_autossh_bash_cmd):
        self.conn.cd("~/.autossh")
        res = self.conn.run(run_autossh_bash_cmd)
        return is_cmd_success(res)

    def is_inited(self):
        """
        查询服务器是否初始化了autossh的环境。
        """
        try:
            check_cmd = "cat ~/.autossh/run_autossh_by_native.sh"
            res = self.conn.run(check_cmd)
            return is_cmd_success(res)
        except Exception:
            return False
        
    def init(self):
        """
        初始化服务器的autossh运行脚本，不包含安装软件服务
        """
        # install_dependence_software(self.conn, )
        self._mkdir()
        return self._upload_run_sh_file()


class RAutosshCtl:
    """
    autossh运行控制
    """

    def __init__(self, conn):
        self.conn = conn

    def start_autossh(self, run_autossh_bash_cmd):
        """
        参数：
            run_autossh_bash_cmd： 为AutosshConfiger的general_autossh_command
        """
        with self.conn.cd("~/.autossh"):
            res = self.conn.run(run_autossh_bash_cmd)
            return is_cmd_success(res)
        return False

    def stop_autossh(self, autossh_cmd_str):
        """
        参数：
            autossh_cmd_str 为直接autossh开头的运行命令
            autossh_stater: AutosshStatus instance
        """
        autossh_stater = AutosshStatus(self.conn)
        pid = autossh_stater.get_autossh_state(autossh_cmd_str)
        if pid:
            kill_pid(self.conn, pid)
        return True


class AutosshStatus:
    """
    获取autossh的运行状态
    autossh -M 5327 -NR 2227:127.0.0.1:22 le@ip
    """
    autossh_pid_pat = re.compile("\s(?:[0-9]+?\s)")

    def __init__(self, conn):
        self.conn = conn

    def _get_autossh_pid(self, ps_line):
        return re.findall(self.autossh_pid_pat, ps_line)[0].strip()

    def _format_stdout(self, res) -> dict:
        """
        返回 {pid: autossh_cmd} dict
        """
        autossh_str = res.stdout.split("\n")
        res_lines = {}
        for line in autossh_str:
            if "autossh -M" in line and 'expect -c' not in line:
                try:
                    """
                    centos: "/usr/lib/autossh/autossh -M 6144 -NR 2270:127.0.0.1:22 user@host"
                    ubuntu: "/usr/bin/autossh -M 6144 -NR 3457:127.0.0.1:22 user@host"
                    """
                    res_lines[self._get_autossh_pid(
                        line)] = "autossh -M" + line.split("autossh -M")[1]
                except IndexError:
                    print(line)
        return res_lines

    def get_autossh_programe(self):
        """
        返回pid->autossh -M 5327 -NR 2227:127.0.0.1:22 user@172.20.51.1 的dict
        """
        ps_cmd = "ps aux | grep autossh"
        res = self.conn.run(ps_cmd)
        if not is_cmd_success(res):
            raise RuntimeError("cannot ps autossh")
        return self._format_stdout(res)

    def get_autossh_state(self, autossh_cmd_str):
        autossh_programe = self.get_autossh_programe()
        for pid, autossh_cmd in autossh_programe.items():
            if autossh_cmd == autossh_cmd_str:
                return pid
        return None
