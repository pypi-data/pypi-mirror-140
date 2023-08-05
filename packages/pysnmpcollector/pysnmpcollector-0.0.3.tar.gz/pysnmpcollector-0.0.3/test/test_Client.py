import unittest
import logging
from pprint import pprint
from pysnmpcollector import Client

default_cfg = {'ID': None, 'Host': None, 'Port': 161, 'SystemOIDs': [''], 'Retries': 5,
               'Timeout': 20, 'Repeat': 0, 'Active': True, 'SnmpVersion': '2c', 'Community': None,
               'V3SecLevel': '', 'V3AuthUser': '', 'V3AuthPass': '', 'V3AuthProt': '', 'V3PrivPass': '',
               'V3PrivProt': '', 'V3ContextEngineID': '', 'V3ContextName': '', 'DisableBulk': False,
               'MaxRepetitions': 50, 'Freq': 60, 'UpdateFltFreq': 60, 'ConcurrentGather': True, 'OutDB': None,
               'LogLevel': 'error', 'LogFile': '', 'SnmpDebug': False, 'DeviceTagName': 'hostname',
               'DeviceTagValue': 'id', 'ExtraTags': [''], 'DeviceVars': None, 'Description': '',
               'MeasurementGroups': [], 'MeasFilters': None}


class TestClient(unittest.TestCase):
    def test_login(self):
        c = Client('http://django-dev.vestas.net:8090', 'adm1', 'adm1pass')
        try:
            cfg = c.get_device_config('dkhbo-dmvpn01')
            pprint(cfg)
        except:
            pass

        new_cfg = default_cfg
        new_cfg['ID'] = 'dkhbo-dmvpn01'
        new_cfg['Host'] = '10.12.17.239'
        new_cfg['Community'] = 'vestasnet'
        new_cfg['MeasurementGroups'].append('test-group')
        new_cfg['MeasurementGroups'].append('core_switch_ipsla')
        new_cfg['OutDB'] = 'django-dev'
        try:
            r = c.delete_device_config(new_cfg['ID'])
        except:
            pass
        r = c.create_device_config(new_cfg)
        del new_cfg['MeasurementGroups'][1]
        r = c.update_device_config(new_cfg['ID'], new_cfg)
        self.assertEqual(new_cfg, c.get_device_config(new_cfg['ID']))
        r = c.update_device_config(new_cfg['ID'], new_cfg, runtime=True)

    def test_get_devices(self):
        c = Client('http://django.vestas.net:8090', 'adm1', 'adm1pass')
        configs = {c['ID']: c for c in c.get_devices_config()}
        if 'esmadsh01' in configs:
            print(configs['esmadsh01'])
            #c.delete_device_config('esmadsh02', runtime=False)
        else:
            print("whaaat!")