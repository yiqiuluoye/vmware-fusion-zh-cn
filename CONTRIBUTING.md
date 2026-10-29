# 贡献指南

## 贡献翻译

译文全部集中在 **`vmsg/vmware.vmsg`**（2715 条）。格式是一行一条：

```
msg.fusion.settings.general.name = "通用"
```

三条硬规则，`python3 fzp.py verify` 会检查：

1. **换行**写 `|0A`，**双引号**写 `|22`，**百分号**写 `%%`
2. 多参数一律用编号占位符 `%1$s %2$s`，**不可**与 `%s` 混用
3. 键名不能杜撰，必须来自 app 二进制里的 `@&!*@*@(键名)英文`

尚未翻译的键名清单见 [docs/remaining-keys.txt](docs/remaining-keys.txt)（只列键名，
英文原文请在你本机 app 里自行查阅，仓库不入库厂商文本）。

提交前：

```bash
python3 fzp.py verify                 # 格式 + 重复键 + 占位符
sudo python3 fzp.py install --dry-run # 看会改哪些文件（不写盘）
```

## 报告问题

用 Issue 模板：**翻译错误 / 仍为英文 / 安装失败**。请附：

- macOS 版本、Fusion 版本与 build（`python3 fzp.py doctor` 的输出）
- 截图（标出位置）
- 若涉及崩溃，附 `~/Library/Logs/DiagnosticReports/VMware Fusion-*.ips`

## 不要做的事

- 不要提交 VMware / Broadcom 的二进制、EULA 原文或其他厂商版权文本
- 不要提交 `backup/`（含用户机器上的文件副本）
- 不要改 `LICENSE`（GPLv3 原文须保持逐字不变）

## 代码风格

`fzp.py` 单文件，Python 3.9+，只用标准库。改动请保证
`python3 fzp.py verify` 与 `python3 fzp.py doctor` 都能正常跑。
