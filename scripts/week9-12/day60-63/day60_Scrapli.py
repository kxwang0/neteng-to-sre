from scrapli import Scrapli
from getpass import getpass

hosts = ["192.168.30.252", "192.168.30.253"]
password = getpass("设备统一密码: ")

cmds = [
    "display version",
    "display current-configuration",
    "display interface brief",
]

for ip in hosts:
    conn = Scrapli(
        host=ip,                      # 必须是 str，不能是 list
        auth_username="admin1",
        auth_password=password,
        auth_strict_key=False,
        platform="huawei_vrp",
    )
    try:
        conn.open()
        print(f"===== {ip} =====")
        # 多条命令：send_commands(列表)；单条才用 send_command("一条")
        resps = conn.send_commands(cmds, timeout_ops=180)
        for cmd, resp in zip(cmds, resps):
            print(f"--- {cmd} ---")
            print(resp.result)
            print()
    except Exception as e:
        print(f"{ip} 失败: {e}")      # 一台挂了继续下一台
    finally:
        conn.close()