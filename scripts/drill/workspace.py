# 任务写在终端里。从下一行开始敲，不要粘贴手册。
# 写好保存，回到终端按回车批改。

def collect(host, cmd, device_type='huawei'):
    """采集设备命令输出。"""
    return {cmd: "fake"}

data = collect("192.168.30.252","display version","huawei")
print(data)
