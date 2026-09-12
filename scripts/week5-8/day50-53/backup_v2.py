#!/usr/bin/env python3
import argparse
import difflib
import logging
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date
from getpass import getpass

import yaml
from netmiko import ConnectHandler
from netmiko.exceptions import NetmikoAuthenticationException, NetmikoTimeoutException


class Device:
    def __init__(self, host, username, password, device_type="huawei"):
        self.host = host
        self.username = username
        self.password = password
        self.device_type = device_type
        self.conn = None

    def connect(self):
        self.conn = ConnectHandler(
            device_type=self.device_type,
            host=self.host,
            username=self.username,
            password=self.password,
            timeout=15,
        )

    def get_config(self):
        return self.conn.send_command(
            "display current-configuration",
            read_timeout=180,   # 整份配置很慢，v1 就用了 180
        )

    def close(self):
        if self.conn:
            self.conn.disconnect()
            self.conn = None


def load_devices(path):
    with open(path) as f:
        devices = yaml.safe_load(f)
    if not devices:
        raise ValueError(f"设备清单为空: {path}")
    return devices


def backup_one(dev, password):
    d = Device(dev["host"], dev["username"], password, dev["device_type"])
    try:
        d.connect()
        return d.get_config()
    except NetmikoTimeoutException:
        logging.error("%s 连接超时：网络不通或设备没开 SSH", dev["name"])
    except NetmikoAuthenticationException:
        logging.error("%s 认证失败：用户名/密码或 aaa 配置问题", dev["name"])
    except Exception as e:
        logging.error("%s 未预期错误：%s", dev["name"], e)
    finally:
        d.close()
    return None


def save_with_diff(name, new_cfg, backup_dir="backups"):
    """与 latest 比对：无变化只记日志；有变化则归档日期版并更新 latest。"""
    os.makedirs(backup_dir, exist_ok=True)
    latest = os.path.join(backup_dir, f"{name}_latest.txt")

    old = ""
    if os.path.exists(latest):
        with open(latest) as f:
            old = f.read()

    if old == new_cfg:
        logging.info("%s 无变更", name)
        return False

    diff = difflib.unified_diff(
        old.splitlines(), new_cfg.splitlines(),
        fromfile="旧配置", tofile="新配置", lineterm="",
    )
    changes = [
        l for l in diff
        if l.startswith(("+", "-")) and not l.startswith(("+++", "---"))
    ]
    logging.info("%s 配置变更，差异 %d 行", name, len(changes))

    today = date.today().isoformat()
    dated = os.path.join(backup_dir, f"{name}_{today}.txt")
    with open(dated, "w") as f:
        f.write(new_cfg)
    with open(latest, "w") as f:
        f.write(new_cfg)
    return True


def main():
    parser = argparse.ArgumentParser(description="网络设备配置备份工具 v2")
    parser.add_argument("--config", default="devices.yaml", help="设备清单 YAML")
    parser.add_argument("--workers", type=int, default=5, help="并发线程数")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler("backup.log", encoding="utf-8"),
            logging.StreamHandler(),
        ],
    )

    password = getpass("设备统一密码: ")
    devices = load_devices(args.config)
    ok, failed, changed = [], [], []

    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = {pool.submit(backup_one, dev, password): dev for dev in devices}
        for fut in as_completed(futures):
            dev = futures[fut]
            name = dev["name"]
            cfg = fut.result()
            if cfg is None:
                failed.append(name)
                continue
            ok.append(name)
            if save_with_diff(name, cfg):
                changed.append(name)

    logging.info(
        "成功 %d 台，失败 %d 台，有变更 %d 台",
        len(ok), len(failed), len(changed),
    )


if __name__ == "__main__":
    main()