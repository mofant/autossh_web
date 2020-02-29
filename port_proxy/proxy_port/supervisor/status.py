"""
supervisor 状态监控
"""
import re
from proxy_port.client import is_cmd_success
from proxy_port.bash_cmd import SUPERVISORCTL_STATUS


class SupervisorStatus:

    def __init__(self, conn):
        self.conn = conn
        self.task_info_key = ["name", "state",
                              "pid_", "pid", "uptime_", "uptime"]

    def _res_format(self, cmd_stdout):
        """
        把 test                             RUNNING   pid 8354, uptime 0:00:07\ntest2                            RUNNING   pid 8355, uptime 0:00:07\n'
        转换为：
            {
                "name": "task_name",
                "state": "RUNNING",
                "pid": "pid",
                "uptime": "12;”
            }
        """
        res_lines = cmd_stdout.split("\n")
        running_task = []

        for each in res_lines:
            running_task.append(
                dict(
                    zip(
                        self.task_info_key, re.split(r'[;,\s]\s*', each)
                    )
                )
            )
        for each in running_task:
            if 'pid_' not in each or "uptime_" not in each:
                del(each)
                continue
            each.pop("pid_")
            each.pop("uptime_")
        return running_task

    def get_all_task(self):
        """
        获取主机所有supervisor任务
        """
        check_cmd = SUPERVISORCTL_STATUS
        res = self.conn.sudo(
            check_cmd, password=self.conn.connect_kwargs['password'], warn=True)
        if not is_cmd_success(res):
            raise RuntimeError("execute status check faild")

        running_tasks = self._res_format(res.stdout)
        return running_tasks

    def get_task_state(self, task_name):
        """
        校验supervisor中是否存在某个任务
        """
        running_tasks = self.get_all_task()
        task_name_map_task_info = {
            task['name']: task for task in running_tasks}
        if task_name in task_name_map_task_info:
            return task_name_map_task_info[task_name]
