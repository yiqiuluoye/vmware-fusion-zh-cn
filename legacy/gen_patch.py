#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成 VMware Fusion 26H1 简体中文补全补丁。
只补 zh-Hans.lproj 中缺失的 21 个 .strings 整文件 + 6 个文件里缺的 19 条 key。
不修改任何二进制、不使用第三方汉化包。
"""
import os, re, sys

APP = "/Applications/VMware Fusion.app/Contents/Resources"
OUT = os.path.dirname(os.path.abspath(__file__))
EN = os.path.join(APP, "English.lproj")
ZH = os.path.join(APP, "zh-Hans.lproj")

PAT = re.compile(r'^"((?:[^"\\]|\\.)*)"\s*=\s*"((?:[^"\\]|\\.)*)"\s*;', re.M)


def load(p):
    b = open(p, "rb").read()
    if b[:2] in (b"\xff\xfe", b"\xfe\xff"):
        return b.decode("utf-16")
    if b[:3] == b"\xef\xbb\xbf":
        return b[3:].decode("utf-8")
    if b.count(b"\x00") > len(b) // 4:
        return b.decode("utf-16-le", errors="replace")
    return b.decode("utf-8", errors="replace")


# ---------------------------------------------------------------- 翻译表
# 说明：IB 内部占位（OtherViews / Item N / Text Cell / Button / Box / Radio /
# <<placeholder>> / *** DO NOT LOCALIZE ***）保留原文，避免影响布局与调试。
T = {
"duiNonModalAlert": {
    "8mI-8n-oXA.title": "按钮",
    "D20-Dv-STv.title": "按钮",
    "LMa-hE-N4a.title": "按钮",
    "xhu-Zc-0lV.title": "不再显示此消息",
},
"duiServerConnection": {
    "1.title": "连接",
    "14.title": "服务器：",
    "20.title": "用户名：",
    "24.title": "密码：",
    "28.title": "连接",
    "GnX-Ue-4Zz.title": "记住密码",
    "MBi-9V-U7G.title": "取消",
    "V4D-wE-Xvz.title": "正在连接服务器…",
    "Zcd-q1-e7y.title": "Item 3",
    "bhQ-Kn-wsP.title": "OtherViews",
    "e1K-ir-nnN.title": "选择要连接的远程服务器。该服务器上可以运行 VMware ESX 或 VMware vCenter Server。",
    "eX9-1v-PP5.title": "Item 2",
},
"duiSettingsViewBrowser": {
    "86.title": "系统设置",
    "98.title": "可移除设备",
    "110.title": "其他",
    "ETt-nH-9zX.ibExternalAccessibilityDescription": "更多设置项",
    "ETt-nH-9zX.ibShadowedToolTip": "更多设置项",
},
"duiSettingsViewCDROM": {
    "159.title": "此 CD/DVD 驱动器配置为使用以下内容：",
    "191.title": "OtherViews",
    "222.title": "移除 CD/DVD 驱动器",
    "230.title": "选取光盘或光盘映像…",
    "233.title": "自动检测",
    "244.title": "<<文件名>>",
    "321.title": "高级选项",
    "332.title": "OtherViews",
    "333.title": "SATA",
    "334.title": "SCSI",
    "335.title": "IDE",
    "336.title": "总线类型：",
    "A2J-Kr-Hqv.title": "远程客户端",
    "KHL-Qn-ox8.title": "选取本地光盘或光盘映像…",
    "YPg-LW-tJM.title": "打开电源时连接",
    "no9-kd-KXJ.title": "选取远程光盘映像…",
    "q7m-62-xTs.title": "连接 CD/DVD 驱动器",
},
"duiSettingsViewFloppy": {
    "159.title": "此软盘驱动器配置为使用以下内容：",
    "191.title": "OtherViews",
    "196.title": "只读",
    "222.title": "移除软盘驱动器",
    "232.title": "选取软盘映像…",
    "234.title": "<<文件名>>",
    "Ubq-uz-3CI.title": "打开电源时连接",
    "cxv-yK-nuF.title": "连接软盘驱动器",
    "dtu-ZI-aIz.title": "选取本地软盘映像…",
    "gho-5u-U0g.title": "选取远程软盘映像…",
},
"duiSettingsViewGeneral": {
    "78.title": "备注",
    "79.title": "操作系统",
    "80.title": "名称",
    "bwb-XI-lko.title": "OtherViews",
    "vTc-w6-ROQ.title": "Item 3",
    "wJF-wY-Nbr.title": "Item 1",
    "xTv-FC-EcO.title": "Item 2",
},
"duiSettingsViewHWVersionPro": {
    "296.title": "<<placeholder>>",
    "374.title": "OtherViews",
    "379.title": "使用硬件版本：",
    "394.title": "Text Cell",
    "400.title": "Text Cell",
    "402.title": "兼容产品：",
    "404.title": "限制：",
    "434.title": "高级选项",
    "443.title": "允许升级此虚拟机的虚拟硬件。",
    "445.title": "应用",
    "447.title": "还原",
    "449.title": "升级",
},
"duiSettingsViewHardDisk": {
    "227.ibShadowedToolTip": "预分配的磁盘性能更好，但会始终占用全部磁盘空间。",
    "228.ibShadowedToolTip": "拆分磁盘可以让您更轻松地把虚拟机移动到外部存储设备上。",
    "239.placeholderString": "VMDK 最大大小",
    "239.title": "GB",
    "244.title": "OtherViews",
    "245.title": "SCSI",
    "246.title": "IDE",
    "247.title": "总线类型：",
    "254.title": "应用",
    "256.title": "拆分为多个文件",
    "257.title": "预分配磁盘空间",
    "258.title": "还原",
    "262.title": "高级选项",
    "279.title": "OtherViews",
    "282.title": "存储为…",
    "284.title": "文件名：",
    "286.title": "磁盘大小：",
    "294.title": "移除硬盘",
    "360.title": "SATA",
    "dYj-gw-W6R.title": "NVMe",
},
"duiSettingsViewNetworkVIM": {
    "4Bm-46-kDw.title": "正在载入…",
    "4S3-KC-4lV.placeholderString": "01:23:45:67:89:AB",
    "8Dh-MQ-ARV.title": "连接网络适配器",
    "BUZ-fl-haF.title": "网络连接：",
    "EDb-18-USb.title": "MAC 地址：",
    "NB6-e5-5G6.title": "移除网络适配器",
    "O1X-Do-oRx.title": "打开电源时连接",
    "f5I-Ss-HvE.title": "OtherViews",
    "thg-vD-Ldt.title": "生成",
},
"duiSettingsViewParallel": {
    "159.title": "此并行端口配置为使用以下内容：",
    "222.title": "移除并行端口",
    "231.title": "OtherViews",
    "232.title": "<<文件名>>",
    "234.title": "选取文件…",
    "3qr-AF-8ht.title": "打开电源时连接",
    "AZx-Re-QS6.title": "连接并行端口",
},
"duiSettingsViewProcessorsAndRAM": {
    "65.title": "处理器",
    "85.title": "内存",
    "94.ibExternalAccessibilityDescription": "处理器选择",
    "96.title": "OtherViews",
    "102.ibExternalAccessibilityDescription": "以 MB 为单位的内存大小",
    "103.title": "12345",
    "107.title": "MB",
    "249.ibExternalAccessibilityDescription": "推荐的内存大小",
    "250.title": "99999 MB",
    "273.title": "高级选项",
    "288.title": "在此虚拟机中启用虚拟机监控程序应用程序",
    "302.title": "通过在此虚拟机中提供对 Intel VT-x/EPT 的支持，允许运行现代虚拟化应用程序。",
    "305.title": "通过在此虚拟机中提供对 CPU 性能监视计数器的支持，允许运行现代代码分析应用程序。",
    "306.title": "在此虚拟机中启用代码分析应用程序",
    "335.title": "（推荐）",
    "337.title": "您的 Mac 上剩余 99999 MB",
    "342.title": "99999 MB",
    "344.title": "99999 GB",
    "0NR-5S-tUz.title": "兼容性模式：",
    "JfU-pI-Pjc.title": "限制可用的 CPU 功能后，可以在其他主机上恢复此虚拟机的快照或挂起状态。",
    "R1X-GH-2py.title": "在此虚拟机中启用 IOMMU",
    "jia-HR-TsE.title": "启用 CPU 兼容性",
},
"duiSettingsViewSerial": {
    "159.title": "此串行端口配置为使用以下内容：",
    "222.title": "移除串行端口",
    "229.title": "OtherViews",
    "230.title": "<<文件名>>",
    "232.title": "选取文件…",
    "Vle-qe-1Qw.title": "打开电源时连接",
    "y4n-j8-7aj.title": "连接串行端口",
},
"duiSettingsViewUSBDevices": {
    "32.headerCell.title": "名称",
    "55.headerCell.title": "插入时操作",
    "68.title": "连接 USB 设备：",
    "70.title": "移除 USB 控制器",
    "72.title": "OtherViews",
    "73.title": "询问要执行的操作",
    "74.title": "连接到 Windows",
    "75.title": "连接到您的 Mac",
    "84.title": "高级 USB 选项",
    "106.title": "询问要执行的操作",
    "107.title": "连接到此虚拟机",
    "108.title": "连接到您的 Mac",
    "111.title": "OtherViews",
    "116.title": "虚拟机运行时，如果有新的 USB 设备插入您的 Mac，VMware Fusion 应该：",
    "119.title": "连接到其他虚拟机",
    "139.title": "添加 USB 控制器",
    "140.title": "您的虚拟机当前没有 USB 控制器。请添加一个 USB 控制器，才能将 USB 设备连接到虚拟机。",
    "160.title": "OtherViews",
    "161.title": "USB 1.1",
    "162.title": "USB 2.0",
    "163.title": "USB 3.2",
    "165.title": "USB 兼容性：",
    "201.title": "OtherViews",
    "202.title": "询问要执行的操作",
    "203.title": "连接到 Mac",
    "204.title": "连接到 Windows",
    "288.title": "连接到其他虚拟机",
    "uxk-wq-VgC.title": "重置所有已保存的操作",
},
"duiSettingsViewUSBDevicesVIM": {
    "32.headerCell.title": "名称",
    "68.title": "从您的 Mac 连接 USB 设备：",
    "70.title": "移除 USB 控制器",
    "84.title": "高级 USB 选项",
    "139.title": "添加 USB 控制器",
    "140.title": "您的虚拟机当前没有 USB 控制器。请添加一个 USB 控制器，才能将 USB 设备连接到虚拟机。",
    "160.title": "OtherViews",
    "161.title": "USB 1.1",
    "162.title": "USB 2.0",
    "163.title": "USB 3.2",
    "165.title": "USB 兼容性：",
},
"duiSettingsViewVTPM": {
    "g8z-be-EXm.title": "移除受信任的平台模块会销毁此虚拟机上的所有加密数据，且无法恢复。",
    "p8D-gY-Cvc.title": "移除受信任的平台模块",
},
"duiSupport": {
    "7.title": "正在收集支持信息",
    "17.title": "取消",
},
"duiUpdateWindow": {
    "1.title": "软件更新",
    "74.title": "下载并安装",
    "75.title": "跳过此版本",
    "76.title": "稍后提醒我",
    "122.title": "取消",
    "140.title": "安装并重新启动",
},
"vmCocoa": {
    "AboutWindowTitle": "关于 %@",
    "AboutWindowVersion": "版本 %@ (%@)",
    "AboutAcknowledgements": "致谢",
    "AboutLicenseAgreement": "许可协议",
    "TimeEstimateMultiHourEstimate": "约 %u 小时",
    "TimeEstimateSingleHourEstimate": "约 1 小时",
    "TimeEstimateMultiMinuteEstimate": "约 %u 分钟",
    "TimeEstimateSingleMinuteEstimate": "约 1 分钟",
    "TimeEstimateSubMinuteEstimate": "不到一分钟",
    "AssistantCancel": "取消",
    "AssistantContinue": "继续",
    "AssistantGoBack": "返回",
    "ResizeTrackingWidthLabel": "宽：",
    "ResizeTrackingHeightLabel": "高：",
    "ExportOVFValidationMsg": "文件名不能以“.%1$@”结尾，必须以“.%2$@”结尾。",
    "ExportOVFValidationText": "您可以同时使用两者，文件名将是“.%1$@.%2$@”。",
    "ExportOVFValidationFixButton": "使用 .%@",
    "ExportOVFValidationCancel": "取消",
    "ExportOVFValidationUseBoth": "两者都用",
    "ExportOVFURLValidationMsg": "导出文件名的长度不能超过 %d 个字符。",
    "ExportOVFURLValidationText": "请使用更短的文件名重试。",
},
"vmExportOvfSavePanelAccessory": {
    "Gf0-D3-cF0.title": "Radio",
    "iLU-pS-zCX.title": "导出为 OVF（含独立文件的文件夹）",
    "z5d-KV-a7L.title": "导出为 OVA（单文件归档）",
},
"vmOverwriteQuestion": {
    "42.title": "不替换",
    "44.title": "停止",
    "46.title": "替换",
    "48.title": "全部应用",
},
"vmUSBArbitratorWindowController": {
    "367.title": "VMware Fusion",
    "456.title": "请选择 %{value1}@ 的连接位置。",
    "468.title": "记住我的选择，不再询问",
    "471.title": "OtherViews",
    "472.title": "连接到您的 Mac",
    "473.title": "连接到虚拟机",
    "478.title": "好",
    "518.ibShadowedDisplayPattern": "请选择 %{value1}@ 的连接位置。",
    "520.title": "VMware Fusion",
    "528.title": "记住我的选择，不再询问",
    "533.title": "连接到 Windows",
    "535.title": "请选择 %{value1}@ 的连接位置。",
    "538.title": "连接到 Mac",
    "549.ibShadowedDisplayPattern": "请选择 %{value1}@ 的连接位置。",
    "571.title": "Button",
    "574.title": "Box",
    "577.title": "Warning text *** DO NOT LOCALIZE ***",
},
}

# 6 个「文件存在但缺 key」的补充
MERGE = {
"plVMCreationAssistantChooseEncryptionPanel": {
    "x1w-bg-q7e.title": "输入加密密码",
    "dOs-Sp-Lsf.title": "仅加密支持虚拟 TPM 所需的文件（.nvram、.vmss、\\n.vmem、.vmx、.vmsn）。",
    "tfr-PW-P5H.title": "此虚拟机的所有文件（.vmdk、.vmx 等）都将被加密。",
    "Sae-GR-xRJ.title": "密码",
    "kse-Fz-bC3.title": "验证",
    "kXw-J2-9H4.title": "生成",
    "4051.title": "密码不匹配",
    "WWf-6o-z21.title": "在 macOS 钥匙串中记住密码",
},
"plMainMenu": {
    "dXV-jn-ugI.title": "收集支持信息",
    "TM2-8f-DpP.title": "快速",
    "Lo6-ol-FLY.title": "完整",
},
"plSettingsViewGeneral": {
    "Z8V-fG-szS.title": "创建于",
    "7mj-5B-Nk3.title": "创建日期未知",
    "nGr-sh-XkV.title": "设置",
},
"plInventoryLocalInfoView": {
    "299.title": "创建于：",
    "399.title": "上次请求开机：",
},
"plSettingsViewDisplay": {
    "Njx-hx-TVI.title": "单一窗口",
    "dg3-b9-8Si.title": "全屏",
},
"plInventoryRemoteInfoView": {
    "Ysr-wD-e2x.title": "创建于：",
},
}

HEADER = "/* 由 fusion-zh-patch 生成：VMware Fusion 26H1 简体中文补全 */\n\n"


def esc(s):
    return s.replace("\\", "\\\\").replace('"', '\\"')


def emit(path, pairs):
    with open(path, "w", encoding="utf-8") as f:
        f.write(HEADER)
        for k, v in pairs:
            f.write('"%s" = "%s";\n' % (esc(k), esc(v)))


def main():
    # A. 整文件缺失 -> 生成完整 zh-Hans 文件
    n_a = 0
    for fname, tr in T.items():
        src = os.path.join(EN, fname + ".strings")
        keys = [k for k, _ in PAT.findall(load(src))]
        pairs = [(k, tr.get(k, dict(PAT.findall(load(src)))[k])) for k in keys]
        lost = [k for k, v in pairs if v == dict(PAT.findall(load(src)))[k] and k in tr and tr[k] != v]
        emit(os.path.join(OUT, "zh-Hans", fname + ".strings"), pairs)
        n_a += len(pairs)
        if lost:
            print("  ! 翻译未生效的 key:", fname, lost, file=sys.stderr)
    # B. 已有文件缺 key -> 生成待追加的补丁块
    n_b = 0
    for fname, tr in MERGE.items():
        cur = dict(PAT.findall(load(os.path.join(ZH, fname + ".strings"))))
        en_all = dict(PAT.findall(load(os.path.join(EN, fname + ".strings"))))
        pairs = [(k, v) for k, v in tr.items() if k not in cur]
        for k, v in pairs:
            if k not in en_all:
                print("  ! 补丁 key 在英文原文里不存在:", fname, k, file=sys.stderr)
        emit(os.path.join(OUT, "merge", fname + ".append.strings"), pairs)
        n_b += len(pairs)
    print("整文件补全: %d 个文件 / %d 条" % (len(T), n_a))
    print("增量补 key: %d 个文件 / %d 条" % (len(MERGE), n_b))
    print("合计 %d 条" % (n_a + n_b))


if __name__ == "__main__":
    main()
