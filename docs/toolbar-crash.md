# Fusion 26H1 在 macOS 27 上「打开虚拟机就崩溃」

## 现象

双击虚拟机后 VMware Fusion 整个进程退出，崩溃报告里是：

```
+[NSApplication _crashOnException:]
 └ -[NSWindow(NSDisplayCycle) _postWindowNeedsUpdateConstraints]
   └ -[NSSegmentedCell setSegmentCount:]        (VMware Fusion 自身代码)
     └ -[NSToolbarItemViewer layout]
```

系统日志（`log show --predicate 'process == "VMware Fusion"'`）里有决定性的一句：

```
Warning: -layoutSubtreeIfNeeded for <NSToolbarItemViewer> has continued for 300 iterations
because -updateConstraints and/or -layout has kept the layout or constraints dirty.
```

## 原因

虚拟机单窗口工具栏里的分段控件，在 macOS 27 的 `NSToolbarItemViewer` 尺寸计算下不断
把约束标记为脏，超过 AppKit 的 300 次迭代上限后 AppKit 主动终止进程。

这是 Fusion 26H1 与 macOS 27 的兼容问题，与本汉化补丁无关；26H1u1 的官方 Release Notes
里也没有相关修复。

## 规避

隐藏出问题的那条工具栏（功能改从菜单栏「虚拟机」进入）：

```bash
sudo ./tools/fusion-toolbar-fix.sh off    # 规避崩溃
sudo ./tools/fusion-toolbar-fix.sh on     # 恢复工具栏（等官方修复后用）
./tools/fusion-toolbar-fix.sh status      # 查看当前状态
```

原理：把 `com.vmware.fusion` 偏好里的
`NSToolbar Configuration PLVMSingleWindowToolbar2` 设为 `TB Is Shown = 0`。
改动前会自动备份 `~/Library/Preferences/com.vmware.fusion.plist`。
