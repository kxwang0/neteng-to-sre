# 配置备份工具 v2

相对 Day 26–27 的 v1，这是工程化版本：YAML 清单、Device 类、logging 双输出、命令行参数、并发采集、变更才归档。

## 环境

- Python 3.12
- `netmiko`、`PyYAML`

```bash
python3.12 -m pip install netmiko PyYAML
```

密码运行时输入，不要写进脚本、YAML 或日志。

## 设备清单

编辑同目录下的 `devices.yaml`：

```yaml
- name: R1
  host: 192.168.30.252
  username: admin1
  device_type: huawei
- name: R-BAD
  host: 192.168.30.250
  username: admin1
  device_type: huawei
```

字段：`name` / `host` / `username` / `device_type`。`R-BAD` 是故意不可达的地址，用来验收「一台失败，其他继续」。

## 用法

在本目录执行（相对路径才找得到默认清单）：

```bash
cd scripts/week5-8/day50-53
python3.12 backup_v2.py --help
python3.12 backup_v2.py --config devices.yaml --workers 2
```

| 参数 | 默认 | 含义 |
|---|---|---|
| `--config` | `devices.yaml` | 设备清单路径 |
| `--workers` | `5` | 并发线程数（别超过设备 VTY 数量） |

## 示例输出

第一次跑（R1 通、R-BAD 不通）：

```text
设备统一密码:
2026-09-13 00:04:42,857 [INFO] Authentication (password) successful!
2026-09-13 00:04:45,509 [INFO] R1 配置变更，差异 87 行
2026-09-13 00:04:45,647 [ERROR] R-BAD 连接超时：网络不通或设备没开 SSH
2026-09-13 00:04:45,648 [INFO] 成功 1 台，失败 1 台，有变更 1 台
```

连续再跑一次，配置没改过：

```text
[INFO] R1 无变更
[ERROR] R-BAD 连接超时：网络不通或设备没开 SSH
[INFO] 成功 1 台，失败 1 台，有变更 0 台
```

## 产物

| 路径 | 作用 |
|---|---|
| `backups/R1_latest.txt` | 当前最新配置，下次 diff 的基准 |
| `backups/R1_YYYY-MM-DD.txt` | 有变更时才写的日期归档 |
| `backup.log` | 屏幕同步落盘的运行日志 |

`backups/` 和 `backup.log` 不要提交到 Git（含真机配置）。
