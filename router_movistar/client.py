import random
import subprocess
from datetime import datetime
from urllib.parse import quote

import requests

from router_movistar import endpoints, endpoints_v2

from router_movistar.extractor import RouterInfoExtractor
from router_movistar.model import RouterInfo

DEBUG = False

class Client:
    session_id: str
    router_url: str
    cookie: str
    endpoints_set: any

    def __init__(self, password: str, username='user'):
        self.password = password
        self.username = username
        self.session_id = random.randint(10000000, 999999999)
        self.endpoints_set = endpoints
        self.router_url = self.endpoints_set.DEFAULT_ROUTER_IP

    def login(self) -> None:
        url = f"{self.router_url}{self.endpoints_set.LOGIN_ENDPOINT}"

        payload = f"loginUsername={self.username}&loginPassword={self.password}"
        headers = {
            'Cache-Control': 'max-age=0',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Cookie': 'sessionID=801077585; sessionID=739333578'
        }

        response = requests.request("POST", url, headers=headers, data=payload)
        cookie = response.headers['Set-Cookie']
        self.session_id = int(cookie.split(';')[0].split('=')[1])
        self.cookie = self.session_id

    def get_router_info(self) -> RouterInfo:
        self.login()
        extractor = RouterInfoExtractor(self.router_url, self.cookie, self.endpoints_set)
        return extractor.get_router_info()

    def reboot(self):
        self.login()
        epoch_ms = int((datetime.now().timestamp() + 1) * 1000)
        # It must be done through the console, because if it is done
        # using "request", as the router closes the connection,
        # then it fails, does not confirm and therefore does not restart
        curl_command = f"""curl --location '{self.router_url}/askey_reboot_secret.html?sessionKey={self.session_id}&_={epoch_ms}' \
        --header 'X-Requested-With: XMLHttpRequest' \
        --header 'Cookie: sessionID={self.session_id}'"""

        process = subprocess.Popen(curl_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        process.communicate()


class Client_V2(Client):
    def __init__(self, password: str, username='user', **kwargs):
        super().__init__(password, username, **kwargs)
        self.endpoints_set = endpoints_v2
        self.router_url = self.endpoints_set.DEFAULT_ROUTER_IP

    @staticmethod
    def mess_userpass(payload: str) -> str:
        # str.split('').map(function(c){ return String.fromCharCode(c.charCodeAt(0) ^ 0x1f); }).join('');
        updated_chars = []

        for single_char in payload:
            updated_chars.append(chr(ord(single_char) ^ 31))

        return ''.join(updated_chars)


    def login(self) -> None:
        url = f"{self.router_url}{self.endpoints_set.BASE_ENDPOINT}"
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Connection': 'keep-alive'
        }
        response = requests.request("GET", url, headers=headers)

        if DEBUG:
            print(response)
            print(response.headers)

        set_cookie_value = response.headers['Set-Cookie']

        if DEBUG:
            print('Set-Cookie obtained:', set_cookie_value)

        set_cookie_map = {}

        for pair in set_cookie_value.split(';'):
            pair = pair.strip()
            if not pair:
                continue

            pair_split = pair.split('=')
            if len(pair_split) < 2:
                continue

            pair_key = pair_split[0]
            pair_value = pair_split[1]
            set_cookie_map[pair_key] = pair_value

        self.session_id = set_cookie_map['_httpdSessionId_']
        self.cookie = '_httpdSessionId_=' + self.session_id

        url = f"{self.router_url}{self.endpoints_set.LOGIN_ENDPOINT}"

        payload = f"loginUsername={quote(self.mess_userpass(self.username))}&loginPassword={quote(self.mess_userpass(self.password))}"

        if DEBUG:
            print('Payload: ', payload)

        headers = {
            'Cookie': self.cookie,
            'Content-Type': 'application/x-www-form-urlencoded',
            'Content-Length': str(len(payload))
        }

        if DEBUG:
            print('Request headers ', headers)

        response = requests.request("POST", url, headers=headers, data=payload)

        if DEBUG:
            print(response)
            print('Response headers ', response.headers)

