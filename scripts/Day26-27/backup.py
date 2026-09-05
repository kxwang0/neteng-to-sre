import json
import os
import difflib
from datetime import date
from getpass import getpass
from netmiko import ConnectHandler

# =============================================================================
# Day 26–27：配置备份脚本 v1（本月毕业作品）
#
# 人话版流水线（写代码前先能把这 6 步说出来，说不出来就别急着敲）：
#   1. 从 devices.json 读出设备清单（字典的列表）
#   2. 密码运行时输入，不写进文件
#   3. for 循环逐台：SSH 登录 → 抓 display current-configuration → 断开
#   4. 和 backups/设备名_latest.txt 做 diff（没有这份文件 = 第一次，当空配置）
#   5. 同时写两份：设备名_日期.txt（归档）+ 设备名_latest.txt（下次对比用）
#   6. 某一台报错只记失败，继续下一台；最后打印成功/失败清单
#
# 对应旧课（卡住时回去重练那一天，不要整份死抄）：
#   Day 18  字典的列表          devices[i]["ip"]
#   Day 19  with open 读写文件   写备份、读 latest
#   Day 20  json.load + try/except
#   Day 23  ConnectHandler + send_command + disconnect
#
# 用法：cd ~/practice/Day26-27 && python3.12 backup.py
# 加设备：只改 devices.json，脚本不用动
# =============================================================================

BACKUP_DIR = "backups"                 # 所有备份文件都扔这个目录
DEVICES_FILE = "devices.json"          # 设备清单路径（和脚本同目录）
CONFIG_CMD = "display current-configuration"
READ_TIMEOUT = 180                     # 抓整份配置可能很慢，默认 10 秒会超时


def load_devices(path):
    # Day 20：json.load 把 JSON 数组变成 Python 的 list[dict]
    # with 打开：读完自动关文件（Day 19）
    with open(path) as f:
        return json.load(f)


def fetch_config(dev, password):
    # Day 23：连一台、敲一条、断开。字典字段来自 devices.json，密码来自 getpass
    # timeout=15 是「建连」超时（IP 不通别死等）
    # read_timeout 是「等回显结束」超时（配置太长要给够）
    conn = ConnectHandler(
        device_type=dev["device_type"],
        host=dev["ip"],
        username=dev["username"],
        password=password,
        timeout=15,
    )
    try:
        return conn.send_command(CONFIG_CMD, read_timeout=READ_TIMEOUT)
    finally:
        # finally：成功、失败都会跑（Day 20）——避免设备上留僵尸 SSH
        conn.disconnect()


def previous_lines(latest_path):
    # 下次对比的基准是「上一份 latest」，不是带日期的归档
    # 第一次跑还没有 latest → 返回空列表，diff 会把整份配置算成新增
    if not os.path.exists(latest_path):
        return []
    with open(latest_path) as f:
        return f.read().splitlines()   # splitlines：按行切开，方便 difflib 一行行比


def save_backups(name, today, config):
    # 两份都写，职责不同：
    #   设备名_日期.txt     历史归档，今天覆盖今天、昨天的还在
    #   设备名_latest.txt   永远是「当前最新」，下次跑脚本拿它来 diff
    dated = os.path.join(BACKUP_DIR, f"{name}_{today}.txt")
    latest = os.path.join(BACKUP_DIR, f"{name}_latest.txt")
    with open(dated, "w") as f:        # "w" 覆盖写
        f.write(config)
    with open(latest, "w") as f:
        f.write(config)
    return latest


def change_line_count(old_lines, new_text):
    # difflib.unified_diff 产出的是「diff 文本行」，不是「改了几个配置命令」
    # 里面会带 --- / +++ / @@ 这种头；0 行 = 和上次完全一样
    # lineterm=""：不要再给每行补 \n，否则 len() 会虚高
    diff = difflib.unified_diff(
        old_lines,
        new_text.splitlines(),
        lineterm="",
    )
    return len(list(diff))             # unified_diff 是生成器，必须 list() 才能数行数


def backup_one(dev, password, today):
    # 单台完整流水线：读旧 latest → 采集 → 数 diff → 落盘 → 打印
    # 注意顺序：必须先读 latest，再覆盖写；写反了就永远「无变化」
    name = dev["name"]
    latest_path = os.path.join(BACKUP_DIR, f"{name}_latest.txt")
    old = previous_lines(latest_path)
    config = fetch_config(dev, password)
    n = change_line_count(old, config)
    save_backups(name, today, config)
    if n:
        print(f"[{name}] 备份完成，变更 {n} 行")
    else:
        print(f"[{name}] 无变化")
    return name


def main():
    os.makedirs(BACKUP_DIR, exist_ok=True)     # 目录不存在就建；已存在也不报错
    today = date.today().isoformat()           # 2026-09-05，拿来拼归档文件名
    password = getpass("设备统一密码: ")        # 运行时输入，不进 JSON、不进 Git

    devices = load_devices(DEVICES_FILE)
    ok, failed = [], []                       # 两个清单，最后汇总（需求第 5 条）

    for dev in devices:                        # Day 18：遍历字典的列表
        name = dev.get("name", "?")            # .get：键缺失时不炸，方便失败日志
        try:
            ok.append(backup_one(dev, password, today))
        except Exception as e:
            # 单台失败只记账，循环继续 —— 这就是「不中断」
            print(f"[{name}] 失败：{e}")
            failed.append(name)

    print(f"\n成功 {len(ok)} 台：{ok}")
    print(f"失败 {len(failed)} 台：{failed}")


if __name__ == "__main__":
    # 直接 python3.12 backup.py 时才跑 main；被别人 import 时不自动备份
    main()
