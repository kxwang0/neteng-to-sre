# 配置备份 v2：零件练习手册

> 给谁：会看 `backup_v2.py`，空白文件却写不出，也没有「学写代码」的现成方法。  
> 不是新课：代码你已经跑通。这里只教**怎么练**，像当初天天练网络命令那样，但单位换成 5–15 行零件，不是 140 行整机。  
> 答案页（默写时合上）：`scripts/week5-8/day50-53/backup_v2.py`  
> 草稿文件（反复覆盖没关系）：`scripts/week5-8/day50-53/scratch.py`（没有就自己建一个空文件）

---

## 1. 先建立方法（比敲代码更重要）

### 1.1 你现在的茫然从哪来

看懂和写出是两条路：

| | 看懂（你已经会） | 写出（现在发虚） |
|---|---|---|
| 眼睛 | 代码在眼前，认熟人 | 空白，要回忆结构 |
| 网络类比 | 看着配置文本知道这是 OSPF | 自己从空设备配出一套 OSPF |
| 练错了会怎样 | 把 140 行再抄三遍，手会、脑不会 | 零件变奏 5 次，结构留下 |

v2 那几轮你真实卡的不是 Netmiko，而是：

- 零件贴在文件顶层，不属于任何函数
- `def` 下一行没缩进
- 说明里的 `...` 原样留下
- `main` 已经调用 `save_with_diff`，函数还没写

所以练的目标不是「把 140 行背下来」，而是：**先有骨架，再把零件装进对的函数。**

### 1.2 和学网络怎么对应

| 学网络（你有经验） | 学这套脚本（按这个练） |
|---|---|
| 每天练几条命令，不抄整本手册 | 每天练 2～3 张零件卡，不抄整份 `backup_v2.py` |
| `display ip interface brief` 敲熟 | `Device.connect / close` 敲熟 |
| 周末做一次完整实验 | 每周整机默写 **1 遍**，跑通就停 |
| 忘了命令查手册，不算没学会 | 忘了 `unified_diff` 参数就查，骨架能默即可 |
| 同一条命令换参数再敲（变奏） | 同一零件改一处再跑（变奏） |

通抄 140 行 = 每天把整网配置重打一遍。第三遍大脑会关机，那叫假勤奋。

### 1.3 三条纪律（违反就停）

1. **零件允许看 20 秒再合上敲；整机默写禁止粘贴、禁止开着答案打。**  
2. **报错先自己扛 10 分钟。** 先看最后一行异常类型，再看指向 `scratch.py` 的行号。10 分钟后再翻答案页 **5 秒**，合上继续。  
3. **密码永不写进 .py。** 零件用假数据就行，不必每次连真设备。

### 1.4 空白文件启动仪式（每次开练先做，3 分钟）

打开 `scratch.py`，先写中文，**不许第一行就 `from netmiko`**：

```python
# 1. 设备怎么来（YAML / argparse / 写死）
# 2. 密码怎么来（getpass，只问一次）
# 3. 怎么连上（Device 或 ConnectHandler）
# 4. 干什么（抓配置 / 比对 / 并发）
# 5. 结果去哪（文件 / logging）
# 6. 怎么断开（close / finally）
```

今天只练一张卡，六行里和这张无关的可以写「今天不练」。  
**六行写不出 = 题还没理解，不是忘了 API。** 先把中文写完再翻译。

### 1.5 一张零件卡怎么打（固定五步，8～12 分钟）

1. **看 20 秒**：只看本节「默写目标」，合上 `backup_v2.py`。  
2. **默写**：写到 `scratch.py`，保存。  
3. **跑**：`cd ~/code/neteng-to-sre/scripts/week5-8/day50-53 && python3.12 scratch.py`  
   （相对路径，Day 45 的坑：在家目录跑会找不到文件。）  
4. **变奏**：按卡上列表各改一处再跑。同一块肌肉，表面每次不同。  
5. **记账**：五次里有两次卡在同一点，抄到下面「便利贴」区，明天热身只打这一张。

过关：默写能跑通 + 至少完成 3 个变奏。不要求背下 `import` 清单。

### 1.6 每天时间盒（约 40 分钟，别加量）

| 分钟 | 做什么 |
|---|---|
| 0–3 | 六行中文骨架 |
| 3–25 | 零件卡 × 2（或卡点一张打五遍变奏） |
| 25–35 | 对照答案页，只看自己写错的那几行，写进便利贴 |
| 35–40 | 合上文件，口头说清：这个零件输入是什么、输出是什么、失败怎么收场 |

周末另加 40 分钟：整机默写 1 遍（第 4 节），不要工作日做。

---

## 2. 练习场怎么摆

```bash
cd ~/code/neteng-to-sre/scripts/week5-8/day50-53
# 没有 scratch.py 就：touch scratch.py
python3.12 scratch.py
```

- **不要改** `backup_v2.py`。那是答案页，也是已经合进 GitHub 的作品。  
- `scratch.py`、练习用的假 `latest.txt` 不要 commit。  
- 零件尽量用假数据，避免每天输密码、占设备 VTY。只有「异常顺序」「真机 diff」两张卡才连 R1。

便利贴就写在本文最末「我的卡点」里，或纸上。连续 3 天只打同一张卡也可以。

---

## 3. 七张零件卡（正餐）

从易到难。新手上前 4 张，`save_with_diff` 和线程池放到后半周。

---

### 卡 A · Device 类（连接零件）

**一句话：** 一台设备的连接状态放在实例上，`connect` / `get_config` / `close` 各干一件事。

**默写目标（允许不连真机，只把类写出来并 `print` 属性）：**

```python
class Device:
    def __init__(self, host, username, password, device_type="huawei"):
        self.host = host
        self.username = username
        self.password = password
        self.device_type = device_type
        self.conn = None          # 先占位，connect 之后才有连接

    def connect(self):
        self.conn = ConnectHandler(
            device_type=self.device_type,
            host=self.host,
            username=self.username,
            password=self.password,
            timeout=15,
        )

    def get_config(self):
        return self.conn.send_command(
            "display current-configuration",
            read_timeout=180,
        )

    def close(self):
        if self.conn:
            self.conn.disconnect()
            self.conn = None
```

**必须说得清：** `self.conn` 为什么不能写成普通局部变量 `conn`？  
答：方法之间要共用同一条 SSH；局部变量离开 `connect` 就没了。

**变奏（改一处再跑，不必真连）：**

1. 建两个实例 `r1`、`r2`，打印 `r1.host`、`r2.host`，证明互不干扰。  
2. 加方法 `run(self, cmd)`，`get_config` 改成调用它。  
3. 故意不 `connect` 就 `get_config`：自己加 `if not self.conn: raise RuntimeError("先 connect")`。  
4. `close` 里去掉 `if self.conn`，想一想第二次 `close` 会怎样。  
5. 口头：`timeout=15` 是建连超时，`read_timeout=180` 是等整份配置。

**你已踩过：** 类写对了，但后面零件贴在类外面当顶层代码。练完这张，文件里应该只有 `class` + 几行测试，不要有裸露的 `diff = ...`。

---

### 卡 B · 读 YAML 清单

**一句话：** `safe_load` 得到的是 list[dict]；空文件是 `None`，不能 `for`。

**默写目标：**

```python
import yaml

def load_devices(path):
    with open(path) as f:
        devices = yaml.safe_load(f)
    if not devices:
        raise ValueError(f"设备清单为空: {path}")
    return devices

print(load_devices("devices.yaml"))
```

**变奏：**

1. 清单改成空文件（另存 `empty.yaml`），确认会 `ValueError`，不是 `TypeError: NoneType is not iterable`。  
2. 用 `.get("name", "?")` 打印每台名字。  
3. 检查每台是否缺 `host`，缺了 `logging.error` 并跳过。  
4. 把字段 `host` 故意写成 `ip`，看 `Device` 会在哪爆（键名必须和 v2 一致）。  
5. 口头：v1 的 `devices.json` + `json.load` 和这里只换了加载函数，结构都是字典的列表。

**你已踩过：** Day 45 编辑器里有内容、磁盘是 0 字节 → `safe_load` 返回 `None`。练之前先 `ls -l` 看文件大小。

---

### 卡 C · 单台备份 + 异常顺序

**一句话：** 具体异常在前，`Exception` 在后；成功 `return` 配置，失败 `return None`；`finally` 里一定 `close`。

**默写目标（可先不连设备，把结构写全，`connect` 暂时 `return "fake-config"`）：**

```python
def backup_one(dev, password):
    d = Device(dev["host"], dev["username"], password, dev["device_type"])
    try:
        d.connect()
        return d.get_config()
    except NetmikoTimeoutException:
        logging.error("%s 连接超时：网络不通或设备没开 SSH", dev["name"])
    except NetmikoAuthenticationException:
        logging.error("%s 认证失败：用户名/密码或 aaa 配置问题", dev["name"])
    except Exception as e:
        logging.error("%s 未预期错误：%s", dev["name"], e)
    finally:
        d.close()
    return None
```

**必须说得清：** `try` 里 `return` 之后 `finally` 还会不会跑？  
答：会。所以成功也会断开，设备上不留僵尸 SSH。

**变奏：**

1. 把 `except Exception` 挪到最前，注释为什么 Timeout/Auth 永远走不到。  
2. 假数据：`connect` 里 `raise` 一个普通 `Exception`，确认落到第三条、返回 `None`。  
3. 连真机时只改错 IP（测超时）；下次只改错密码（测认证）。一次只错一件。  
4. 去掉 `finally`，想一想成功路径忘了 `close` 的后果。  
5. `else: pass` 不要写。成功路径就是 `try` 里 `return`。

**你已踩过：** 函数体没缩进 → `IndentationError`。`def` 下面每一行都要缩进一级。

---

### 卡 D · argparse + logging 双输出

**一句话：** 清单路径和并发数从命令行走；日志同时打屏和落盘；密码不进 argv。

**默写目标：**

```python
import argparse
import logging
from getpass import getpass

parser = argparse.ArgumentParser(description="网络设备配置备份工具 v2")
parser.add_argument("--config", default="devices.yaml", help="设备清单 YAML")
parser.add_argument("--workers", type=int, default=5, help="并发线程数")
args = parser.parse_args()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("scratch.log", encoding="utf-8"),
        logging.StreamHandler(),
    ],
)

print(args.config, args.workers)
# password = getpass("设备统一密码: ")   # 零件阶段可注释，整机再打开
logging.info("清单=%s workers=%s", args.config, args.workers)
```

跑：

```bash
python3.12 scratch.py --help
python3.12 scratch.py --config devices.yaml --workers 2
```

**变奏：**

1. `--workers` 去掉 `type=int`，传入 `2` 后和数字比大小，看类型变成 str。  
2. 再加 `--backup-dir`，默认 `backups`。  
3. `level=DEBUG`，加一条 `logging.debug("细节")`，再改回 INFO 看它消失。  
4. 五个级别背一遍：DEBUG → INFO → WARNING → ERROR → CRITICAL。  
5. 口头：`logging` 是脚本日记，不是设备 `display logbuffer`。

---

### 卡 E · save_with_diff（v2 真正升级点）

**一句话：** 先读 `latest`，再决定写不写。相同只记日志；不同才写日期版 + 覆盖 latest。

**默写目标（全程假数据，不连设备）：**

```python
import difflib
import logging
import os
from datetime import date

def save_with_diff(name, new_cfg, backup_dir="scratch_backups"):
    os.makedirs(backup_dir, exist_ok=True)
    latest = os.path.join(backup_dir, f"{name}_latest.txt")

    old = ""
    if os.path.exists(latest):
        with open(latest) as f:
            old = f.read()

    if old == new_cfg:
        logging.info("%s 无变更", name)
        return False

    diff = difflib.unified_diff(
        old.splitlines(), new_cfg.splitlines(),
        fromfile="旧配置", tofile="新配置", lineterm="",
    )
    changes = [
        line for line in diff
        if line.startswith(("+", "-")) and not line.startswith(("+++", "---"))
    ]
    logging.info("%s 配置变更，差异 %d 行", name, len(changes))

    today = date.today().isoformat()
    dated = os.path.join(backup_dir, f"{name}_{today}.txt")
    with open(dated, "w") as f:
        f.write(new_cfg)
    with open(latest, "w") as f:
        f.write(new_cfg)
    return True
```

文件末尾自测（这才是这张卡的跑法）：

```python
logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
print("第一次", save_with_diff("LAB", "sysname R1\n"))
print("第二次", save_with_diff("LAB", "sysname R1\n"))
print("改字  ", save_with_diff("LAB", "sysname R1-NEW\n"))
```

预期：`True` → `False`（无变更，目录不新增长日期文件）→ `True`。

**必须说得清：** 为什么必须先读 latest 再写？  
答：写反了，读到的就是刚写进去的自己，永远「无变更」。

**变奏：**

1. `lineterm=""` 去掉，看 diff 行数是否虚高。  
2. `changes` 过滤条件去掉，数一数会不会把 `---` / `+++` 算进去。  
3. `backup_dir` 改成 `scratch_backups2`，确认 `makedirs(..., exist_ok=True)` 不报错。  
4. 同一天改两次，日期文件名相同，第二次覆盖——接受这个行为。  
5. 口头：v1 每次都写日期版；v2 无变更不归档。这是需求第 6 条。

**你已踩过：** 把 `unified_diff` 贴在模块顶层，`old` / `new_cfg` 还不存在。这段只能活在函数里面。

---

### 卡 F · 线程池 + 失败隔离

**一句话：** 每台提交一个任务；谁先完谁处理；返回 `None` 记失败，不要让一台异常把循环打断。

**默写目标（假 `backup_one`，不连设备）：**

```python
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

def backup_one(dev, password):
    name = dev["name"]
    if name == "R-BAD":
        time.sleep(0.2)
        return None
    time.sleep(0.1)
    return f"{name} fake-config"

devices = [
    {"name": "R1"},
    {"name": "R-BAD"},
    {"name": "R2"},
]
ok, failed = [], []

with ThreadPoolExecutor(max_workers=2) as pool:
    futures = {pool.submit(backup_one, dev, "x"): dev for dev in devices}
    for fut in as_completed(futures):
        dev = futures[fut]
        name = dev["name"]
        cfg = fut.result()
        if cfg is None:
            failed.append(name)
            continue
        ok.append(name)

print("成功", ok, "失败", failed)
```

**变奏：**

1. `max_workers=1`，看完成顺序更接近提交顺序。  
2. 在假 `backup_one` 里对某台 `raise RuntimeError`，外层给 `fut.result()` 再包一层 `try`。  
3. 成功后再调用卡 E 的 `save_with_diff`。  
4. 口头：`max_workers` 别大于设备 VTY（华为默认大约 5）。  
5. 口头：采集是 I/O 等待，用线程池；不是因为「看起来高级」。

---

### 卡 G · 六行骨架 → 四个函数名（组装，不写满 140 行）

**一句话：** 整机之前先能默出函数分工。写不出函数名，就还没资格抄 `main`。

**默写目标（只写注释 + 空函数 + `pass`，10 分钟内）：**

```python
# 1. 设备怎么来：load_devices(path) ← YAML
# 2. 密码怎么来：main 里 getpass 一次，传给每台
# 3. 怎么连上：Device 类
# 4. 干什么：backup_one 抓配置；线程池并发
# 5. 结果去哪：save_with_diff；logging 汇总
# 6. 怎么断开：backup_one 的 finally close

class Device:
    pass

def load_devices(path):
    pass

def backup_one(dev, password):
    pass

def save_with_diff(name, new_cfg, backup_dir="backups"):
    pass

def main():
    pass

if __name__ == "__main__":
    main()
```

**变奏：** 合上答案页，在纸上画：`main` 调用谁、谁返回 `None`、谁返回 `True/False`。画不出来就再打卡 A～F，不要开始整机。

---

## 4. 整机默写（每周最多 1 次）

工作日只打零件。周末或你认为 A～G 都过关时，才做这一节。

1. 合上 `backup_v2.py` 和本文第 3 节。  
2. 新文件 `from_memory.py`（不要覆盖作品）。  
3. 先写六行中文，再填。卡住看答案 **5 秒**，合上继续。  
4. 只默 **一遍**。`python3.12 from_memory.py --help` 能出来就算结构对；连设备自选。  
5. 跑通 = 过关。**不要默第二遍。** 想练就回到零件变奏。

对照清单（默完再勾，默的时候别看）：

- [ ] YAML + `safe_load` + 空清单判断  
- [ ] Device 类  
- [ ] `backup_one` 异常顺序 + `finally close` + 失败 `None`  
- [ ] `--config` / `--workers`  
- [ ] logging 文件 + 屏幕  
- [ ] 线程池，单台失败继续  
- [ ] 无变更不写日期文件  
- [ ] `getpass`，密码不进文件  
- [ ] `if __name__ == "__main__"`

---

## 5. 两周日程（照着打即可）

每天约 40 分钟。打卡就在本节日期后打勾。

| 天 | 练什么 | 完成 |
|---|---|---|
| D1 | 第 1 节读完 + 卡 A 变奏 ×3 | [ ] |
| D2 | 卡 B + 卡 A 各一遍（防忘） | [ ] |
| D3 | 卡 C 结构（假数据，不连设备） | [ ] |
| D4 | 卡 D `--help` 必须像样 | [ ] |
| D5 | 卡 E 假数据三次调用（有变更/无变更/再变更） | [ ] |
| D6 | 卡 C 真机：错 IP 一次、对密码一次（可选） | [ ] |
| D7 | 休息或只复述六行骨架 | [ ] |
| D8 | 卡 F 假并发 | [ ] |
| D9 | 卡 E + 卡 F 焊在一起（仍假数据） | [ ] |
| D10 | 卡 G 只写函数名和注释 | [ ] |
| D11 | 对着便利贴，只打最弱的一张，变奏 5 次 | [ ] |
| D12 | 第 4 节整机默写 1 遍 | [ ] |
| D13 | 改造选 1：加 `--backup-dir`，或失败也写 `failed.txt` | [ ] |
| D14 | 口头给自己讲：v1 和 v2 差在哪 6 点 | [ ] |

某张连续 3 天不过：日程暂停，只打那一张，过了再往下。

---

## 6. 怎样算「这块熟了」（不要用「能背 140 行」当标准）

隔天合上答案，能做到：

1. 六行中文 3 分钟写完。  
2. 说出四个函数各自的输入 / 输出 / 失败返回值。  
3. 空白文件 15 分钟内默出卡 E 并跑通三次自测。  
4. 看到 `TypeError: 'NoneType' is not iterable` 能立刻说：YAML 空了或 `backup_one` 当列表用了。  
5. 看到 `NameError: old is not defined` 能立刻说：零件写在函数外面了。

做不到 1、2，继续零件，不要加量抄整机。

---

## 7. 和仓库里其它入口的关系

| 入口 | 干什么 |
|---|---|
| `python3.12 ~/code/neteng-to-sre/scripts/drill/interactive.py` | 回炉 A–L 零件，继续打，和本文不冲突 |
| 本文卡 A–G | 专门练毕业作品 v2 的组装 |
| `backup_v2.py` | 答案页，默写时合上 |
| `scripts/week5-8/day50-53/README.md` | 作品说明，给陌生人跑工具，不是练习册 |

每天若只选一个：工作日 interactive **或** 本文 2 张卡；不要同一天既抄 140 行又打 interactive。

---

## 8. 我的卡点（自己填，这是有效重复的证据）

日期 / 卡号 / 卡在哪一行语法 / 明天是否只打这一张：

```
# 例：2026-09-14  卡 C  def 下一行没缩进  是
#
#
#
```

---

## 9. 开始的第一件事（现在就做）

```bash
cd ~/code/neteng-to-sre/scripts/week5-8/day50-53
touch scratch.py
```

打开 `scratch.py`，写六行中文，再打 **卡 A**。不要打开 `backup_v2.py` 对着抄。看 20 秒、合上、敲、跑、改一个变奏。今天到此为止。
