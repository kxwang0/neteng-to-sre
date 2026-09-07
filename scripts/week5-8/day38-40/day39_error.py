import logging
from getpass import getpass
from netmiko import ConnectHandler
from netmiko.exceptions import NetmikoTimeoutException, NetmikoAuthenticationException

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

# 测超时时只改 host；测认证失败时只改密码。一次只错一件，否则永远走不到认证。
dev = {
    "device_type": "huawei",
    "host": "192.168.30.252",
    "username": "admin1",
    "password": getpass("输入设备密码: "),
}

try:
    conn = ConnectHandler(**dev)
except NetmikoTimeoutException:
    logging.error("%s 连接超时：网络不通或设备没开 SSH", dev["host"])
except NetmikoAuthenticationException:
    logging.error("%s 认证失败：用户名/密码或 aaa 配置问题", dev["host"])
except Exception as e:
    logging.error("%s 未预期错误：%s", dev["host"], e)
else:
    logging.info("%s 连接成功", dev["host"])
    conn.disconnect()
