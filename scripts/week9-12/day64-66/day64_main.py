from fastapi import FastAPI

app = FastAPI(title="网络自动化平台")

@app.get("/")
def index():
    return {"msg": "网络自动化平台 API 在线"}

@app.get("/devices")
def devices():
    return [{"name": "R1", "ip": "192.168.30.252", "vendor": "huawei"}]