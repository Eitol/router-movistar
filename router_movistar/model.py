from typing import List, Optional

from pydantic import BaseModel


class Device(BaseModel):
    status: bool = ''
    device_name: str = ''
    ip_address: str = ''
    interface: Optional[str] = None
    mac_address: str = ''


class RouterInfo(BaseModel):
    devices: List[Device] = []
    router_brand: str = ''
    model: str = ''
    serial_number: str = ''
    hardware_version: str = ''
    software_version: str = ''
    firmware_version: str = ''
    status: str = ''
    wan_ip: str = ''
    local_gateway_ip: str = ''
    subnet_mask: str = ''
    dns1: str = ''
    dns2: str = ''
    wifi_24ghz_status: str = ''
    ssid_24ghz: str = ''
    hide_ssid_24ghz: bool = False
    wifi_24ghz_password: str = ''
    wifi_24ghz_encryption: str = ''
    auth_method_24ghz: str = ''
    encryption_24ghz: str = ''
    wifi_5ghz_status: str = ''
    ssid_5ghz: str = ''
    wifi_5ghz_password: str = ''
    wifi_5ghz_encryption: str = ''
    wifi_5ghz_channel: int = 0
    hide_ssid_5ghz: bool = False
    auth_method_5ghz: str = ''
    encryption_5ghz: str = ''
    iptv_service: str = ''
    iptv_service_ip: str = ''
    iptv_addressing_type: str = ''
    voip_terminal: str = ''
    voip_status: str = ''
    voip_an: str = ''
    voip_ss: str = ''
    voip_le: str = ''
    ont_id: str = ''
