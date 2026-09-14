from getpass import getpass
from nornir import InitNornir
from nornir_netmiko.tasks import netmiko_send_command
from nornir_utils.plugins.functions import print_result

nr = InitNornir(config_file="day57_config.yaml")

# 密码不落盘：统一运行时注入（守住"密码不进仓库"的红线）
pw = getpass("设备统一密码: ")
for host in nr.inventory.hosts.values():
    host.password = pw

result = nr.run(task=netmiko_send_command, command_string="display version")
print_result(result)