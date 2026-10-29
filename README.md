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

## 安装

```bash
sudo ./install.sh      # 需要管理员密码；会先自动退出 Fusion
open -a "VMware Fusion"
sudo ./uninstall.sh    # 回滚
```

`install.sh` 会：

1. 备份被覆盖的文件到 `backup/<时间戳>/`
2. 写入 `zh-Hans/*.strings` 与增量补丁
3. 写入 `messages/zh-Hans/vmware.vmsg`
4. 从**本机已安装的** Fusion 读取英文 EULA 原文，与 `legal/eula_zh.txt` 合成中英对照版
5. 用 `plutil -lint` 校验所有改动过的字符串表

## 目录结构

```
install.sh / uninstall.sh   安装与回滚
gen_patch.py                生成 .strings 补丁（v1）
gen_patch_v2.py             生成 nib 补丁与附加表（v2）
gen_vmsg.py                 合成 .vmsg（读取 translations_v*.py）
translations_v4..v12.py     中文词条（按批次组织）
vmsg/vmware.vmsg            生成物，安装时写入 app
zh-Hans/  merge/  v2/       生成物
legal/eula_zh.txt           协议中文译本（英文原文安装时从 app 读取，不入库）
legal/build_legal.py        生成中英对照 EULA / Credits
signature.txt               署名来源
tools/fusion-toolbar-fix.sh macOS 27 工具栏崩溃的规避开关
docs/toolbar-crash.md       该崩溃的成因与规避说明
NOTICE.md                   声明与共享说明
```

## 维护

```bash
python3 gen_patch.py && python3 gen_patch_v2.py && python3 gen_vmsg.py
```

`.vmsg` 格式注意：换行写作 `|0A`，双引号写作 `|22`，百分号写作 `%%`，
多参数使用 `%1$s %2$s` 编号占位符。缺键会自动回退到内置英文，可安全增量维护。

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
