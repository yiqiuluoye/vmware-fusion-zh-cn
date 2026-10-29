#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""补丁 v2：补「设置窗口」里那些不在 .strings 中的文案。
   ① 磁贴标题（General / Processors & Memory / Network Adapter …）—— 代码里写死，
      但 Fusion 会按表名 duiSettingsViewBrowser / Localizable 查，所以两张表都喂。
   ② 设置窗口标题的 ": Settings" 后缀。
   ③ 修 Base.lproj/duiSettingsViewBrowser.nib 里一个「写的是字面量而不是 key」
      的分组标题（第二组 Removable Devices 一直英文就是因为这个）。
"""
import os, plistlib, shutil

APP = "/Applications/VMware Fusion.app/Contents/Resources"
OUT = os.path.dirname(os.path.abspath(__file__))
ZH = os.path.join(APP, "zh-Hans.lproj")
BASE = os.path.join(APP, "Base.lproj")

# 磁贴标题 + 分组标题 + 窗口标题
TILES = {
    "General": "通用",
    "Keyboard & Mouse": "键盘和鼠标",
    "Processors & Memory": "处理器和内存",
    "Display": "显示器",
    "Network Adapter": "网络适配器",
    "Hard Disk (NVMe)": "硬盘 (NVMe)",
    "CD/DVD (SATA)": "CD/DVD (SATA)",
    "Sound Card": "声卡",
    "USB": "USB",
    "Camera": "摄像头",
    "Trusted Platform Module": "受信任的平台模块",
    "Startup Disk": "启动磁盘",
    "Encryption": "加密",
    "Compatibility": "兼容性",
    "Isolation": "隔离",
    "Advanced": "高级",
    "System Settings": "系统设置",
    "Removable Devices": "可移除设备",
    "Other": "其他",
    "Settings": "设置",
    "%@: Settings": "%@：设置",
    "Show All": "显示全部",
    "Add Device...": "添加设备…",
}


def write_utf8(path, pairs, header):
    with open(path, "w", encoding="utf-8") as f:
        f.write("/* %s */\n\n" % header)
        for k, v in pairs.items():
            f.write('"%s" = "%s";\n' % (k.replace('"', '\\"'), v.replace('"', '\\"')))


def gen_tables():
    d = os.path.join(OUT, "v2")
    os.makedirs(d, exist_ok=True)
    write_utf8(os.path.join(d, "Localizable.strings"), TILES,
               "fusion-zh-patch v2：默认表（Localizable）")
    write_utf8(os.path.join(d, "duiSettingsViewBrowser.extra.strings"), TILES,
               "fusion-zh-patch v2：并入 duiSettingsViewBrowser 表")
    return d


def gen_nib():
    """把写死字面量的分组标题改成 key，使其能走本地化表。"""
    src = os.path.join(BASE, "duiSettingsViewBrowser.nib")
    dst = os.path.join(OUT, "v2", "duiSettingsViewBrowser.nib")
    os.makedirs(dst, exist_ok=True)
    for f in os.listdir(src):
        shutil.copy2(os.path.join(src, f), os.path.join(dst, f))
    p = os.path.join(dst, "keyedobjects.nib")
    pl = plistlib.load(open(p, "rb"))
    objs = pl["$objects"]
    fixed = 0
    for i, x in enumerate(objs):
        if x == "Removable Devices":
            objs[i] = "98.title"       # 交给 .strings 表解析（英文下结果不变）
            fixed += 1
    plistlib.dump(pl, open(p, "wb"), fmt=plistlib.FMT_BINARY)
    print("   nib 修补: 替换字面量 %d 处 -> key（对象数 %d）" % (fixed, len(objs)))
    # 校验可回读
    back = plistlib.load(open(p, "rb"))
    assert len(back["$objects"]) == len(objs)
    return dst


if __name__ == "__main__":
    os.makedirs(os.path.join(OUT, "v2"), exist_ok=True)
    gen_tables()
    gen_nib()
    print("v2 资源已生成:", os.path.join(OUT, "v2"))
