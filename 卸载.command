#!/bin/bash
# 双击运行：还原到安装前的状态
cd "$(dirname "$0")" || exit 1
xattr -dr com.apple.quarantine "$(dirname "$0")" 2>/dev/null
chmod +x ./fzp.py 2>/dev/null
./fzp.py uninstall
rc=$?
echo
[ $rc -eq 0 ] && echo "✅ 已还原。请重新打开 VMware Fusion。" || echo "❌ 还原失败（退出码 $rc）"
read -r -p "按回车关闭此窗口"
