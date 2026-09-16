import re
import yaml

def load_rules(path="rules.yaml"):
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)

def check_config(config_text, rules):
    """对一份配置跑全部规则，返回每条规则的检查结果列表。"""
    results = []
    for rule in rules:
        hit = re.search(rule["pattern"], config_text, re.IGNORECASE)
        if rule["type"] == "forbid":
            passed = not hit        # forbid：没命中才算过
        else:
            passed = bool(hit)      # require：命中才算过
        results.append({**rule, "pass": passed})
    return results

if __name__ == "__main__":
    from pathlib import Path

    rules = load_rules("rules.yaml")
    sample = Path(
        "/home/kxwang/code/neteng-to-sre/scripts/week9-12/day-71-77/R1_latest.txt" 
    )
    config_text = sample.read_text(encoding="utf-8")

    print(f"样本: {sample}")
    print("-" * 50)
    for r in check_config(config_text, rules):
        mark = "PASS" if r["pass"] else "FAIL"
        print(f"[{mark}] {r['id']} {r['name']}  ({r['severity']})")
        if not r["pass"]:
            print(f"       建议: {r['advice']}")