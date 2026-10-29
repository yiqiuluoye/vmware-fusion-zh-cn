#!/bin/bash
# 双击运行：安装中文补丁（会要求输入登录密码）
cd "$(dirname "$0")" || { echo "无法进入脚本所在目录"; read -r -p "按回车退出"; exit 1; }
xattr -dr com.apple.quarantine "$(dirname "$0")" 2>/dev/null
chmod +x ./fzp.py 2>/dev/null
./fzp.py install
rc=$?
echo
if [ $rc -eq 0 ]; then echo "✅ 安装完成。请重新打开 VMware Fusion 生效。"
else echo "❌ 安装未完成（退出码 $rc）。查看上面的提示，或运行 ./fzp.py doctor"; fi
read -r -p "按回车关闭此窗口"
