from getpass import getpass
from netmiko import ConnectHandler

class Device:
    def __init__(self, host, username, password, device_type="huawei"):
        self.host = host
        self.username = username
        self.password = password
        self.device_type = device_type
        self.conn = None          # 连接先占个位

    def connect(self):
        self.conn = ConnectHandler(
            device_type=self.device_type, host=self.host,
            username=self.username, password=self.password,
        )

    def run(self, cmd):
        return self.conn.send_command(cmd)

    def close(self):
        if self.conn:
            self.conn.disconnect()

r1 = Device("192.168.30.252", "admin1", getpass("输入设备密码: "))
r1.connect()
print(r1.run("display version"))
r1.close()