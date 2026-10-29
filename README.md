# fusion-zh-patch

**VMware Fusion 26H1 简体中文补全补丁**

VMware Fusion 官方只提供 English / French / Japanese / Spanish 四种语言的完整本地化，
简体中文只有半套（`zh-Hans.lproj` 里 104 张字符串表缺 16 张），代码里的文案更是完全没有
中文消息目录（`Contents/Library/messages/` 只有 es / fr / ja）。本项目把这些缺口补齐。

- 适用版本：VMware Fusion Pro 26H1（26.0.0，build 25388279），macOS 27.x
- 不修改任何可执行代码，只替换语言资源
- 无需重新签名，因此 hypervisor / device-access / 钥匙串权限原样保留

## 覆盖内容

| 层 | 位置 | 本项目 |
|---|---|---|
| `.strings` | `Resources/zh-Hans.lproj/*.strings` | 新增 21 张表，补 19 个缺失键，共 **245 条** |
| nib 字面量 | `Resources/Base.lproj/*.nib` | 修 1 处（把写死的标题改为走本地化表）|
| **`.vmsg`** | `Library/messages/zh-Hans/vmware.vmsg` | **新建，2715 条**：`msg.*` 与 `button.*` 两套前缀 |
| 法律文本 | `zh-Hans.lproj/EULA.rtf`、`Credits.html` | 中英对照（中文在上，英文原文在下），安装时生成 |

覆盖范围：设置面板全部磁贴与选项、虚拟机菜单与设备子菜单、发送键、全部对话框与按钮、
磁盘/快照/VMDB/检查点/串口/配置文件解析等运行时错误、许可证激活、组件下载进度。

**有意未翻译**：客户机操作系统名称表（`button.guest*`，属产品名）、`vmrun` 命令行输出、
`foundryErrMsgId` 内部错误码、三枚 JIS 键盘键（`変換 / 無変換 / ひらがな`，硬编码在二进制
按键表里，不在任何消息目录，要改需破坏代码签名，得不偿失）。


## 使用前

```bash
python3 fzp.py doctor     # 环境体检：版本、架构、写入权限一次看清
```

安装前做三项检查，不通过会直接中止（不改任何文件）：

| 检查 | 不通过时 |
|---|---|
| 版本为 26H1（26.0.0 / build 25388279） | 提示词条可能错位，需 `--force` 才继续 |
| 主机是否 arm64（本项目实测环境） | 非 arm64 主机 → 拒绝，需 `--force`；Intel 未经验证 |
| 能写入 `/Applications`（macOS 14+ 的「App 管理」权限）| 给出授权路径与重开终端的提示 |

**首次使用请先授权**：系统设置 → 隐私与安全性 → **App 管理** → 勾选你运行命令的终端
（Terminal / iTerm2 / VS Code / Codex）。授权后必须**完全退出该终端再重新打开**，
权限只在进程启动时读取。若列表里没有该项，先执行一次 `sudo python3 fzp.py install`
触发系统提示。

## 已验证环境

| 项目 | 值 |
|---|---|
| Fusion | 26H1，26.0.0，build 25388279（universal，含 x86_64 + arm64 切片）|
| 主机 | Apple Silicon（M5），macOS 27.2 |

**Intel Mac 未验证。** 补丁只替换语言资源、不修改任何可执行代码，理论上与架构无关，
但被修改的 nib 存在两种编译变体（`keyedobjects.nib` 与 NIBArchive 的
`keyedobjects-101300.nib`），我们只改了前者，另一份原样保留。因此：
即使资源不匹配，最坏结果也只是个别文案仍为英文，不会导致崩溃或功能异常——
但请自行承担未验证的风险，预检会要求 `--force`。

## 安装

```bash
sudo python3 fzp.py install     # 需要管理员密码；会先自动退出 Fusion
open -a "VMware Fusion"         # 消息目录在启动时加载，必须重新打开
sudo python3 fzp.py uninstall   # 回滚到安装前
python3 fzp.py status           # 查看当前安装状态
python3 fzp.py verify           # 校验 .vmsg / .strings 格式（不需管理员权限）
python3 fzp.py package          # 打包成 zip 便于分享
```

`install` 会：

1. 退出 Fusion，备份被覆盖的文件到 `backup/<时间戳>/`
2. 写入 `zh-Hans/*.strings` 与增量补丁
3. 写入 `v2/` 的附加表与 nib 补丁
4. 写入 `messages/zh-Hans/vmware.vmsg`，并把署名注入「关于」窗口文案
5. 从**本机已安装的** Fusion 读取英文 EULA，合成中英对照版；生成致谢页
6. 用 `plutil -lint` 校验所有改动过的字符串表
## 目录结构

```
fzp.py                      唯一入口：install / uninstall / status / verify / package
vmsg/vmware.vmsg            消息目录（译文的源，可直接编辑）
zh-Hans/*.strings           整表补全（21 张）
merge/*.append.strings      已有表的增量补丁（6 张）
v2/                         nib 补丁与附加表
legal/eula_zh.txt           协议中文译本（英文原文安装时从本机读取，不入库）
legal/build_legal.py        生成中英对照 EULA / Credits / 致谢
legal/apply_signature.py    署名注入（由 fzp.py 调用）
signature.txt               署名来源（第一行即显示内容）
tools/fusion-toolbar-fix.sh macOS 27 工具栏崩溃的规避开关
docs/toolbar-crash.md       该崩溃的成因与规避说明
legacy/                     早期拆分的构建脚本，仅作参考，可删
```

## 已知限制

- Fusion 升级会覆盖整个 app，补丁需要重装
- 26H1 在 macOS 27 上存在一个与本项目无关的崩溃（工具栏布局死循环），规避见 `docs/toolbar-crash.md`
- 汉化只覆盖语言资源，不改变任何功能行为

## 许可

本项目采用 **MIT**（见 [LICENSE](LICENSE)）。

选择 MIT 的理由：补丁的常见使用场景是二次修改与再分发，MIT 兼容性最好。
如果你更希望衍生作品必须保持开源，可换成 **GPL-3.0**；如果看重专利授权与商标条款，
可用 **Apache-2.0**；如果只想对译文本身要求署名与相同方式共享，可用 **CC BY-SA 4.0**
单独授权 `legal/eula_zh.txt` 与 `.vmsg` 中的译文。

## 声明

第三方本地化项目，**非 Broadcom / VMware 官方发布**。VMware Fusion 的著作权与商标归
Broadcom Inc. 及其关联公司所有。本仓库不含任何 VMware 二进制文件；EULA 英文原文不随仓库
分发，由安装脚本从用户本机读取。协议中文译本仅供参考，法律效力以英文原文为准。

中文本地化：yiqiuluoye
