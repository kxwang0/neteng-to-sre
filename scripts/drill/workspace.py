# 任务写在终端里。从下一行开始敲，不要粘贴手册。
# 写好保存，回到终端按回车批改。

import re
text = "8.180 (CE12800 V200R005C10SPC607B607)"
m = re.search(r"\s+([\d.]+)",text)
print(m.group(1) if m else "未匹配")