from jinja2 import Template
import yaml

with open("day45_interface.j2") as f:
    template = Template(f.read())
with open("day45_devices.yaml") as f:
    devices = yaml.safe_load(f)        # 必须用 safe_load，见验收题

for dev in devices:
    config = template.render(dev)
    filename = f"{dev['hostname']}_生成配置.txt"
    with open(filename, "w") as f:
        f.write(config)
    print(f"{filename} 已生成")