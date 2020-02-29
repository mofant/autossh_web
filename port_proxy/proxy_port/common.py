import os


class AutosshConfiger:
    """
    生成一个配置文件类
    """
    config_file_path = os.path.dirname(__file__)
    supervisor_config_file = config_file_path + "/config/ssh_config_template.conf"
    autossh_config_file = config_file_path + "/config/ssh_config_template.conf"

    task_stdout_logfile = "/var/log/"
    run_supervisor_bash_path = '/etc/supervisor/conf.d/'

    def __init__(self,
                 service_port,
                 proxy_port,
                 listing_port,
                 proxy_host,
                 username,
                 password):

        self.service_port = service_port
        self.proxy_port = proxy_port
        self.listing_port = listing_port
        # self.super_task_name = super_task_name
        self.proxy_host = proxy_host
        self.username = username
        self.password = password

    def _general_autossh_command(self, user_super=True):
        """
        ./run_autossh_by_super.sh 172.20.51.30 le helehele 5327 22 2227
        """
        temp_cmd = f"{self.proxy_host} {self.username} {self.password} {self.listing_port} {self.service_port} {self.proxy_port}"
        if user_super:
            return f"/etc/supervisor/conf.d/run_autossh_by_super.sh {temp_cmd}"
        else:
            return f"./run_autossh_by_native.sh {temp_cmd}"

    def general_supservisor_config(self, super_task_name):
        with open(self.supervisor_config_file, 'r') as conf:
            content = conf.read()
            content = content.replace("$__task_name__", super_task_name)
            content = content.replace(
                "$__directory__", self.run_supervisor_bash_path)
            content = content.replace(
                "$__command__", self._general_autossh_command())
            content = content.replace(
                "$__logfile__", self.task_stdout_logfile + super_task_name)
            return content
        return None

    def general_autossh_command(self):
        """
        /run_autossh_by_native.sh
        """
        return self._general_autossh_command(user_super=False)


def general_autossh_cmd(service_port, listing_port, proxy_port, proxy_host, username):
    """
    生成bash的autossh启动命令
    """
    cmd = "autossh -M "
    cmd += f"{listing_port} -NR {proxy_port}:127.0.0.1:{service_port} "
    cmd += f"{username}@{proxy_host}"
    return cmd
