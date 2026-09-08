"""Day 44：ntc-templates——用社区现成模板，不再手写。

用法就一个参数：send_command(..., use_textfsm=True)
  命中模板 → 返回字典列表
  没命中 → 返回原始字符串

注意两件事（课程示例路径在这台机器上对不上）：
  1) 模板目录用 ntc_templates 包自己的路径，不要写死 /usr/local/...
  2) index 里华为平台叫 huawei_vrp；device_type='huawei' 会找不到模板
"""
import os
from getpass import getpass
from pathlib import Path

import ntc_templates
from netmiko import ConnectHandler
from textfsm.parser import TextFSMError

# Netmiko 靠 NET_TEXTFSM 找 index；装在用户目录时必须指到 .../ntc_templates/templates
os.environ["NET_TEXTFSM"] = str(Path(ntc_templates.__path__[0]) / "templates")
print("NET_TEXTFSM =", os.environ["NET_TEXTFSM"])
print("长期生效可写入 ~/.bashrc：")
print(f'  export NET_TEXTFSM={os.environ["NET_TEXTFSM"]}')

dev = {
    "device_type": "huawei_vrp",  # 和 ntc index 的 platform 一致（仍走华为 SSH）
    "host": "192.168.30.252",
    "username": "admin1",
    "password": getpass("输入设备密码: "),
}

conn = ConnectHandler(**dev)
HERE = Path(__file__).resolve().parent
CE_TEMPLATE = HERE / "huawei_ce_display_interface_brief.textfsm"

# 社区模板末尾是 ^. -> Error：CE 多出来的图例行（如 (p): port alarm down）会直接炸
print("\n===== display interface brief  use_textfsm=True =====")
try:
    hit = conn.send_command("display interface brief", use_textfsm=True)
except TextFSMError as e:
    print("社区模板已命中，但解析失败：", e)
    print("原因：ntc 按园区交换机图例写死，CE12800 多了 (p)/(c) 等行。")
    print("回退：用本目录补过图例的模板再解析一次（这就是给社区提 PR 的素材）。")
    hit = conn.send_command(
        "display interface brief",
        use_textfsm=True,
        textfsm_template=str(CE_TEMPLATE),
    )

print("返回类型:", type(hit).__name__)
if isinstance(hit, list):
    print("结构化结果，共", len(hit), "行")
    for row in hit[:5]:
        print(row)
    if len(hit) > 5:
        print("...")
else:
    print("没命中，仍是原始字符串（前 300 字）：")
    print(hit[:300])

# index 里没有「display ospf peer brief」，但 huawei_vrp 的 dir 写成了 d[[ir]]
# 正则变成 d(ir)? ，会误匹配任何以 d 开头的命令（包括 display ...）
# 于是套上 dir 模板，第一行 OSPF Process ... 对不上就 State Error
print("\n===== display ospf peer brief  use_textfsm=True =====")
try:
    miss = conn.send_command("display ospf peer brief", use_textfsm=True)
except TextFSMError as e:
    print("误命中了别的模板（huawei_vrp_dir，index 写成 d[[ir]] 太宽）：", e)
    print("课程说「没命中返回字符串」在这里不成立，会直接抛错。改回不用 TextFSM：")
    miss = conn.send_command("display ospf peer brief")

print("返回类型:", type(miss).__name__)
if isinstance(miss, list):
    print(miss)
else:
    print("没有可用的 OSPF 邻居模板，原始回显如下（手写见 Day 43）。")
    print(miss[:400])

conn.disconnect()
