import json
from jinja2 import Template

with open("compliance_report.json", encoding="utf-8") as f:
    report = json.load(f)
with open("report.j2", encoding="utf-8") as f:
    template = Template(f.read())

html = template.render(**report)
with open("合规检查报告.html", "w", encoding="utf-8") as f:
    f.write(html)
print("报告已生成：合规检查报告.html")