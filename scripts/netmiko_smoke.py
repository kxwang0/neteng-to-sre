from netmiko import ConnectHandler
from getpass import getpass

dev = {
    "device_type": "linux",
    "host": "127.0.0.1",
    "username": "kxwang",
    "password": getpass("输入ssh密码:"),   #运行时输入，不进仓库
}

conn = ConnectHandler(**dev)
output = conn.send_command("hostname && uptime")
print("===== 设备返回 =====")
print(output)
conn.disconnect()
