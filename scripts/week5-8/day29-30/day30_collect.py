from netmiko import ConnectHandler
from getpass import getpass

def collect(host, username, password, commands, device_type="huawei"):
    """连接设备，批量执行命令，返回 {命令: 输出} 字典。"""
    dev = {
        "device_type": device_type,
        "host": host,
        "username": username,
        "password": password,
    }
    result = {}
    conn = ConnectHandler(**dev)
    for cmd in commands:
        result[cmd] = conn.send_command(cmd)
    conn.disconnect()
    return result

def save_report(data, filename):
    """把 {命令: 输出} 字典写入一个汇总文件。"""
    with open(filename, "w") as f:
        for cmd, output in data.items():
            f.write(f"===== {cmd} =====\n{output}\n\n")

if __name__ == "__main__":
    cmds = ["display version", "display device", "display interface brief"]
    data = collect("192.168.30.252", "admin1", getpass("输入设备密码: "), cmds)
    save_report(data, "R1_采集汇总.txt")
    print("完成")