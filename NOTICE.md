# 署名与声明 NOTICE

**VMware Fusion 26H1 简体中文补全补丁包（vmware-fusion-zh-cn）**

- 中文本地化：**yiqiuluoye**
- 适用版本：VMware Fusion Pro 26H1（26.0.0，build 25388279），macOS 27.x
- 制作方式：本地资源级本地化，不修改任何可执行代码、不替换界面 xib/nib 结构
- 许可证：GNU GPL v3.0（见 LICENSE；中文对照见 LICENSE.zh-CN.md）
- 版权：Copyright (C) 2026 yiqiuluoye

## 声明

1. 本汉化包为**第三方本地化**，非 Broadcom / VMware 官方发布，未获其背书。
2. VMware Fusion 的著作权、商标及一切知识产权归 **Broadcom Inc.** 及其关联公司所有。
3. 本包仅包含语言资源（`.strings`、`.vmsg`、`EULA.rtf`、`Credits.html`），
   不含、也不再分发任何 VMware 二进制文件。
4. `EULA.rtf` 与 `Credits.html` 采用「中文在上、英文原文在下」的中英对照形式：
   **中文为参考译本，法律效力以英文原文为准**。协议文本本身未作任何删改。
5. 使用本包造成的任何后果由使用者自行承担；请自行确认符合您所在地的法律与许可条款。

## 共享说明

把整个目录（本仓库）打包分享即可（不含 `backup/` 更干净）：

```bash
cd ~/Documents/deepseek-harness/default-workspace
zip -r vmware-fusion-zh-cn-$(date +%Y%m%d).zip fusion-zh-patch \
    -x 'fusion-zh-patch/backup/*' -x '*/__pycache__/*'
```

接收方解压后执行 `sudo ./install.sh` 即可；`sudo ./uninstall.sh` 回滚。

署名文字集中在一个文件：**`signature.txt`**。改这个文件后重装，
署名会更新到「关于 VMware Fusion → 致谢」页面底部。
