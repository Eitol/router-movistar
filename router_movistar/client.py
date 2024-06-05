import os
import random
import subprocess
from datetime import datetime

import requests

from router_movistar.endpoints import DEFAULT_ROUTER_IP, LOGIN_ENDPOINT
from router_movistar.extractor import RouterInfoExtractor
from router_movistar.model import RouterInfo


class Client:
    session_id: int
    router_url: str

    def __init__(self, password: str, username='user'):
        self.password = password
        self.username = username
        self.router_url = DEFAULT_ROUTER_IP
        self.session_id = random.randint(10000000, 999999999)

    def login(self) -> None:
        url = f"{self.router_url}{LOGIN_ENDPOINT}"

        payload = f"loginUsername={self.username}&loginPassword={self.password}"
        headers = {
            'Cache-Control': 'max-age=0',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Cookie': 'sessionID=801077585; sessionID=739333578'
        }

        response = requests.request("POST", url, headers=headers, data=payload)
        cookie = response.headers['Set-Cookie']
        self.session_id = int(cookie.split(';')[0].split('=')[1])

    def get_router_info(self) -> RouterInfo:
        self.login()
        extractor = RouterInfoExtractor(self.router_url, self.session_id)
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
