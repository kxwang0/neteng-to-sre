from netmiko import ConnectHandler
from getpass import getpass

# 回退：删掉 Day 38 练手的 LoopBack 100，VRP8 同样必须 commit
conn = ConnectHandler(
    device_type="huawei_vrpv8",
    host="192.168.30.252",
    username="admin1",
    password=getpass("输入设备密码: "),
)

print(conn.send_config_set(["undo interface LoopBack 100"]))
print(conn.commit())

# 接口已删就不能再 display interface LoopBack 100（会 Wrong parameter）
# 改查列表：没有 LoopBack100 才算回退成功
output = conn.send_command("display ip interface brief")
print(output)
if "LoopBack100" in output.replace(" ", ""):
    print("回退未生效：LoopBack 100 仍在")
else:
    print("回退成功：LoopBack 100 已删除")
conn.disconnect()
