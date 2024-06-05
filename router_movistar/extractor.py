import json
import re
from typing import Dict, List

import requests

from router_movistar.endpoints import INFO_ENDPOINT, WIFI_5GHZ_ENDPOINT, WIFI_24GHZ_ENDPOINT
from router_movistar.model import RouterInfo, Device


class RouterInfoExtractor:

    def __init__(self, router_url: str, session_id: int):
        self.session_id = session_id
        self.router_url = router_url

    def get_router_info(self) -> RouterInfo:
        html_resp = self._get_page(INFO_ENDPOINT)
        basic_info = self._parse_router_info(html_resp)
        html_resp = self._get_page(WIFI_5GHZ_ENDPOINT)
        basic_info = self._set_5ghz_fields(basic_info, html_resp)
        html_resp = self._get_page(WIFI_24GHZ_ENDPOINT)
        basic_info = self._set_24ghz_fields(basic_info, html_resp)
        return basic_info

    def _get_page(self, endpoint: str) -> str:
        url = f"{self.router_url}{endpoint}"
        headers = {
            'Cookie': f'sessionID={self.session_id}'
        }
        response = requests.request("GET", url, headers=headers)
        return response.text

    def _set_5ghz_fields(self, basic_info, html_resp) -> RouterInfo:
        wifi_5ghz_info = self._parse_vars_info(html_resp)
        if 'wifiCurrentChannel' in wifi_5ghz_info:
            basic_info.wifi_5ghz_channel = int(wifi_5ghz_info['wifiCurrentChannel'])
        if 'wpaPskKey' in wifi_5ghz_info:
            basic_info.wifi_5ghz_password = wifi_5ghz_info['wpaPskKey']
        if 'wpa' in wifi_5ghz_info:
            basic_info.wifi_5ghz_encryption = wifi_5ghz_info['wpa']
        return basic_info

    def _set_24ghz_fields(self, basic_info: RouterInfo, html_resp: str) -> RouterInfo:
        wifi_24ghz_info = self._parse_vars_info(html_resp)
        if 'wpaPskKey' in wifi_24ghz_info:
            basic_info.wifi_24ghz_password = wifi_24ghz_info['wpaPskKey']
        if 'deviceData' in wifi_24ghz_info:
            json_array = json.loads(wifi_24ghz_info['deviceData'].replace("'", '"'))
            for device in json_array:
                basic_info.devices.append(
                    Device(
                        status=device[0] == '1',
                        device_name=device[1],
                        ip_address=device[3],
                        interface=device[4] if device[4] != '(null)' else None,
                        mac_address=device[6],
                    ))
        return basic_info

    @staticmethod
    def _parse_vars_info(html_resp: str) -> Dict[str, str]:
        lines = html_resp.split('\n')
        regexp = re.compile(r"\s*var (?P<key>\w+) ?= ?(((?P<value_array>\[.*]);)|(.*'(?P<value>.*)'\)?))")
        output = {}
        for i in range(len(lines)):
            match = regexp.match(lines[i])
            if match:
                key = match.group('key')
                value = match.group('value_array')
                if value is None:
                    value = match.group('value')
                output[key] = value
        return output

    def _parse_router_info(self, html_resp: str) -> RouterInfo:
        lines = html_resp.split('\n')
        start_line = 0
        for i in range(len(lines)):
            if lines[i].strip() == 'var info = [];':
                start_line = i
                break
        return self._extract_info(lines[start_line:])

    @staticmethod
    def _extract_info(lines: List[str]) -> RouterInfo:
        field_regex = re.compile(r"\s*info\[\s*(?P<key>\w+)] = .*'(?P<value>.*)'\)?;")
        router_info = RouterInfo()
        for line in lines:
            match = field_regex.match(line)
            if match:
                value = match.group('value')
                key: int = int(match.group('key'))
                if key == 0:  # 'Askey';
                    router_info.router_brand = value
                elif key == 1:  # 3505VW':
                    router_info.model = value
                elif key == 2:  # C8B42225692B':
                    router_info.serial_number = value
                elif key == 3:  # REV4_B6M':
                    router_info.hardware_version = value
                elif key == 4:  # CL_g000_R3505VWCL203_n48':
                    router_info.software_version = value
                elif key == 5:  # CL_g000_R3505VWCL203_n48':
                    router_info.firmware_version = value
                elif key == 6:  # Connected':
                    router_info.status = value
                elif key == 7:  # 186.106.21.123':
                    router_info.wan_ip = value
                elif key == 8:  # 192.168.1.1':
                    router_info.local_gateway_ip = value
                elif key == 9:  # 255.255.255.0':
                    router_info.subnet_mask = value
                elif key == 13:  # '1':
                    if value == '1':
                        router_info.wifi_24ghz_status = 'Enabled'
                    else:
                        router_info.wifi_24ghz_status = 'Disabled'
                elif key == 14:  # 'familia_abreu':
                    router_info.ssid_24ghz = value
                elif key == 10:  # '0':
                    router_info.hide_ssid_24ghz = True if value == '1' else False
                elif key == 16:  # 'psk2':
                    router_info.auth_method_24ghz = value
                elif key == 17:  # 'aes':
                    router_info.encryption_24ghz = value
                elif key == 18:  # '1':
                    if value == '1':
                        router_info.wifi_5ghz_status = 'Enabled'
                    else:
                        router_info.wifi_5ghz_status = 'Disabled'
                elif key == 19:  # 'familia_abreu_5Ghz':
                    router_info.ssid_5ghz = value
                elif key == 20:  # 'familia_abreu_5Ghz':
                    router_info.hide_ssid_5ghz = True if value == '1' else False
                elif key == 21:  # 'psk2':
                    router_info.auth_method_5ghz = value
                elif key == 22:  # 'aes':
                    router_info.encryption_5ghz = value
                elif key == 24:  # '1':
                    if value == '0':
                        router_info.iptv_addressing_type = 'DHCP'
                    elif value == '1':
                        router_info.iptv_addressing_type = 'STATIC'
                    elif value == '2':
                        router_info.iptv_addressing_type = 'NONE'
                elif key == 25:  # '10.76.185.79':
                    router_info.iptv_service_ip = value
                elif key == 26:  # '':
                    router_info.iptv_service = value
                elif key == 29:  # '':
                    router_info.id_ont = value

        tmpan = ''
        tmpss = ''
        tmple = ''
        regex = re.compile(r"\s+\w+ = ' ([a-z_\d]+ = )\"(?P<value>.*)\";'.*")
        for line in lines:
            if tmpan == '' and "tmpan =" in line:
                match = regex.match(line)
                if match:
                    tmpan = match.group('value')
            if tmpss == '' and 'tmpss = ' in line:
                match = regex.match(line)
                if match:
                    tmpss = match.group('value')
            if tmple == '' and 'tmple = ' in line:
                # tmple = ' le0_0 = "1";'.match(/"([^"]+)"/);
                match = regex.match(line)
                if match:
                    tmple = match.group('value')
        router_info.voip_an = tmpan
        router_info.voip_ss = tmpss
        router_info.voip_le = tmple
        return router_info
