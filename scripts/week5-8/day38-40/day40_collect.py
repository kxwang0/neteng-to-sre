from concurrent.futures import ThreadPoolExecutor, as_completed
from getpass import getpass
from netmiko import ConnectHandler

def collect(dev):
    conn = ConnectHandler(**dev)
    output = conn.send_command("display version")
    conn.disconnect()
    return dev["host"], output

password = getpass("输入设备密码: ")
devices = [
    {"device_type": "huawei", "host": "192.168.30.252", "username": "admin1", "password": password},
    {"device_type": "huawei", "host": "192.168.30.253", "username": "admin1", "password": password},
]

with ThreadPoolExecutor(max_workers=5) as pool:
    futures = {pool.submit(collect, d): d for d in devices}
    for fut in as_completed(futures):
        host, output = fut.result()
        print(f"{host} 采集完成，{len(output)} 字节")