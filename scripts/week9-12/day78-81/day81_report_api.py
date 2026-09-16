from pathlib import Path
from fastapi import FastAPI
from fastapi.responses import FileResponse, HTMLResponse

HERE = Path(__file__).resolve().parent
REPORT = HERE / "合规检查报告.html"

app = FastAPI(title="合规报告")

@app.get("/")
def index():
    return {"msg": "打开 /report 看合规检查报告"}

@app.get("/report")
def report():
    if not REPORT.exists():
        return HTMLResponse("<p>还没有报告，先跑 day80_check.py</p>", status_code=404)
    return FileResponse(REPORT, media_type="text/html; charset=utf-8")