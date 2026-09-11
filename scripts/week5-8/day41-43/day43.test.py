"""Day 43 本地演示：Filldown 干什么。不连设备。"""
from io import StringIO

import textfsm

# 区域号只在块首出现一次，邻居行里没有 Area —— 这就是 Filldown 要解决的形状
raw = """
 Area: 0.0.0.0
 Router ID       Address         Interface     State
 192.168.30.253  10.0.10.253     Vlanif10      Full
 192.168.30.254  10.0.10.254     Vlanif10      2-Way

 Area: 0.0.0.1
 Router ID       Address         Interface     State
 2.2.2.2         10.0.20.2       GE1/0/0       Full
"""

# 唯一差别：AREA 前面有没有 Filldown
# Required：这一列必须有值才允许 Record，避免文件结束时把「只剩 Filldown」的空行存进去
tpl_fill = r"""Value Filldown AREA (\S+)
Value Required RID (\d+\.\d+\.\d+\.\d+)
Value ADDR (\d+\.\d+\.\d+\.\d+)
Value INTF (\S+)
Value STATE (\S+)

Start
  ^\s*Area:\s+${AREA}
  ^\s*Router ID
  ^\s*${RID}\s+${ADDR}\s+${INTF}\s+${STATE} -> Record
"""

tpl_plain = tpl_fill.replace("Value Filldown AREA", "Value AREA")


def run(title, tpl):
    fsm = textfsm.TextFSM(StringIO(tpl))
    rows = fsm.ParseText(raw)
    print(f"\n===== {title}  header={fsm.header} =====")
    for row in rows:
        print(row)


print("===== 原始回显 =====")
print(raw)
run("有 Filldown（AREA 会跟着每一行）", tpl_fill)
run("没有 Filldown（AREA 只在 Area 那一行里，Record 时已被丢掉）", tpl_plain)
