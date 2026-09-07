class Device:
    def __init__(self, host, device_type="huawei"):
        self.host = host
        self.device_type = device_type

    def show(self):
        print(f"{self.host} ({self.device_type})")

r1 = Device("192.168.x.11")
r2 = Device("192.168.x.12", "hp_comware")
r1.show()   # 各是各的数据，互不干扰
r2.show()