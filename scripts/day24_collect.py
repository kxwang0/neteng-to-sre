from netmiko import ConnectHandler
from getpass import getpass

# Day 24：连一次设备，批量采集多条命令，写入同一个汇总文件
# 目标：display version / display device / display interface brief → R1_采集汇总.txt
# 相对 Day 23 的进步：命令放进列表循环发；文件只开一次；输出用标题隔开，方便事后查阅
# 铁律：SSH 会话比命令贵——能连一次就别连三次

# 1) 设备信息（密码运行时输入，不写进仓库）
dev = {
    "device_type": "huawei",          # 华为 VRP；H3C 改 "hp_comware"
    "host": "192.168.30.252",         # 换成你的设备 IP
    "username": "admin1",
    "password": getpass("输入设备密码: "),
}

# 2) 建立 SSH：整个脚本只连一次，后面三条命令都复用这条会话
conn = ConnectHandler(**dev)

# 3) 批量采集：命令清单 + 循环 send_command，结果写进同一个文件
#    "w" = 覆盖写（每次跑脚本都生成一份新的汇总，旧内容丢掉）
#    with 打开：写完自动关文件，中途报错也会关，不会泄漏句柄
commands = ["display version", "display device", "display interface brief"]
with open("R1_采集汇总.txt", "w") as f:            # 文件只开一次，循环在里面写
    for cmd in commands:
        output = conn.send_command(cmd)            # 一条命令一次往返，返回完整字符串
        f.write(f"===== {cmd} =====\n")            # 分隔标题，事后用 grep 也能按命令跳
        f.write(output + "\n\n")                   # 命令输出 + 空行，三条之间留缝
    print(f"完成，{len(commands)} 条命令已写入 R1_采集汇总.txt")

# 4) 收尾：断开 SSH，释放设备侧会话
conn.disconnect()
