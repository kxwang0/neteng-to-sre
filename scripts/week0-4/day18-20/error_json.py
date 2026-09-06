# 设备清单 = 字典的列表(以后所有自动化下面都长这样)
devices = [
    {"name":"sw1","ip":"192.168.1.1","vendor":"huawei"},
    {"name":"sw2","ip":"192.168.1.2","vendor":"h3c"},
]
print(devices[0]["ip"])     #取第1台的IP
devices.append({"name":"sw3","ip":"192.168.1.3","vendor":"huawei"}) #追加
for dev in devices:         #遍历
    print(dev["name"],dev.get("ip"),dev["vendor"])    #.get()取值,键不存在时返回None而不是报错
len(devices)                #几台设

try:
    with open("/不存在的文件") as f:
        data = f.read()
except FileNotFoundError:
    print("文件不存在,跳过")
except PermissionError:
    print("没有权限读取文件")
finally:
    print("无论如何都会执行(收尾动作)")

import json
with open("devices.json","w") as f:
    json.dump(devices, f,indent=2,ensure_ascii=False)    #存
with open("devices.json") as f:
    loaded = json.load(f)   #读取JSON文件为Python对象
    print(loaded[0]["name"])
