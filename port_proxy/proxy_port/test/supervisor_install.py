import unittest
import time
from proxy_port.supervisor.initialization import SupervisorConfiger
from proxy_port.client import create_connect, is_cmd_success
from proxy_port.utils import install_dependence_software


class SupervisorInstallAndConfigure(unittest.TestCase):

    def setUp(self):
        self.supervisor_configure = SupervisorConfiger(self.conn)

    def _install_supervisor(self):
        self.assertTrue(install_dependence_software(self.conn, 'ubuntu', True))

    def _config_supervisor(self):
        res = self.supervisor_configure._mkdir()
        self.assertTrue(res)

        res = self.supervisor_configure._upload_config()
        self.assertTrue(res)

        time.sleep(0.5)
        self.supervisor_configure._force_stop_existed_supervisor()
        res = self.supervisor_configure._start_spervisor()
        self.assertTrue(is_cmd_success(res))

        res = self.supervisor_configure._check_supervisor_status()
        self.assertTrue(res)

    def test_install_supervisor(self):
        self._install_supervisor()
        self._config_supervisor()

    # def test_check_supervisor(self):
    #     self.assertTrue(self.supervisor_configure._check_supervisor_status())
