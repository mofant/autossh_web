import unittest
from proxy_port.client import create_connect
from proxy_port.main import AutosshCtl, AutosshState
from proxy_port.test.server_info import server1_info, server2_info


class SuperAutosshCtl(unittest.TestCase):

    def setUp(self):
        self.conn = create_connect(**server2_info)
        self.supervisor_task_name = "test_by_nothing"
        self.service_port = 22
        self.proxy_port = 3232
        self.proxy_host = server2_info['host']
        self.listing_port = 3230
        self.username = server2_info['user']
        self.password = server2_info['password']

    def test_start_autossh(self):
        ctl = AutosshCtl(self.conn)
        self.assertTrue(ctl.start_autossh(self.service_port,
                                          self.listing_port,
                                          self.proxy_port,
                                          self.proxy_host,
                                          self.username,
                                          self.password,
                                          self.supervisor_task_name,
                                          True)
                        )
        autossh_stater = AutosshState(self.conn)
        state = autossh_stater.get_autossh_stete(self.supervisor_task_name)
        self.assertIsNotNone(state)
        self.assertEqual(state['state'], 'STARTING')

    def test_stop_autossh(self):
        ctl = AutosshCtl(self.conn)
        self.assertTrue(ctl.stop_autossh(
            supervisor_task_name=self.supervisor_task_name))

    def test_delete_autossh(self):
        ctl = AutosshCtl(self.conn)
        self.assertTrue(ctl.delete_autossh(
            supervisor_task_name=self.supervisor_task_name))
