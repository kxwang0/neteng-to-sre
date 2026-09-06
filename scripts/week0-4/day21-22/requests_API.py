import requests

r = requests.get("https://wttr.in/Beijing?format=j1&lang=zh", timeout=10)
print("HTTP 状态码:", r.status_code)          # 200 = 成功（HTTP 状态码是你的老本行）
data = r.json()                                # 把 JSON 响应直接转成 Python 字典
current = data["current_condition"][0]
print("北京现在:", current["lang_zh"][0]["value"], current["temp_C"], "℃")