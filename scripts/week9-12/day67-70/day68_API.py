from fastapi import FastAPI
from getpass import getpass
import yaml

app = FastAPI(title="备份平台")
PASSWORD = getpass("设备统一密码: ")   # 服务启动时输入一次

def load_devices(path="devices.yaml"):
    with open(path) as f:
        return yaml.safe_load(f)

@app.get("/devices")
def list_devices():
    devs = load_devices()
    return [{"name": d["name"], "host": d["host"]} for d in devs]

@app.post("/backup/{name}")
def backup_one_api(name: str):
    devs = {d["name"]: d for d in load_devices()}
    if name not in devs:
        return {"ok": False, "msg": f"设备 {name} 不在清单里"}
    d = devs[name]
    try:
        # 复用项目 v2 的采集逻辑（这里简写）
        from netmiko import ConnectHandler
        conn = ConnectHandler(device_type=d.get("device_type", "huawei"),
                              host=d["host"], username=d["username"],
                              password=PASSWORD)
        cfg = conn.send_command("display current-configuration")
        conn.disconnect()
        return {"ok": True, "device": name, "bytes": len(cfg)}
    except Exception as e:
        return {"ok": False, "device": name, "msg": str(e)}