from fastapi import FastAPI

app = FastAPI(title="网络自动化平台")

@app.get("/devices/{name}")
def get_device(name: str):
    return {"name": name, "status": "up"}   # 真实场景去查清单/设备

@app.post("/backup/{name}")
def backup(name: str):
    return {"device": name, "result": "备份完成（示意）"}