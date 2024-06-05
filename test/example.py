from router_movistar.client import Client

if __name__ == '__main__':
    password = 'ewrSz8EJ'  # My router password
    c = Client(password)
    info = c.get_router_info()
    print(info.model_dump_json(indent=2))
    c.reboot()
