"""Day 43：手写 TextFSM 进阶（Filldown + 跨行）。

Day 25：一行里抠完就 Record。
今天：
  1) Filldown —— 块首出现一次的字段，跟着后面每一行记录走
  2) 跨行     —— 字段分散在连续几行，凑齐最后一行才 Record

铁律：先 print 原始回显，再对着真实空格/标点写规则。
ntc-templates 是后面的课，今天不引入。
"""
import textfsm
from getpass import getpass
from netmiko import ConnectHandler


def parse(raw, template, filename):
    """模板写到磁盘（TextFSM 要文件对象），返回 (表头, 二维列表)。"""
    with open(filename, "w", encoding="utf-8") as f:
        f.write(template)
    with open(filename, encoding="utf-8") as t:
        fsm = textfsm.TextFSM(t)
        return fsm.header, fsm.ParseText(raw)


def show(title, header, rows):
    print(f"\n===== {title} 解析结果 {header} =====")
    if not rows:
        print("(空表：回显对不上规则，或设备上没有这类数据)")
        return
    for row in rows:
        print("  ".join(str(c) for c in row))


# CE 的 peer brief 是一张表：Area / 接口 / 邻居 / 状态都在同一行（所以 AREA 不用 Filldown）。
# Filldown 练的是块首只出现一次的「进程号、本机 Router ID」——Record 邻居时自动带上。
# TextFSM 用 ${VAR} 做替换，正则行尾不能写单个 $（会被当成残缺变量），行尾用 $$ 才是「结束」。
OSPF_TEMPLATE = r"""Value Filldown PROCESS (\d+)
Value Filldown LOCAL_RID (\d+\.\d+\.\d+\.\d+)
Value AREA (\d+\.\d+\.\d+\.\d+)
Value INTF (\S+)
Value NEIGHBOR (\d+\.\d+\.\d+\.\d+)
Value STATE (\S+)

Start
  ^\s*OSPF Process ${PROCESS} with Router ID ${LOCAL_RID}
  ^\s*Area Id
  ^\s*${AREA}\s+${INTF}\s+${NEIGHBOR}\s+${STATE} -> Record
"""

# 跨行：接口名 / 物理 / 协议 / IP 不在同一行，第三段 Internet Address 才 Record。
# display ip interface brief 仍是一行一条，练不出跨行，所以用非 brief。
IP_INTF_TEMPLATE = r"""Value INTF (\S+)
Value PHY (\S+)
Value PROTO (\S+)
Value IP (\S+)

Start
  ^${INTF}\s+current state\s+:\s+${PHY}
  ^Line protocol current state\s+:\s+${PROTO}
  ^Internet Address is\s+${IP} -> Record
"""

dev = {
    "device_type": "huawei",
    "host": "192.168.30.252",
    "username": "admin1",
    "password": getpass("输入设备密码: "),
}

conn = ConnectHandler(**dev)

print("===== 1) Filldown：display ospf peer brief =====")
ospf_raw = conn.send_command("display ospf peer brief")
print(ospf_raw)
header, rows = parse(ospf_raw, OSPF_TEMPLATE, "ospf_peer.template")
show("OSPF 邻居", header, rows)

print("\n===== 2) 跨行：display ip interface =====")
ip_raw = conn.send_command("display ip interface")
print(ip_raw)
header, rows = parse(ip_raw, IP_INTF_TEMPLATE, "ip_intf.template")
show("IP 接口", header, rows)

conn.disconnect()
