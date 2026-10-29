#!/bin/bash
# VMware Fusion 26H1 (26.0.0) @ macOS 27.x —— 打开虚拟机窗口时崩溃的规避开关
#
# 原因：VM 单窗口工具栏的 NSToolbarItemViewer 在 AppKit 新布局逻辑下无限循环
#      （-layoutSubtreeIfNeeded 超过 300 次迭代），AppKit 用 _crashOnException 终止 App。
# 规避：让 VM 窗口不显示那条工具栏，功能改从菜单栏「虚拟机」菜单进入。
#
# 用法：  ./fusion-toolbar-fix.sh off      # 隐藏出问题的工具栏（修好崩溃）
#         ./fusion-toolbar-fix.sh on       # 恢复工具栏（升到修复版后再用）
#         ./fusion-toolbar-fix.sh status   # 看当前状态

KEY="NSToolbar Configuration PLVMSingleWindowToolbar2"

quit_fusion() {
  if pgrep -f "VMware Fusion.app/Contents/MacOS/VMware Fusion" >/dev/null; then
    osascript -e 'tell application "VMware Fusion" to quit' >/dev/null 2>&1
    for _ in $(seq 1 20); do
      pgrep -f "VMware Fusion.app/Contents/MacOS/VMware Fusion" >/dev/null || break
      sleep 0.5
    done
  fi
}

case "$1" in
  off)
    quit_fusion
    cp -f ~/Library/Preferences/com.vmware.fusion.plist \
          ~/Library/Preferences/com.vmware.fusion.plist.bak.$(date +%Y%m%d%H%M%S)
    defaults write com.vmware.fusion "$KEY" -dict \
      "TB Display Mode" -int 2 "TB Icon Size Mode" -int 1 "TB Is Shown" -bool false "TB Size Mode" -int 1
    echo "已隐藏 VM 窗口工具栏：$(defaults read com.vmware.fusion "$KEY" | tr -d '\n')"
    open -a "/Applications/VMware Fusion.app"
    ;;
  on)
    quit_fusion
    cp -f ~/Library/Preferences/com.vmware.fusion.plist \
          ~/Library/Preferences/com.vmware.fusion.plist.bak.$(date +%Y%m%d%H%M%S)
    defaults write com.vmware.fusion "$KEY" -dict \
      "TB Display Mode" -int 2 "TB Icon Size Mode" -int 1 "TB Is Shown" -bool true "TB Size Mode" -int 1
    echo "已恢复 VM 窗口工具栏：$(defaults read com.vmware.fusion "$KEY" | tr -d '\n')"
    open -a "/Applications/VMware Fusion.app"
    ;;
  status)
    defaults read com.vmware.fusion "$KEY" 2>/dev/null
    if defaults read com.vmware.fusion "$KEY" 2>/dev/null | grep -q 'TB Is Shown" = 0'; then
      echo "=> 工具栏已隐藏（崩溃已规避）"
    else
      echo "=> 工具栏显示中（打开 VM 窗口可能崩溃）"
    fi
    ;;
  *)
    echo "用法: $0 {off|on|status}"
    exit 1
    ;;
esac
