#!/usr/bin/env python3.12
"""回炉零件训练：终端选题 → 改 workspace.py → 回车批改 → 立刻过关/提示。

用法（在仓库根目录或本目录均可）：
    python3.12 scripts/drill/interactive.py
"""
from __future__ import annotations

import io
import json
import os
import re
import sys
import traceback
from datetime import date
from pathlib import Path
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
WORKSPACE = HERE / "workspace.py"
PROGRESS = HERE / ".progress.json"
TODAY = date.today().isoformat()

G = "\033[32m"
R = "\033[31m"
C = "\033[36m"
Y = "\033[33m"
B = "\033[1m"
Z = "\033[0m"


def cprint(color: str, msg: str) -> None:
    if sys.stdout.isatty():
        print(f"{color}{msg}{Z}")
    else:
        print(msg)


def load_progress() -> dict:
    if PROGRESS.exists():
        return json.loads(PROGRESS.read_text(encoding="utf-8"))
    return {"xp": 0, "cards": {}}


def save_progress(p: dict) -> None:
    PROGRESS.write_text(json.dumps(p, ensure_ascii=False, indent=2), encoding="utf-8")


def xp_bar(xp: int) -> str:
    level = xp // 50 + 1
    into = xp % 50
    filled = into // 5
    return f"Lv{level} [{ '#' * filled }{'.' * (10 - filled) }] {xp} XP"


# ---------------------------------------------------------------------------
# 批改：返回 (是否过关, 一条条反馈)
# ---------------------------------------------------------------------------

def src_has_literal_password(src: str) -> bool:
    return bool(re.search(r"""password\s*=\s*['"][^'"]+['"]""", src))


def run_source(src: str, argv: list[str] | None = None, extra_globals: dict | None = None):
    ns = extra_globals.copy() if extra_globals else {}
    buf = io.StringIO()
    argv = argv or ["workspace.py"]
    with patch("sys.argv", argv), patch("getpass.getpass", return_value="secret"), patch(
        "sys.stdout", buf
    ):
        exec(compile(src, str(WORKSPACE), "exec"), ns, ns)
    return ns, buf.getvalue()


def check_A(src: str, ns: dict, out: str, var: str) -> list[tuple[bool, str]]:
    hits = []
    hits.append((not src_has_literal_password(src), "密码用 getpass，不能写成字符串字面量"))
    hits.append(("getpass" in src, "有 from getpass import getpass"))
    hits.append(("dev" in ns and isinstance(ns.get("dev"), dict), "存在名为 dev 的字典"))
    d = ns.get("dev") or {}
    hits.append(("host" in d and "username" in d and "device_type" in d, "含 host / username / device_type"))
    if var == "1":
        hits.append((d.get("host") == "192.168.30.252", "host 是 192.168.30.252"))
        hits.append((d.get("device_type") == "huawei", "device_type 是 huawei"))
    if var == "2":
        hits.append((d.get("device_type") == "huawei_vrp", "device_type 改成 huawei_vrp（找 ntc 模板用）"))
    if var == "3":
        hits.append(("port" in d and d.get("port") in (22, "22"), "字典里有 port=22"))
    return hits


def check_B(src: str, ns: dict, out: str, var: str) -> list[tuple[bool, str]]:
    hits = []
    hits.append(("**" in src, "用了 ** 拆包（ConnectHandler(**dev) 或 demo(**d)）"))
    hits.append(("def " in src, "定义了函数"))
    if var == "1":
        hits.append(("kwargs" in src or "**" in src, "函数能接收关键字参数"))
        hits.append(("{" in out or "host" in out, "调用后有打印（能看到字典或 host）"))
    if var == "2":
        hits.append(("ConnectHandler" in src or "connect" in src.lower() or "demo" in src, "有拆包调用"))
    if var == "3":
        hits.append(("*" in src and "**" in src or "tag" in src, "普通参数和 ** 一起用，或写了对比"))
    return hits


def check_C(src: str, ns: dict, out: str, var: str) -> list[tuple[bool, str]]:
    hits = []
    hits.append(("with open" in src, "用了 with open"))
    # with 必须在 for 外面：粗检 for 出现在 with 块内，不能 with 在 for 内
    with_before_for = src.find("with open") != -1 and (
        src.find("for ") == -1 or src.find("with open") < src.find("for ")
    )
    hits.append((with_before_for, "with open 在 for 循环外面（否则每次清空只剩最后一条）"))
    out_file = HERE / "drill_out.txt"
    hits.append((out_file.exists() and out_file.stat().st_size > 0, f"写了文件 {out_file.name}"))
    if out_file.exists():
        text = out_file.read_text(encoding="utf-8", errors="replace")
        hits.append(("=====" in text or "display" in text, "文件里有命令分隔或内容"))
        if var == "2":
            hits.append((str(date.today()) in str(ns) or str(date.today()) in src or str(date.today()) in text,
                         "文件名或内容带上今天日期"))
        if var == "3":
            hits.append(("utf-8" in src, "open(..., encoding='utf-8')"))
    return hits


def check_D(src: str, ns: dict, out: str, var: str) -> list[tuple[bool, str]]:
    hits = []
    hits.append(("def collect" in src or "def " in src, "定义了函数"))
    hits.append(("return " in src, "函数里有 return（不要只 print）"))
    fns = [v for v in ns.values() if callable(v) and getattr(v, "__name__", "") != "<lambda>"]
    hits.append((bool(fns), "函数成功定义进内存"))
    if fns and var == "1":
        try:
            r = fns[0]("192.168.30.252", "display version") if fns[0].__code__.co_argcount >= 2 else fns[0]()
            hits.append((r is not None, "调用有返回值，不是 None"))
        except TypeError:
            hits.append((True, "函数可调用（参数你自己定）"))
    if var == "3":
        hits.append(('"""' in src or "'''" in src, "写了 docstring"))
    return hits


def check_E(src: str, ns: dict, out: str, var: str) -> list[tuple[bool, str]]:
    hits = []
    hits.append(("import re" in src or "from re" in src, "import re"))
    hits.append(("r\"" in src or "r'" in src, "正则用了原始字符串 r\"...\""))
    hits.append(("search" in src or "findall" in src, "用了 search 或 findall"))
    hits.append(("if " in src or "else" in src or "if m" in src, "search 结果判空再 .group()"))
    hits.append(("8.180" in out or "CE12800" in out or "GE" in out or "未匹配" in out or out.strip() != "",
                 "有打印结果"))
    return hits


def check_F(src: str, ns: dict, out: str, var: str) -> list[tuple[bool, str]]:
    hits = []
    hits.append(("import logging" in src, "import logging"))
    hits.append(("basicConfig" in src, "调用 logging.basicConfig"))
    hits.append(("logging.info" in src, "有 logging.info"))
    hits.append(("logging.warning" in src or "logging.error" in src, "有 warning 或 error"))
    hits.append((not src_has_literal_password(src) and "password" not in src.lower() or "getpass" in src,
                 "不要把密码写进日志字符串"))
    if var == "2":
        hits.append(("FileHandler" in src or "filename=" in src, "日志同时落盘"))
    return hits


def check_G(src: str, ns: dict, out: str, var: str) -> list[tuple[bool, str]]:
    hits = []
    hits.append(("argparse" in src, "import argparse"))
    hits.append(("add_argument" in src, "有 add_argument"))
    hits.append(('"-H"' in src or "'-H'" in src, "设备 IP 用大写 -H（小写 -h 是帮助）"))
    hits.append(("parse_args" in src, "调用 parse_args"))
    hits.append(("args" in ns, "解析出了 args"))
    args = ns.get("args")
    if args is not None and var == "1":
        hits.append((getattr(args, "host", None) == "192.168.30.252", "args.host 是 192.168.30.252"))
    return hits


def check_H(src: str, ns: dict, out: str, var: str) -> list[tuple[bool, str]]:
    hits = []
    hits.append(("try:" in src, "有 try"))
    hits.append(("except" in src, "有 except"))
    # Exception 必须在后面
    pos_ex = src.find("except Exception")
    pos_t = src.find("except")
    hits.append((pos_ex == -1 or pos_ex > pos_t + 5, "具体异常在前，except Exception 在后"))
    hits.append(("Timeout" in src or "Auth" in src or "Netmiko" in src or "except" in src, "区分了不同失败"))
    if var == "1":
        hits.append(("超时" in out or "认证" in out or "timeout" in out.lower() or "auth" in out.lower() or out,
                     "分支有打印"))
    return hits


def check_I(src: str, ns: dict, out: str, var: str) -> list[tuple[bool, str]]:
    hits = []
    hits.append(("class Device" in src or "class " in src, "定义了 class"))
    hits.append(("def __init__" in src, "有 __init__"))
    hits.append(("self.conn" in src, "连接挂在 self.conn 上"))
    hits.append(("def connect" in src and "def run" in src, "有 connect 和 run"))
    hits.append(("def close" in src, "有 close"))
    Device = ns.get("Device")
    if Device and var != "3":
        try:
            r1 = Device("192.168.30.252") if Device.__init__.__code__.co_argcount == 2 else None
            hits.append((r1 is not None or "r1" in ns, "造出了实例"))
        except TypeError:
            hits.append(("r1" in ns or "Device(" in src, "有实例化"))
    if var == "3":
        hits.append(("r1" in src and "r2" in src, "造了两个实例证明互不干扰"))
    return hits


def check_J(src: str, ns: dict, out: str, var: str) -> list[tuple[bool, str]]:
    hits = []
    hits.append(("huawei_vrpv8" in src or "commit" in src.lower() or "send_config_set" in src,
                 "提到 vrpv8 / commit / send_config_set"))
    hits.append(("commit" in src.lower() or "commit" in out.lower(), "有 commit 这一步"))
    hits.append(("验证" in src or "display" in src or "verify" in src.lower(), "下发后有验证"))
    if var == "2":
        hits.append(("undo" in src.lower() or "回退" in src, "有回退 undo"))
    return hits


def check_K(src: str, ns: dict, out: str, var: str) -> list[tuple[bool, str]]:
    hits = []
    hits.append(("Filldown" in src or "filldown" in src.lower() or "AREA" in src, "用了 Filldown 或 AREA 字段"))
    hits.append(("Record" in src, "有 -> Record"))
    hits.append(("Area" in src or "AREA" in src, "有 Area 行规则"))
    # Area 行不应和 Record 写在同一规则（粗检：Area 那行不要 Record）
    bad = False
    for line in src.splitlines():
        if "Area" in line and "Record" in line and "Filldown" not in line:
            bad = True
    hits.append((not bad, "Area 行不要 -> Record（只更新 Filldown）"))
    return hits


def check_L(src: str, ns: dict, out: str, var: str) -> list[tuple[bool, str]]:
    hits = []
    hits.append(("list" in src or "isinstance" in src or "TextFSMError" in src or "use_textfsm" in src,
                 "处理了 list / 原始字符串 / 异常 至少一种"))
    hits.append(("huawei_vrp" in src or "NET_TEXTFSM" in src or "ntc" in src.lower() or "Error" in src,
                 "提到 huawei_vrp、NET_TEXTFSM 或解析失败"))
    hits.append(("print" in src or out.strip() != "", "有输出"))
    return hits


CARDS = {
    "A": {
        "title": "连接字典 + getpass",
        "check": check_A,
        "argv": ["workspace.py"],
        "vars": {
            "1": "写 dev 字典：huawei / 192.168.30.252 / admin1，密码必须 getpass。最后可以 print(dev['host'])。",
            "2": "同上，但 device_type 改成 huawei_vrp（找 ntc 模板才对得上 index）。",
            "3": "在字典里加上 port: 22。密码仍用 getpass。",
        },
    },
    "B": {
        "title": "** 拆包",
        "check": check_B,
        "argv": ["workspace.py"],
        "vars": {
            "1": "写 def demo(**kwargs): print(kwargs)，用字典 d 调用 demo(**d)。",
            "2": "写一个假的 connect(dev: dict)，内部用 ConnectHandler 的形状：把 **dev 传给 print 也行，不必真连设备。",
            "3": "对比 demo(**d) 和 demo(host=..., username=...) 两种写法，都打印出来。",
        },
    },
    "C": {
        "title": "with open 在循环外",
        "check": check_C,
        "argv": ["workspace.py"],
        "vars": {
            "1": "cmds 两条假命令，with open('drill_out.txt','w') 在 for 外面，写成 ===== cmd =====。",
            "2": "文件名带上今天日期（datetime.date.today()）。仍写到本目录，名字里有日期即可。",
            "3": "open 加上 encoding='utf-8'。",
        },
    },
    "D": {
        "title": "函数要 return",
        "check": check_D,
        "argv": ["workspace.py"],
        "vars": {
            "1": "def collect(host, cmd): return 某字符串。主程序调用并 print 返回值。",
            "2": "collect 返回 {{cmd: 'fake'}} 字典。",
            "3": "给 collect 写一行 docstring，并加默认参数 device_type='huawei'。",
        },
    },
    "E": {
        "title": "正则 + 判空",
        "check": check_E,
        "argv": ["workspace.py"],
        "vars": {
            "1": "本地字符串含 Version 8.180，re.search 抠出版本号，找不到要打印未匹配。",
            "2": "findall 找出文本里所有 IP（形如 192.168.30.252）。",
            "3": "把 Version 那行改成没有 Version，确认走未匹配分支、不炸。",
        },
    },
    "F": {
        "title": "logging",
        "check": check_F,
        "argv": ["workspace.py"],
        "vars": {
            "1": "basicConfig + info/warning/error 各一条。密码不要出现在日志里。",
            "2": "同时 FileHandler 写 drill_out.log（本目录）。",
            "3": "level=DEBUG，再加一条 logging.debug。",
        },
    },
    "G": {
        "title": "argparse -H 不是 -h",
        "check": check_G,
        "argv": ["workspace.py", "-H", "192.168.30.252", "-u", "admin1"],
        "vars": {
            "1": "ArgumentParser，-H/--host required，-u 默认 admin1，打印 args.host。",
            "2": "再加 -o/--output 默认 out.txt。",
            "3": "description 写一句话。批改时会自动传入 -H 192.168.30.252。",
        },
    },
    "H": {
        "title": "except 具体在前",
        "check": check_H,
        "argv": ["workspace.py"],
        "vars": {
            "1": "自定义 Timeout/Auth 异常，try/except 顺序：Timeout → Auth → Exception。三种 case 都跑一下。",
            "2": "成功路径用 else: 打印成功。",
            "3": "把 Exception 写在最前试一次（应感到具体 except 失效），再改回正确顺序。最终提交正确顺序。",
        },
    },
    "I": {
        "title": "Device 类 connect/run/close",
        "check": check_I,
        "argv": ["workspace.py"],
        "vars": {
            "1": "class Device，self.conn=None，connect/run/close。假连接即可，不连真机。",
            "2": "加 run_many(cmds) 返回 dict。",
            "3": "r1、r2 两个实例，打印证明 host 互不干扰。",
        },
    },
    "J": {
        "title": "VRP8 下发顺序（不必连设备）",
        "check": check_J,
        "argv": ["workspace.py"],
        "vars": {
            "1": "用 print 写出三步：huawei_vrpv8 的 send_config_set → commit → display 验证。",
            "2": "再加上回退：undo interface LoopBack 100 → commit。注明不要 display 已删接口。",
            "3": "注释写清 huawei 为什么会 Pattern not detected: '>'。",
        },
    },
    "K": {
        "title": "Filldown 模板",
        "check": check_K,
        "argv": ["workspace.py"],
        "vars": {
            "1": "写一段 TextFSM 模板字符串：Value Filldown AREA，Area 行不 Record，邻居行 Record。",
            "2": "给 RID 加 Required。",
            "3": "注释写明行尾不能写单个 $ 。",
        },
    },
    "L": {
        "title": "ntc 三种结果",
        "check": check_L,
        "argv": ["workspace.py"],
        "vars": {
            "1": "用注释或 print 列出：命中 list / CE 图例 Error / d[[ir]] 误匹配。",
            "2": "写一段 if isinstance(result, list) / except TextFSMError 的骨架（可假数据）。",
            "3": "注明 NET_TEXTFSM 要用 ntc_templates 包路径，device_type 找模板用 huawei_vrp。",
        },
    },
}


STARTER = """\
# 任务写在终端里。从下一行开始敲，不要粘贴手册。
# 写好保存，回到终端按回车批改。

"""


def write_starter() -> None:
    WORKSPACE.write_text(STARTER, encoding="utf-8")


def grade(card_id: str, var: str) -> tuple[bool, list[str]]:
    src = WORKSPACE.read_text(encoding="utf-8")
    if src.strip() == STARTER.strip() or len(src.strip()) < 20:
        return False, ["workspace.py 几乎是空的。先写再批改。"]
    card = CARDS[card_id]
    try:
        ns, out = run_source(src, argv=card.get("argv"))
    except Exception:
        tb = traceback.format_exc().splitlines()
        short = [line for line in tb if "workspace.py" in line or line.startswith("    ")][-6:]
        return False, ["运行报错（先把这几行看懂再改）："] + short[-8:]
    hits = card["check"](src, ns, out, var)
    lines = []
    ok_all = True
    for ok, msg in hits:
        if ok:
            lines.append(f"  ✓ {msg}")
        else:
            ok_all = False
            lines.append(f"  ✗ {msg}")
    return ok_all, lines


def mark_pass(p: dict, card_id: str, var: str) -> None:
    p["xp"] = p.get("xp", 0) + 10
    cards = p.setdefault("cards", {})
    c = cards.setdefault(card_id, {"passed": [], "last": TODAY})
    if var not in c["passed"]:
        c["passed"].append(var)
    c["last"] = TODAY
    save_progress(p)


def menu(p: dict) -> None:
    print()
    cprint(B + C, "════ 回炉零件训练 ════")
    print("  " + xp_bar(p.get("xp", 0)))
    print("  选题 → 改 workspace.py → 回车批改。过关立刻 +10 XP。")
    print()
    for cid, card in CARDS.items():
        passed = p.get("cards", {}).get(cid, {}).get("passed", [])
        stars = "★" * len(passed) + "☆" * (3 - len(passed))
        print(f"  [{cid}] {card['title']:<18} {stars}  {len(passed)}/3 变奏")
    print("  [q] 退出")
    print()


def session(card_id: str, p: dict) -> None:
    card = CARDS[card_id]
    passed = set(p.get("cards", {}).get(card_id, {}).get("passed", []))
    remaining = [v for v in ("1", "2", "3") if v not in passed] or ["1", "2", "3"]
    var = remaining[0]
    write_starter()
    print()
    cprint(B, f"【{card_id} {card['title']} · 变奏 {var}/3】")
    print(card["vars"][var])
    print()
    cprint(Y, f"请编辑：{WORKSPACE}")
    print("写好保存后，回到这里按回车批改。（输入 s 跳过本变奏，b 回菜单）")
    fails = 0
    while True:
        cmd = input("批改/s/b > ").strip().lower()
        if cmd == "b":
            return
        if cmd == "s":
            return
        ok, lines = grade(card_id, var)
        print()
        for line in lines:
            if line.startswith("  ✓"):
                cprint(G, line)
            elif line.startswith("  ✗"):
                cprint(R, line)
            else:
                print(line)
        if ok:
            mark_pass(p, card_id, var)
            cprint(G + B, "过关。手指记得住了。+10 XP")
            print("  " + xp_bar(load_progress().get("xp", 0)))
            nxt = input("下一变奏？[Y/n] ").strip().lower()
            if nxt == "n":
                return
            p = load_progress()
            passed = set(p.get("cards", {}).get(card_id, {}).get("passed", []))
            remaining = [v for v in ("1", "2", "3") if v not in passed]
            if not remaining:
                cprint(C, "这张卡 3 个变奏都过了。回菜单换一张。")
                return
            var = remaining[0]
            write_starter()
            print()
            cprint(B, f"【变奏 {var}/3】")
            print(card["vars"][var])
            cprint(Y, "workspace.py 已清空，重新敲。")
            fails = 0
        else:
            fails += 1
            cprint(Y, "还没过。改 workspace.py 再按回车。")
            if fails >= 2:
                print("提示：对照终端里的 ✗ 逐条补，不要一次重写整篇。")


def main() -> None:
    HERE.mkdir(parents=True, exist_ok=True)
    if not WORKSPACE.exists():
        write_starter()
    os.chdir(HERE)
    p = load_progress()
    cprint(C, "热身零件，不是整份脚本。每次过关都有反馈。")
    print(f"工作区：{WORKSPACE}")
    while True:
        p = load_progress()
        menu(p)
        choice = input("选卡片 > ").strip().upper()
        if choice in ("Q", "QUIT", "退出"):
            cprint(C, "今日 XP 已记在 .progress.json。明天见。")
            return
        if choice not in CARDS:
            print("输入 A–L 或 q。")
            continue
        session(choice, p)


if __name__ == "__main__":
    main()
