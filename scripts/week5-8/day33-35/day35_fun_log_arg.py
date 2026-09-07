"""Day 35 三合一：Day 30 函数 + Day 33 logging + Day 34 argparse。

数据流（只改入口，干活的两个函数几乎不动）：
    argparse 收参 → logging 初始化 → collect() → 巡检写 -o → log/trap 写 backup.log
"""
import argparse
import logging
from getpass import getpass
from netmiko import ConnectHandler


def collect(host, username, password, commands, device_type="huawei"):
    """连接设备，批量执行命令，返回 {命令: 输出} 字典。"""
    dev = {
        "device_type": device_type,
        "host": host,
        "username": username,
        "password": password,
    }
    result = {}
    logging.info("开始连接设备 %s", host)
    conn = ConnectHandler(**dev)
    logging.info("已连接 %s，开始执行 %d 条命令", host, len(commands))
    for cmd in commands:
        logging.info("执行: %s", cmd)
        # 日志缓冲可能很长，给足等待时间
        result[cmd] = conn.send_command(cmd, read_timeout=60)
    conn.disconnect()
    logging.info("采集完成，已断开 %s", host)
    return result


def save_report(data, filename):
    """把 {命令: 输出} 字典写入一个汇总文件。"""
    with open(filename, "w", encoding="utf-8") as f:
        for cmd, output in data.items():
            f.write(f"===== {cmd} =====\n{output}\n\n")
    logging.info("报告已写入 %s（共 %d 条命令）", filename, len(data))


if __name__ == "__main__":
    # ① argparse 收参：把 Day 30 里写死的 IP / 用户名 / 文件名换成命令行参数
    parser = argparse.ArgumentParser(description="网络设备批量采集工具")
    parser.add_argument("-H", "--host", required=True, help="设备 IP")
    parser.add_argument("-u", "--username", default="admin1", help="登录用户名")
    parser.add_argument("-o", "--output", default="采集汇总.txt", help="输出文件名")
    args = parser.parse_args()

    # ② logging 初始化：必须在第一次 logging.info 之前；密码仍用 getpass，不进命令行、不进日志
    # 脚本日记只打屏，不写 backup.log——那个文件留给设备 log/trap
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[logging.StreamHandler()],
    )

    inspect_cmds = ["display version", "display device", "display interface brief"]
    log_cmds = ["display logbuffer", "display trapbuffer"]
    password = getpass("输入设备密码: ")

    # ③ 一次 SSH 采齐，再按用途拆文件
    try:
        data = collect(args.host, args.username, password, inspect_cmds + log_cmds)
        save_report({cmd: data[cmd] for cmd in inspect_cmds}, args.output)
        save_report({cmd: data[cmd] for cmd in log_cmds}, "backup.log")
        logging.info(
            "全部完成：巡检 → %s ；设备 log/trap → backup.log",
            args.output,
        )
    except Exception as e:
        logging.error("采集失败: %s", e)
        raise
