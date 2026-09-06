from netmiko import ConnectHandler
from getpass import getpass

# Day 23：用 Netmiko 第一次 SSH 上真实网络设备
# 目标：连上华为 CE12800，敲一条 display version，把回显打到终端
# 类比：你平时 ssh admin1@192.168.30.252，再手动敲命令；这里全程脚本代劳
# 排障口诀：先 ping 通 IP，再确认用户名密码，最后才查 device_type

# 1) 设备信息：Netmiko 用字典描述「连谁、用什么驱动」
#    device_type 决定提示符、分页（---- More ----）、命令风格
#    华为 VRP 用 "huawei"；H3C Comware 改 "hp_comware"；Cisco IOS 用 "cisco_ios"
dev = {
    "device_type": "huawei",          # 驱动名写错会连上但解析提示符失败
    "host": "192.168.30.252",         # 设备管理 IP；写错会 NetmikoTimeoutException
    "username": "admin1",             # SSH 用户名；和密码任一不对 → Authentication failed
    "password": getpass("输入设备密码: "),  # 运行时输入，不写进文件、不进 Git
}

# 2) 建立 SSH：ConnectHandler 打开 TCP/22、认证、等到设备提示符
#    **dev 是解包：等价于 ConnectHandler(device_type=..., host=..., ...)
#    这一步最容易报错：超时=IP/防火墙；认证失败=账号密码
conn = ConnectHandler(**dev)

# 3) 下发一条命令并打印回显（send_command 会自动处理分页，把完整输出收回来）
print(conn.send_command("display version"))

# 4) 收尾：断开 SSH，释放设备侧会话（不 disconnect 也能退出，但设备上会留僵尸会话）
conn.disconnect()
