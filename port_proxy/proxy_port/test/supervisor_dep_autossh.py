import unittest
import uuid
from proxy_port.client import create_connect
from proxy_port.utils import chmod_x_to_file, kill_pid
from proxy_port.supervisor.control import SupervisorCtl
from proxy_port.autossh import AutosshStatus
from proxy_port.common import AutosshConfiger
from proxy_port.test.server_info import server2_info, server1_info


class SupervisorDepAutossh(unittest.TestCase):

    def setUp(self):
        self.conn = create_connect(**server1_info)

        self.ctl = SupervisorCtl(self.conn)

    def test_dep_autossh_conf(self):
        autossh_configure = AutosshConfiger(
            service_port=22,
            proxy_port=3232,
            listing_port=3230,
            proxy_host=server2_info['host'],
            username=server2_info['user'],
            password=server2_info['password']
        )
        task_name = "test_" + str(uuid.uuid1())[:6]
        conf_content = autossh_configure.general_supservisor_config(task_name)
        # print(conf_content)
        self.assertTrue(self.ctl.deploy_ssh(conf_content, task_name))

    def test_reload(self):
        chmod_x_to_file(
            self.conn, "/etc/supervisor/conf.d/run_autossh_by_super.sh")
        self.ctl.reload_task()

    def test_stop_task(self):
        autossh_stater = AutosshStatus(self.conn)
        self.assertTrue(self.ctl.stop_task("test_230b4c", autossh_stater))

    def test_start_task(self):
        self.assertTrue(self.ctl.start_task("test_230b4c"))

    def test_destory_task(self):
        self.test_stop_task()
        self.ctl.delete_task("test_230b4c")
