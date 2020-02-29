import unittest
from proxy_port.client import create_connect
from proxy_port.autossh import RAutosshCtl, AutosshInit
from proxy_port.common import general_autossh_cmd, AutosshConfiger
from proxy_port.test.server_info import server1_info, server2_info


class AutosshTest(unittest.TestCase):

    def setUp(self):
        self.conn = create_connect(**server1_info)

        self.service_port = server2_info['port']
        self.proxy_port = 3232
        self.proxy_host = server2_info['host']
        self.listing_port = 3230
        self.username = server2_info['user']
        self.password = server2_info['password']

    def test_init_autossh(self):
        autossh_initer = AutosshInit(self.conn)
        self.assertTrue(autossh_initer.init("ubuntu"))

    def test_start_autossh(self):
        autoss_ctl = RAutosshCtl(self.conn)
        autossh_configuer = AutosshConfiger(self.service_port,
                                            self.proxy_port,
                                            self.listing_port,
                                            self.proxy_host,
                                            self.username,
                                            self.password)

        self.assertTrue(autoss_ctl.start_autossh(
            autossh_configuer.general_autossh_command()))

    def test_stop_autossh(self):
        autoss_ctl = RAutosshCtl(self.conn)
        autossh_cmd = general_autossh_cmd(
            self.service_port, self.listing_port, self.proxy_port, self.proxy_host, self.username)
        self.assertTrue(autoss_ctl.stop_autossh(autossh_cmd))
