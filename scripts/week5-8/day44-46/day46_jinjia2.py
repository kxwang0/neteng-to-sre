from pathlib import Path
from getpass import getpass
from netmiko import ConnectHandler

# 1. 配置从哪来：读生成文件，不是再 render 一遍
config = Path("R1_生成配置.txt").read_text()
# 练手时建议改成只含 LoopBack 的那几行

# 2. 人眼看一眼 —— 生成和下发之间的闸门
print("===== 即将下发，请核对 =====")
print(config)
input("确认无误后按回车继续，不对就 Ctrl+C：")

cmds = [line for line in config.strip().splitlines() if line.strip()]
# strip().splitlines() 把文本变成命令列表；空行滤掉，避免发给设备

# 3. 密码现场问，不写进 .py
conn = ConnectHandler(
    device_type="huawei_vrpv8",   # 你这台 CE 必须用 vrpv8，huawei 会卡在 '>'
    host="192.168.30.252",
    username="admin1",
    password=getpass("输入设备密码: "),
)

# 4. 下发
print(conn.send_config_set(cmds))
print(conn.commit())              # VRP8：不 commit 只是候选配置，不生效

# 5. 验证：设备上真有这条，才算闭环
print(conn.send_command("display current-configuration | include LoopBack"))

# 6. 断开
conn.disconnect()