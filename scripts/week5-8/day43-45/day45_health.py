"""Day 45：健康检查小工具——用解析结果列出异常接口 / OSPF 邻居。

ntc 对 CE 的 display ip interface brief 没有可靠模板，所以用本目录手写模板
（和 Day 43/44 同一套路）。先 print 第一行看字段名，再按字段判断。
"""
import logging
from getpass import getpass
from pathlib import Path

from netmiko import ConnectHandler
from textfsm.parser import TextFSMError

HERE = Path(__file__).resolve().parent
IP_BRIEF = HERE / "huawei_ce_display_ip_interface_brief.textfsm"
IF_BRIEF = HERE / "huawei_ce_display_interface_brief.textfsm"
OSPF_PEER = HERE / "ospf_peer.template"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)


def parse_cmd(conn, cmd, template):
    """指定本地模板解析；失败则返回空列表，不让脚本中断。"""
    try:
        data = conn.send_command(cmd, use_textfsm=True, textfsm_template=str(template))
    except TextFSMError as e:
        logging.error("%s 解析失败: %s", cmd, e)
        return []
    if not isinstance(data, list):
        logging.error("%s 未得到表格（模板可能没对上），类型=%s", cmd, type(data).__name__)
        return []
    return data


def is_down(value):
    return "down" in str(value).lower()


dev = {
    "device_type": "huawei",
    "host": "192.168.30.252",
    "username": "admin1",
    "password": getpass("输入设备密码: "),
}

conn = ConnectHandler(**dev)

# --- 接口：优先 display ip interface brief（课上的命令）---
rows = parse_cmd(conn, "display ip interface brief", IP_BRIEF)
if not rows:
    logging.warning("ip interface brief 没解析出表，改用 display interface brief")
    rows = parse_cmd(conn, "display interface brief", IF_BRIEF)

if rows:
    logging.info("字段结构（第一行）: %s", rows[0])

bad_intf = []
for row in rows:
    phy = row.get("physical") or row.get("phy") or ""
    proto = row.get("protocol") or ""
    if is_down(phy) or is_down(proto):
        logging.warning("接口异常: %s", row)
        bad_intf.append(row)

# --- OSPF 邻居：非 Full 算异常（Day 43 的模板）---
peers = parse_cmd(conn, "display ospf peer brief", OSPF_PEER)
if peers:
    logging.info("OSPF 字段结构（第一行）: %s", peers[0])

bad_peer = []
for row in peers:
    state = str(row.get("state") or "")
    if not state.lower().startswith("full"):
        logging.warning("邻居异常: %s", row)
        bad_peer.append(row)

conn.disconnect()

logging.info(
    "检查完成：接口 %d 条 / 异常 %d ；OSPF 邻居 %d 条 / 异常 %d",
    len(rows),
    len(bad_intf),
    len(peers),
    len(bad_peer),
)
if not bad_intf and not bad_peer:
    logging.info("未发现异常")
