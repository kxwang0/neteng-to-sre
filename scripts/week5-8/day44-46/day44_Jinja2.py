from jinja2 import Template
t = Template("sysname {{ hostname }}")
print(t.render(hostname="R1"))