import re
from netmiko import ConnectHandler
from getpass import getpass

# 思路：SSH 只连一次。先把两条命令的「生文本」都拿到手，再断开，最后用正则解析。
# 数据流：连设备 → 采集 output / ver → 断开 → 逐行抠接口 → 从 ver 抠版本号
conn = ConnectHandler(device_type="huawei", host="192.168.30.252",
                      username="admin1", password=getpass("输入设备密码: "))
output = conn.send_command("display interface brief")
ver = conn.send_command("display version")   # 还在同一条会话上，紧挨着发第二条
conn.disconnect()                            # 采集结束才断开；后面只用字符串，不再碰 conn

for line in output.splitlines():
    m = re.search(r"^(\S+)\s+(up|down)\s+(up|down)", line)
    if m and m.group(2) == "up":
        print(f"UP 的接口: {m.group(1)}")

# 原文: Version 8.180 (CE12800 V200R005C10SPC607B607)
# 三个括号 = 三个字段；原文里的 ( ) 要写成 \( \)
m = re.search(r"Version\s+([\d.]+)\s+\((\S+)\s+(\S+)\)", ver)
if m:
    print(f"软件号: {m.group(1)}")      # 8.180
    print(f"型号: {m.group(2)}")        # CE12800
    print(f"详细版本: {m.group(3)}")    # V200R005C10SPC607B607
else:
    print("未匹配，打印回显检查格式")
    print(ver)
