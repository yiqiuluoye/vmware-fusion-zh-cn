#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成 Contents/Library/messages/zh-Hans/vmware.vmsg
Fusion 的代码文案走 VMware 自己的消息目录（.vmsg），官方只带 es/fr/ja，
没有 zh-Hans —— 所以设置窗口磁贴、虚拟机菜单这些永远是英文。
本脚本按二进制里实际的 msg.* 键补中文；缺的键会自动回退内置英文，安全。
注意 vmsg 转义：双引号写成 |22，百分号写成 %% 。
"""
import os

OUT = os.path.dirname(os.path.abspath(__file__))

T = {
# ---------- 设置窗口：分组 ----------
"msg.dui.settings.removableDevices": "可移除设备",
"msg.dui.settings.windowTitleFormat": "%s：%s",
"msg.dui.settings.nic.unknown": "未知",
"msg.dui.settings.nic.unavailableVMNet": "不可用 (%s)",
"msg.dui.settings.nic.warning.unavailableVMNet": "找不到所选的网络。",
"msg.dui.settings.confirmGuestOSChange": "更改",
"msg.dui.settings.confirmGuestOSDontChange": "不更改",

# ---------- 设置窗口：面板名 ----------
"msg.fusion.settings.browser.name": "设置",
"msg.fusion.settings.browser.browserName": "设置",
"msg.fusion.settings.general.name": "通用",
"msg.fusion.settings.general.browserName": "通用",
"msg.fusion.settings.keyboardAndMouse.name": "键盘和鼠标",
"msg.fusion.settings.keyboardAndMouse.browserName": "键盘和鼠标",
"msg.fusion.settings.processorsAndMemory.name": "处理器和内存",
"msg.fusion.settings.processorsAndMemory.browserName": "处理器和内存",
"msg.fusion.settings.usb.name": "USB",
"msg.fusion.settings.USBDevices.name": "USB",
"msg.fusion.settings.USBDevices.browserName": "USB",
"msg.fusion.settings.USBOnly.name": "USB",
"msg.fusion.settings.USBOnly.browserName": "USB",
"msg.fusion.settings.startup.name": "启动磁盘",
"msg.fusion.settings.startup.browserName": "启动磁盘",
"msg.fusion.settings.encryption.name": "加密",
"msg.fusion.settings.encryption.browserName": "加密",
"msg.fusion.settings.compatibility.name": "兼容性",
"msg.fusion.settings.compatibility.browserName": "兼容性",
"msg.fusion.settings.Isolation.name": "隔离",
"msg.fusion.settings.Isolation.browserName": "隔离",
"msg.fusion.settings.advanced.name": "高级",
"msg.fusion.settings.advanced.browserName": "高级",
"msg.fusion.settings.sharing.name": "共享",
"msg.fusion.settings.sharing.browserName": "共享",
"msg.fusion.settings.snapshot.image": "快照",
"msg.fusion.settings.snapshotWithValue": "快照 %s",
"msg.fusion.settings.harddisk.image": "硬盘",
"msg.fusion.settings.hardDiskWithValue": "硬盘 %s",
"msg.fusion.settings.reclaimable.image": "可回收",
"msg.fusion.settings.reclaimableWithValue": "可回收 %s",
"msg.fusion.settings.totalSize": "总大小：%s",
"msg.fusion.settings.notAvailable": "不适用",
"msg.fusion.settings.unsupportedBackend": "不支持的自定义设置",
"msg.fusion.settings.featurecompat.unsupported": "不支持的模式",

# ---------- 设置窗口：添加设备 ----------
"msg.fusion.settings.add.name": "添加设备",
"msg.fusion.settings.add.browserName": "添加设备",
"msg.fusion.settings.add.cd": "CD/DVD 驱动器",
"msg.fusion.settings.add.existingHD": "现有硬盘",
"msg.fusion.settings.add.newHD": "新硬盘",
"msg.fusion.settings.add.floppy": "软盘驱动器",
"msg.fusion.settings.add.network": "网络适配器",
"msg.fusion.settings.add.parallel": "并行端口",
"msg.fusion.settings.add.serial": "串行端口",
"msg.fusion.settings.add.sound": "声卡",
"msg.fusion.settings.add.vtpm": "受信任的平台模块",
"msg.fusion.settings.add.vusbcamera": "摄像头",
"msg.fusion.settings.add.hd.linkedClone": "链接克隆无法添加硬盘。",
"msg.fusion.settings.add.sonud.alreadyHave": "该虚拟机已有声卡。",
"msg.fusion.settings.add.vtpm.alreadyHave": "该虚拟机已有受信任的平台模块。",

# ---------- 设置窗口：提示与确认 ----------
"msg.fusion.settings.closeError.message": "无法关闭设置。",
"msg.fusion.settings.addDevice.closeError.message": "无法关闭设置。",
"msg.fusion.settings.network.closeError.message": "无法关闭设置。",
"msg.fusion.settings.cdrom.remove.messageText": "确定要移除 CD/DVD 驱动器吗？",
"msg.fusion.settings.floppy.remove.messageText": "确定要移除软盘驱动器吗？",
"msg.fusion.settings.hd.remove.messageText": "确定要移除硬盘吗？",
"msg.fusion.settings.nic.remove.messageText": "确定要移除网络适配器吗？",
"msg.fusion.settings.parallel.remove.messageText": "确定要移除并行端口吗？",
"msg.fusion.settings.serial.remove.messageText": "确定要移除串行端口吗？",
"msg.fusion.settings.sound.remove.messageText": "确定要移除声卡吗？",
"msg.fusion.settings.usbController.remove.messageText": "确定要移除 USB 控制器吗？",
"msg.fusion.settings.vusbcamera.remove.messageText": "确定要移除摄像头吗？",
"msg.fusion.settings.floppy.openPanelMessage": "选取软盘映像文件。",
"msg.fusion.settings.serial.savePanelMessage": "创建文件以保存虚拟串行端口的输出。",
"msg.fusion.settings.hd.defaultName": "虚拟磁盘",
"msg.fusion.settings.hd.DiskSize": "磁盘大小",
"msg.fusion.settings.hd.saveInProgress": "正在存储",
"msg.fusion.settings.hd.warning.bootCamp": "Boot Camp 磁盘无法更改硬盘设置。",
"msg.fusion.settings.hd.warning.fileMissing": "虚拟磁盘文件缺失。",
"msg.fusion.settings.hd.warning.linkClone": "链接克隆无法更改硬盘设置。",
"msg.fusion.settings.hd.applyAlertNew.infoText": "新磁盘尚未添加。",
"msg.fusion.settings.hd.partitionResize.messageText": "虚拟磁盘已调整大小。",
"msg.fusion.settings.display.customMemory": "自定义：%u MB",
"msg.fusion.settings.display.memoryDefaultFormat": "%u MB（推荐）",
"msg.fusion.settings.display.memoryFormat": "%u MB",
"msg.fusion.settings.display.accel3d.winxp": "支持 DirectX 9.0c（Shader Model 3）和 OpenGL 2.1",
"msg.fusion.settings.display.warning.kb": "VMware 知识库",
"msg.fusion.settings.display.warning.period": "。",
"msg.fusion.settings.nic.autodetect": "自动检测",
"msg.fusion.settings.nic.custom": "自定义",
"msg.fusion.settings.nic.hostOnly": "仅主机",
"msg.fusion.settings.nic.nat": "NAT",
"msg.fusion.settings.nic.loading": "正在载入…",
"msg.fusion.settings.nic.networkType.custom": "自定义",
"msg.fusion.settings.usb.connectToMac": "连接到 Mac",
"msg.fusion.settings.usb.connectToOtherVM": "连接到其他虚拟机",
"msg.fusion.settings.usb.unknownDevice": "未知设备",
"msg.fusion.settings.vusbcamera.defaultcamera": "默认摄像头",
"msg.fusion.settings.sound.warning.remote.notSupported": "远程连接不支持声音。",
"msg.fusion.settings.profile.disabled": "已禁用",
"msg.fusion.settings.profile.enabled": "已启用",
"msg.fusion.settings.profile.mac": "Mac",
"msg.fusion.settings.profile.macDefault": "Mac（默认）",
"msg.fusion.settings.profile.standard": "标准",
"msg.fusion.settings.profile.standardDefault": "标准（默认）",
"msg.fusion.settings.profile.windows8": "Windows 8",
"msg.fusion.settings.profile.windows8Default": "Windows 8（默认）",
"msg.fusion.settings.profile.windows10": "Windows 10",
"msg.fusion.settings.profile.windows10Default": "Windows 10（默认）",
"msg.fusion.settings.sharing.changedFolders.infoText": "当前更改将被丢弃。",
"msg.fusion.settings.sharing.saveInProgress": "正在存储",
"msg.fusion.settings.encryptSuccess.message": "已添加加密",
"msg.fusion.settings.decryptSuccess.message": "已移除加密",
"msg.fusion.settings.reencryptSuccess.message": "加密模式已升级。",
"msg.fusion.settings.desc.invalid": "描述无效。",
"msg.fusion.settings.desc.invalid.description": "描述必须少于 127 个字符。",
"msg.fusion.settings.diskSize.outOfRange": "磁盘大小无效。",
"msg.fusion.settings.diskSize.outOfRange.description": "磁盘大小必须介于 %.2f 和 %.2f GB 之间。",
"msg.fusion.settings.memory.outOfRange": "内存大小无效。",
"msg.fusion.settings.memory.outOfRange.description": "内存大小必须介于 %d 和 %d MB 之间。",
"msg.fusion.settings.bandwidth.outOfRange": "网络带宽无效。",
"msg.fusion.settings.bandwidth.outOfRange.description": "带宽必须介于 0 和 10 Gbps 之间。",
"msg.fusion.settings.networkLatency.outOfRange": "网络延迟无效。",
"msg.fusion.settings.packetloss.outOfRange": "网络丢包率无效。",
"msg.fusion.settings.packetloss.outOfRange.description": "有效丢包范围为 0 - 100%%。",
"msg.fusion.settings.ip.invalid": "IP 地址无效。",
"msg.fusion.settings.port.occupied": "主机端口无效。",
"msg.fusion.settings.port.outOfRange": "端口号无效。",
"msg.fusion.settings.port.outOfRange.description": "有效端口范围为 1 - 65535。",
"msg.fusion.settings.insufficientSpaceForCopy.title": "空间不足，无法复制。",
"msg.fusion.settings.vncPasswordNotAscii.title": "密码只能包含 ASCII 字符。",
"msg.fusion.settings.vncPasswordTooLong.title": "输入的密码过长。",
"msg.fusion.settings.vncPortOutOfRangeTitle": "输入的端口超出范围。",
"msg.fusion.settings.vncPortOutOfRangeBody": "端口必须介于 1024 到 65535 之间。",

# ---------- 菜单 / 动作 ----------
"msg.fusion.menuItem.settings": "设置…",
"msg.fusion.menuItem.getInfo": "获取信息…",
"msg.fusion.menuItem.showSnapshots": "快照…",
"msg.fusion.menuItem.takeSnapshot": "拍摄快照",
"msg.fusion.menuItem.revertToSnapshot": "恢复快照…",
"msg.fusion.menuItem.fullClone": "创建完整克隆…",
"msg.fusion.menuItem.linkedClone": "创建链接克隆…",
"msg.fusion.menuItem.export": "导出…",
"msg.fusion.menuItem.exportToOVF": "导出为 OVF…",
"msg.fusion.menuItem.exportToTAR": "导出为 TAR…",
"msg.fusion.menuItem.showWindows": "显示窗口",
"msg.fusion.menu.License": "许可证…",
"msg.fusion.menu.buyNowOrLicense": "输入许可证…",
"msg.fusion.menu.autodetect": "自动检测",
"msg.fusion.menu.chooseDiscOrImage": "选取光盘或光盘映像…",
"msg.fusion.menu.networkDevice.default": "默认",
"msg.fusion.menu.upgradeNow": "立即升级…",

# ---------- 电源状态 / 菜单项 ----------
"msg.dui.menuItem.offPowerStatus.windows": "Windows 已关闭",
"msg.dui.menuItem.offPowerStatus.linux": "Linux 已关闭",
"msg.dui.menuItem.offPowerStatus.macOS": "Mac OS 已关闭",
"msg.dui.menuItem.offPowerStatus.other": "虚拟机已关闭",
"msg.dui.menuItem.onPowerStatus.windows": "Windows 正在运行",
"msg.dui.menuItem.onPowerStatus.linux": "Linux 正在运行",
"msg.dui.menuItem.onPowerStatus.macOS": "Mac OS 正在运行",
"msg.dui.menuItem.onPowerStatus.other": "虚拟机正在运行",
"msg.dui.menuItem.pausedStatus.windows": "Windows 已暂停",
"msg.dui.menuItem.pausedStatus.linux": "Linux 已暂停",
"msg.dui.menuItem.pausedStatus.macOS": "Mac OS 已暂停",
"msg.dui.menuItem.pausedStatus.other": "虚拟机已暂停",
"msg.dui.menuItem.suspendedPowerStatus.windows": "Windows 已挂起",
"msg.dui.menuItem.suspendedPowerStatus.linux": "Linux 已挂起",
"msg.dui.menuItem.suspendedPowerStatus.macOS": "Mac OS 已挂起",
"msg.dui.menuItem.suspendedPowerStatus.other": "虚拟机已挂起",
"msg.dui.menuItem.pause": "暂停",
"msg.dui.menuItem.unpause": "继续",
"msg.dui.menuItem.sendCtrlAltDel": "发送 Ctrl-Alt-Del",
"msg.dui.menuItem.enterFullscreen": "进入全屏",
"msg.dui.menuItem.exitFullscreen": "退出全屏",
"msg.dui.menuItem.fullScreen": "全屏",
"msg.dui.menuItem.singleWindow": "单一窗口",
"msg.dui.menuItem.forceFitGuest": "调整虚拟机大小以适应",
"msg.dui.menuItem.toolsInstallStarting": "正在开始安装 VMware Tools",
"msg.dui.menuItem.toolsInstallStopping": "正在停止安装 VMware Tools",
"msg.dui.menuItem.cancelInstallTools": "取消 VMware Tools 安装",
"msg.dui.menu.installTools": "安装 VMware Tools",
"msg.dui.menu.reinstallTools": "重新安装 VMware Tools",
"msg.dui.menu.updateTools": "更新 VMware Tools",
"msg.dui.menu.toolsUnavailable": "VMware Tools 不可用",
"msg.dui.menu.view.useAllDisplaysInFullScreen": "全屏时使用所有显示器",
"msg.dui.menu.view.useSingleDisplayInFullScreen": "全屏时使用单个显示器",
"msg.dui.action.ctrlAltDel.tooltip": "发送 Ctrl-Alt-Delete 组合键。",
"msg.dui.action.pause.tooltip": "暂停此虚拟机。",
"msg.dui.action.unpause.tooltip": "继续运行此虚拟机。",
"msg.dui.action.singlewindow.tooltip": "在单一窗口中查看虚拟机。",
"msg.dui.palette.pauseUnpause": "暂停 / 继续",
"msg.dui.palette.powerOnAndOff": "%s / %s",
"msg.dui.palette.powerOnAndOffAndSuspend": "%s / %s",
"msg.dui.label.power.poweredOff.sentenceCase": "已关闭",
"msg.dui.label.power.poweredOn.sentenceCase": "已开机",
"msg.dui.label.power.suspended.sentenceCase": "已挂起",
"msg.dui.label.power.startingSoft.titleCase": "正在开机…",
"msg.dui.label.power.stoppingSoft.titleCase": "正在关机…",
"msg.dui.label.power.resumingSoft.titleCase": "正在恢复…",

# ---------- 快照 ----------
"msg.dui.snapshot.currentState": "当前状态",
"msg.dui.snapshot.namePrefix": "快照",
"msg.dui.snapshot.restoreProgress": "正在恢复快照…",
"msg.dui.snapshot.restoreWarning": "VMware Fusion 现在将恢复“%s”快照。",
"msg.fusion.snapshots.windowTitle": "快照",
"msg.fusion.snapshot.closeError.message": "无法关闭快照。",
"msg.fusion.snapshot.deleteSingle": "确定要删除快照“%s”吗？",
"msg.fusion.snapshot.deleteMultiple": "确定要删除 %d 个快照吗？",
"msg.fusion.snapshot.fileSizeSnapshot": "文件大小：%s",
"msg.fusion.snapshot.fullClonePrefix": "%s 的克隆",
"msg.fusion.snapshot.linkedClonePrefix": "%s 的链接克隆",
"msg.fusion.snapshot.interval1Day": "1 天",
"msg.fusion.snapshot.interval1Hour": "1 小时",
"msg.fusion.snapshot.interval30Minutes": "30 分钟",
"msg.fusion.snapshot.intervalCustom": "自定义",
"msg.fusion.snapshot.autoProtect.SetValueErrorDesc": "该值必须是 1 到 100 之间的数字。",
"msg.fusion.snapshots.alert.noName": "没有快照名称",
"msg.fusion.snapshots.alert.noNameInfo": "快照名称不能为空。",
"msg.fusion.snapshots.nextAutoSaveName": "下一个自动保护快照",
"msg.fusion.snapshots.remoteCountLabelSingular": "1 个快照",
"msg.fusion.snapshots.remoteCountLabelPlural": "%d 个快照",
"msg.fusion.snapshots.remoteSizeAndCountSelectedLabel": "已选 %lu / %d",
"msg.fusion.snapshots.sizeAndCountLabelSingular": "1 个快照，已用 %s",
"msg.fusion.snapshots.sizeAndCountLabelPlural": "%d 个快照，已用 %s",
"msg.fusion.snapshots.sizeAndCountSelectedLabel": "已选 %lu / %d，已用 %s",

# ---------- 虚拟机库 / 状态 ----------
"msg.fusion.inventoryNode.state.poweredOff": "已关闭",
"msg.fusion.inventoryNode.state.running": "正在运行",
"msg.fusion.inventoryNode.state.suspended": "已挂起",
"msg.fusion.inventoryNode.state.loading": "正在载入…",
"msg.fusion.inventoryNode.state.locked": "已锁定",
"msg.fusion.inventoryNode.state.invalid": "无效",
"msg.fusion.inventoryNode.state.inaccessible": "无法访问",
"msg.fusion.inventoryNode.state.notFound": "未找到",
"msg.fusion.inventoryNode.state.orphaned": "孤立",
"msg.fusion.inventoryNode.state.pending": "待处理",
"msg.fusion.inventoryNode.state.disconnected": "已断开连接",
"msg.fusion.inventoryNode.state.notResponding": "无响应",
"msg.fusion.inventoryNode.state.maintenanceMode": "维护模式",
"msg.fusion.inventoryNode.info.connectionType": "连接类型：",
"msg.fusion.inventoryNode.info.ipv4address": "IPv4 地址：",
"msg.fusion.inventoryNode.info.ipv6address": "IPv6 地址：",
"msg.fusion.inventoryNode.info.macAddress": "MAC 地址：",
"msg.fusion.inventoryNode.info.cloneTooltip": "此虚拟机的链接克隆",
"msg.fusion.inventoryNode.infoString": "%s - %s 的链接克隆",
"msg.fusion.inventoryNode.notes.placeholder": "在此添加备注",

# ---------- 网络子菜单 ----------
"msg.menubar.networkSubMenu.bridgedAutodetect": "桥接（自动检测）",
"msg.menubar.networkSubMenu.bridgedCustom": "桥接（%s）",
"msg.menubar.networkSubMenu.bridgedCustomUnknown": "桥接（自定义）",
"msg.menubar.networkSubMenu.customUnknown": "自定义",
"msg.menubar.networkSubMenu.customVMNet": "自定义（%s）",
"msg.menubar.networkSubMenu.hostOnly": "仅主机",
"msg.menubar.networkSubMenu.nat": "NAT",

# ---------- USB 设备提示 ----------
"msg.dui.vmmenu.device.tooltip.usb.connect": "将“%s”连接到此虚拟机。",
"msg.dui.vmmenu.device.tooltip.usb.disconnect": "断开“%s”与此虚拟机的连接。",

# ---------- Touch Bar ----------
"msg.fusion.touchbar.powerOpsItem": "开机 / 挂起",
"msg.fusion.touchbar.shutDownOpsItem": "关机",
"msg.fusion.touchbar.pauseOpsItem": "暂停 / 继续",
"msg.fusion.touchbar.settingsOpItem": "设置",
"msg.fusion.touchbar.snapshotsOpsItem": "快照",
"msg.fusion.touchbar.takesnapshotOpsItem": "拍摄快照",
"msg.fusion.touchbar.revertsnapshotOpsItem": "恢复快照",
"msg.fusion.touchbar.ctrlAltDelOpItem": "发送 Ctrl-Alt-Del",
"msg.fusion.touchbar.backToLibraryOpsItem": "返回资源库",
"msg.fusion.touchbar.vmscrubberitem": "虚拟机列表",
"msg.fusion.touchbar.zoomOpsItem": "进入 / 退出全屏",
"msg.fusion.touchbar.prtScnOpItem": "Print Screen",
"msg.fusion.touchbar.popoverFnsItem": "Fn",
}



# ---------- 设备名（设置窗口磁贴的实际来源）----------
EXTRA = {
"msg.cui.vmdevice.CPU.name": "处理器",
"msg.cui.vmdevice.memory.name": "内存",
"msg.cui.vmdevice.SVGA.name": "显示器",
"msg.cui.vmdevice.NIC.name": "网络适配器",
"msg.cui.vmdevice.harddisk.name": "硬盘 (%s)",
"msg.cui.vmdevice.harddisk.names": "硬盘 %d (%s)",
"msg.cui.vmdevice.cdrom.name": "CD/DVD (%s)",
"msg.cui.vmdevice.cdrom.names": "CD/DVD %d (%s)",
"msg.cui.vmdevice.sound.name": "声卡",
"msg.cui.vmdevice.vusbCamera.name": "摄像头",
"msg.cui.vmdevice.VTPM.name": "受信任的平台模块",
"msg.cui.vmdevice.Floppy.name": "软盘",
"msg.cui.vmdevice.Floppy.nameNumbered": "软盘 %d",
"msg.cui.vmdevice.Parallel.name": "并行端口",
"msg.cui.vmdevice.Parallel.nameNumbered": "并行端口 %d",
"msg.cui.vmdevice.Serial.name": "串行端口",
"msg.cui.vmdevice.Serial.nameNumbered": "串行端口 %d",
"msg.cui.vmdevice.USBCtlr.name": "USB 控制器",
"msg.cui.vmdevice.USBDevice.name": "USB 设备",
"msg.cui.vmdevice.XHCICtlr.name": "USB 3.2 控制器",
"msg.cui.vmdevice.IDECtlr.name": "IDE 控制器 %d",
"msg.cui.vmdevice.SATACtlr.name": "SATA 控制器 %d",
"msg.cui.vmdevice.SCSICtlr.name": "SCSI 控制器 %d",
"msg.cui.vmdevice.NVMeCtlr.name": "NVMe 控制器 %d",
"msg.cui.vmdevice.genericSCSI.name": "通用 SCSI (SCSI %d:%d)",
"msg.cui.vmdevice.VMCI.name": "VMCI",
"msg.cui.deviceMgr.cdDVD": "CD/DVD",
"msg.cui.deviceMgr.floppy": "软盘",
"msg.cui.deviceMgr.parallel": "并行端口",
"msg.cui.deviceMgr.serial": "串行端口",
"msg.cui.deviceMgr.usb": "USB 控制器",
"msg.cui.deviceMgr.audio": "声卡",
"msg.usb.genericName": "USB 设备",
"msg.usb.anonymousDevice": "USB 设备 %04x:%04x",
}
T.update(EXTRA)



# ---------- 第二批：各设置面板正文 / 电源菜单 / 高级选项 ----------
BATCH3 = {
"msg.cui.vm.shortLabel.powerOn.soft": "开机",
"msg.cui.vm.shortLabel.powerOff.soft": "关机",
"msg.cui.vm.shortLabel.powerOn.hard": "打开电源",
"msg.cui.vm.shortLabel.powerOff.hard": "关闭电源",
"msg.cui.vm.shortLabel.reset.soft": "重新启动",
"msg.cui.vm.shortLabel.reset.hard": "重置",
"msg.cui.vm.shortLabel.suspend": "挂起",
"msg.cui.vm.shortLabel.resume": "恢复",

"msg.fusion.arm.settings.display.accel3d.dx11": "支持 DirectX 11",
"msg.fusion.settings.display.warning.vulkanWin7": "如果您的 Windows 虚拟机安装了随图形驱动程序一起安装的 Vulkan 运行时库，某些 3D 应用程序可能无法在虚拟机中运行。解决方法请参阅",

"msg.fusion.setting.cpu.oneCore": "%3d  个处理器核心",
"msg.fusion.setting.cpu.supportedOfCores": "%3d  个处理器核心",
"msg.fusion.setting.cpu.otherCores": "其他：%3d  个处理器核心",
"msg.fusion.memory.memoryLeft": "您的 Mac 上剩余 %d MB",

"msg.fusion.setting.network.internetSharingTitle": "互联网共享",
"msg.fusion.setting.network.shareWithMacTitle": "与我的 Mac 共享",
"msg.fusion.setting.network.bridgedNetworkingTitle": "桥接网络",
"msg.fusion.setting.network.privateTitle": "我的 Mac 专用",
"msg.fusion.setting.network.autodetectTitle": "自动检测",
"msg.fusion.setting.network.NAT_Info": "此虚拟机与 Mac 共享外部网络上的同一 IP 地址。Mac 会为来自该虚拟机的网络流量提供网络地址转换 (NAT)。",

"msg.fusion.device.usbDevice.warnings.powerNotOn": "虚拟机开机后才能连接 USB 设备。",
"msg.fusion.encrypt.vtpm": "存在虚拟 TPM 设备时无法移除加密。请先移除 vTPM 再继续。",
"msg.fusion.hardwareVersion.upToDateDesc": "此虚拟机使用硬件版本 %d。该版本可提供 VMware Fusion 中最佳的性能和功能。",
"msg.fusion.settings.advanced.firmware.warning.vtpm": "在移除此虚拟机的“受信任的平台模块”之前，无法更改“固件类型”设置。",

"msg.fusion.setting.syncTime.description": "同步时间",
"msg.fusion.setting.virtualBattery.description": "将电源状态传递给虚拟机",
"msg.fusion.setting.monitorType.description": "疑难解答",
"msg.fusion.setting.hardDiskBuffer.description": "硬盘缓冲",
"msg.fusion.setting.vncEnabled.description": "通过 VNC 远程显示",
"msg.fusion.setting.vncPassword.description": "密码（推荐）",
"msg.fusion.setting.vncPort.description": "端口",
"msg.fusion.setting.powerOptions.description": "电源选项",
"msg.fusion.setting.verboseUSBLogging.description": "启用详细 USB 调试",
"msg.fusion.setting.firmwareType.description": "固件类型",
"msg.fusion.setting.secureBoot.description": "启用 UEFI 安全启动",
"msg.fusion.setting.darkModeSync.description": "启用深色模式同步",

"msg.dui.vmEditable.monitorType.default": "默认",
"msg.dui.vmEditable.hostDiskBuffer.automatic": "自动",
"msg.dui.vmEditable.firmwareType.uefi": "UEFI",
}
T.update(BATCH3)

try:
    from translations_v4 import D4
    T.update(D4)
    from translations_v5 import D5
    T.update(D5)
    from translations_v6 import D6
    T.update(D6)
    from translations_v7 import D7
    T.update(D7)
    from translations_v8 import D8
    T.update(D8)
    from translations_v9 import D9
    T.update(D9)
    from translations_v10 import D10
    T.update(D10)
    from translations_v11 import D11
    T.update(D11)
    from translations_v12 import D12
    T.update(D12)
except ImportError:
    pass


def main():
    d = os.path.join(OUT, "vmsg")
    os.makedirs(d, exist_ok=True)
    path = os.path.join(d, "vmware.vmsg")
    with open(path, "w", encoding="utf-8") as f:
        for k in sorted(T):
            v = T[k].replace('"', "|22")
            f.write('%s = "%s"\n' % (k, v))
    print("生成 %s，共 %d 条" % (path, len(T)))


if __name__ == "__main__":
    main()
