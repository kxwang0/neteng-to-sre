from netmiko import ConnectHandler
from getpass import getpass

# CE12800 是 VRP8：改配置后提示符变成 [~hostname]，必须 commit 才生效。
# device_type="huawei" 会在 send_config_set 末尾 return 并死等 '>'，于是 ReadTimeout。
conn = ConnectHandler(
    device_type="huawei_vrpv8",
    host="192.168.30.252",
    username="admin1",
    password=getpass("输入设备密码: "),
)

# 下发一个无害的 Loopback 练手（vrpv8 默认不自动退出 system-view）
cmds = [
    "interface LoopBack 100",
    "description configured-by-python",
    "ip address 10.255.0.1 255.255.255.255",
]
print(conn.send_config_set(cmds))
print(conn.commit())          # 提交候选配置，再回到用户视图

# 验证
print(conn.send_command("display interface LoopBack 100"))
conn.disconnect()
