import textfsm
from netmiko import ConnectHandler
from getpass import getpass

# Day 25：Netmiko 采集 + TextFSM 结构化解析
# 目标：把 display interface brief 的纯文本，切成「一行一个接口」的表格
# 类比：awk -F 按列切；TextFSM 用正则告诉解析器每一列长什么样

# 1) 设备信息（密码运行时输入，不写进仓库）
dev = {
    "device_type": "huawei",          # 华为 VRP；H3C 改 "hp_comware"
    "host": "192.168.30.252",         # 换成你的设备 IP
    "username": "admin1",
    "password": getpass("输入设备密码: "),
}

# 2) 建立 SSH：整个脚本只连一次（和 Day 24 一样）
conn = ConnectHandler(**dev)

# 3) 采集原始文本：此时还是一整坨字符串，Python 分不清哪是接口、哪是状态
raw = conn.send_command("display interface brief")

# 4) TextFSM 模板：定义「抓哪些字段、一行怎么切」
#    Value 字段名 (正则)  —— 声明要提取的列
#    \S+  = 连续非空白（接口名 / up / down / 0% 都符合）
#    Start 是初始状态；行首匹配成功后 -> Record 记一行，再去匹配下一行
#    华为 display interface brief 实际列：Interface  PHY  Protocol  InUti  OutUti  ...
#    本模板只取前 4 列；第 4 列字段名写成了 IP，实际抓到的是 InUti（利用率）
#    r"""...""" 原始字符串：正则里的 \S 不会被 Python 当成非法转义（否则会 SyntaxWarning）
template = r"""Value INTF (\S+)
Value PHY (\S+)
Value PROTO (\S+)
Value IP (\S+)

Start
  ^${INTF}\s+${PHY}\s+${PROTO}\s+${IP} -> Record
"""

# 5) TextFSM 构造函数要的是文件对象，所以先把模板落到磁盘
with open("intf.template", "w") as f:
    f.write(template)

# 6) 用模板解析 raw → 二维列表：[[接口, PHY, 协议, 第4列], ...]
with open("intf.template") as t:
    table = textfsm.TextFSM(t).ParseText(raw)

# 7) 按列对齐打印（表头宽度要和数据对齐，否则一跑就歪）
print(f"{'接口':<15}{'物理':<8}{'协议':<8}IP")
for row in table:
    print(f"{row[0]:<15}{row[1]:<8}{row[2]:<8}{row[3]}")

# 8) 收尾：断开 SSH，释放设备侧会话
conn.disconnect()
