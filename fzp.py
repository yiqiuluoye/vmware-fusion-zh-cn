#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""VMware Fusion 26H1 简体中文补全补丁 —— 单一入口脚本

用法:
    sudo python3 fzp.py install       # 安装（会先退出 Fusion）
    sudo python3 fzp.py uninstall     # 回滚到安装前
         python3 fzp.py status        # 查看安装状态
         python3 fzp.py verify        # 校验 .vmsg 与 .strings 格式
         python3 fzp.py package       # 打包成 zip 便于分享
         python3 fzp.py install --target /tmp/X.app --no-quit   # 装到副本（测试用）

把所有工作集中在这里：备份、部署、合并、生成法律文本、注入署名、校验、回滚。
数据文件：
    vmsg/vmware.vmsg   消息目录（可直接编辑，这是译文的源）
    zh-Hans/*.strings  整表补全
    merge/*.append.strings  已有表的增量补丁
    v2/                nib 补丁与附加表
    legal/             协议中文译本、致谢模板、生成逻辑
    signature.txt      署名（第一行即显示内容）
"""
from __future__ import annotations

import os
import plistlib
import re
import shutil
import subprocess
import sys
import tempfile
import time
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_APP = "/Applications/VMware Fusion.app"
SIG_FILE = os.path.join(HERE, "signature.txt")

MSG_KEY_ABOUT = "msg.mac.aboutBox.trademarkGeneral"


# ────────────────────────────── 基础工具 ──────────────────────────────
class App:
    def __init__(self, path: str):
        self.path = path
        self.res = os.path.join(path, "Contents", "Resources")
        self.lproj = os.path.join(self.res, "zh-Hans.lproj")
        self.msgdir = os.path.join(path, "Contents", "Library", "messages", "zh-Hans")
        self.vmsg = os.path.join(self.msgdir, "vmware.vmsg")

    def exists(self) -> bool:
        return os.path.isdir(self.lproj)


def say(msg: str) -> None:
    print(msg, flush=True)


def run(cmd: list[str], check: bool = False) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, capture_output=True, text=True, check=check)


def read_text(path: str) -> str:
    """健壮读取：处理 UTF-16 BOM、伪 BOM（BOM 是 UTF-16 但内容是 UTF-8）等情况。"""
    b = open(path, "rb").read()
    if b[:2] in (b"\xff\xfe", b"\xfe\xff"):
        try:
            t = b[2:].decode("utf-8")
            if "\x00" not in t:
                return t
        except UnicodeDecodeError:
            pass
        return b.decode("utf-16")
    if b[:3] == b"\xef\xbb\xbf":
        return b[3:].decode("utf-8")
    try:
        t = b.decode("utf-8")
        if "\x00" not in t:
            return t
    except UnicodeDecodeError:
        pass
    for enc in ("utf-16-le", "utf-16-be"):
        try:
            t = b.decode(enc)
            if "\x00" not in t:
                return t
        except UnicodeDecodeError:
            continue
    return b.decode("utf-8", errors="replace")


def signature() -> str:
    if os.path.exists(SIG_FILE):
        for line in open(SIG_FILE, encoding="utf-8"):
            if line.strip():
                return line.strip()
    return ""


def quit_fusion() -> bool:
    pattern = "VMware Fusion.app/Contents/MacOS/VMware Fusion"
    if not run(["pgrep", "-f", pattern]).stdout.strip():
        return True
    say("==> 退出 VMware Fusion")
    run(["osascript", "-e", 'tell application "VMware Fusion" to quit'])
    for _ in range(30):
        if not run(["pgrep", "-f", pattern]).stdout.strip():
            return True
        time.sleep(0.5)
    say("    Fusion 仍在运行，请先关机虚拟机并手动退出")
    return False


# ────────────────────────────── build（部署集） ──────────────────────────────
def build(tgt: App, bak: str) -> bool:
    """把补丁写入目标 app。返回是否全部成功。"""
    ok = True

    # 1) .strings：整表补全
    say("==> 写入 .strings 整表")
    src = os.path.join(HERE, "zh-Hans")
    tables = sorted(f for f in os.listdir(src) if f.endswith(".strings"))
    for f in tables:
        dst = os.path.join(tgt.lproj, f)
        if os.path.exists(dst):
            shutil.copy2(dst, os.path.join(bak, f))
        shutil.copy2(os.path.join(src, f), dst)
    say("    %d 张表" % len(tables))

    # 2) .strings：已有表的增量补丁
    say("==> 合并增量补丁")
    mdir = os.path.join(HERE, "merge")
    for fn in sorted(os.listdir(mdir)):
        if not fn.endswith(".append.strings"):
            continue
        name = fn[: -len(".append.strings")] + ".strings"
        dst = os.path.join(tgt.lproj, name)
        if not os.path.exists(dst):
            continue
        shutil.copy2(dst, os.path.join(bak, name))
        body = open(os.path.join(mdir, fn), encoding="utf-8").read().split("*/", 1)[1].strip()
        cur = read_text(dst).rstrip("\n")
        have = set(re.findall(r'^"([^"]+)"\s*=', cur, re.M))
        add = [l for l in body.splitlines()
               if re.match(r'^"[^"]+"\s*=', l) and re.findall(r'^"([^"]+)"', l)[0] not in have]
        open(dst, "w", encoding="utf-8").write(cur + "\n\n" + "\n".join(add) + "\n")
        say("    %-46s +%d 条" % (name.replace(".strings", ""), len(add)))

    # 3) v2：附加表 + nib
    say("==> 写入 v2 附加资源")
    v2 = os.path.join(HERE, "v2")
    localizable = os.path.join(v2, "Localizable.strings")
    if os.path.exists(localizable):
        dst = os.path.join(tgt.lproj, "Localizable.strings")
        if os.path.exists(dst):
            shutil.copy2(dst, os.path.join(bak, "Localizable.strings"))
        shutil.copy2(localizable, dst)
        say("    Localizable.strings")
    extra = os.path.join(v2, "duiSettingsViewBrowser.extra.strings")
    if os.path.exists(extra):
        dst = os.path.join(tgt.lproj, "duiSettingsViewBrowser.strings")
        if os.path.exists(dst):
            shutil.copy2(dst, os.path.join(bak, "duiSettingsViewBrowser.strings"))
        body = open(extra, encoding="utf-8").read().split("*/", 1)[1].strip()
        cur = read_text(dst) if os.path.exists(dst) else ""
        have = set(re.findall(r'^"([^"]+)"\s*=', cur, re.M))
        add = [l for l in body.splitlines()
               if re.match(r'^"[^"]+"\s*=', l) and re.findall(r'^"([^"]+)"', l)[0] not in have]
        open(dst, "w", encoding="utf-8").write(cur.rstrip("\n") + "\n\n" + "\n".join(add) + "\n")
        say("    duiSettingsViewBrowser 表 +%d 条" % len(add))
    nib_src = os.path.join(v2, "duiSettingsViewBrowser.nib")
    if os.path.isdir(nib_src):
        nib_dst = os.path.join(tgt.res, "Base.lproj", "duiSettingsViewBrowser.nib")
        if os.path.isdir(nib_dst):
            shutil.copytree(nib_dst, os.path.join(bak, "nib", "duiSettingsViewBrowser.nib"))
        shutil.rmtree(nib_dst, ignore_errors=True)
        shutil.copytree(nib_src, nib_dst)
        say("    nib：分组标题改为走本地化表")

    # 4) .vmsg + 署名
    say("==> 写入消息目录")
    os.makedirs(tgt.msgdir, exist_ok=True)
    src_vmsg = os.path.join(HERE, "vmsg", "vmware.vmsg")
    shutil.copy2(src_vmsg, tgt.vmsg)
    n = open(tgt.vmsg, encoding="utf-8").read().count(" = ")
    say("    %d 条消息" % n)
    inject_signature(tgt.vmsg)

    # 5) 法律文本
    say("==> 生成中英对照法律文本")
    try:
        subprocess.run([sys.executable, os.path.join(HERE, "legal", "build_legal.py"),
                        tgt.res, tgt.lproj, SIG_FILE], check=True, capture_output=True, text=True)
        say("    EULA.rtf / Credits.html / Acknowledgments.txt")
    except subprocess.CalledProcessError as e:
        say("    生成失败（不影响汉化）：%s" % (e.stderr or "").strip()[:200])
        ok = False
    ack = os.path.join(tgt.res, "Acknowledgments.txt")
    if os.path.exists(ack):
        shutil.copy2(ack, os.path.join(bak, "Acknowledgments.txt.orig"))

    return ok


def inject_signature(vmsg: str) -> None:
    sig = signature()
    if not sig:
        return
    text = open(vmsg, encoding="utf-8").read()
    m = re.search(r'^%s = "(.*)"$' % re.escape(MSG_KEY_ABOUT), text, re.M)
    if not m:
        return
    if sig in m.group(1):
        say("    署名已在关于窗口文案中")
        return
    text = text[:m.start()] + '%s = "%s（%s）"' % (MSG_KEY_ABOUT, m.group(1), sig) + text[m.end():]
    open(vmsg, "w", encoding="utf-8").write(text)
    say("    署名已写入关于窗口")


# ────────────────────────────── 校验 ──────────────────────────────
def verify(tgt: App | None = None) -> bool:
    say("==> 校验")
    ok = True

    # .vmsg 格式
    path = tgt.vmsg if (tgt and os.path.exists(tgt.vmsg)) else os.path.join(HERE, "vmsg", "vmware.vmsg")
    lines = [l for l in open(path, encoding="utf-8").read().splitlines() if l.strip()]
    bad_fmt = [l for l in lines if not re.match(r'^[A-Za-z0-9_.-]+ = ".*"$', l)]
    keys = [l.split(" = ")[0] for l in lines]
    dup = {k for k in keys if keys.count(k) > 1}
    say("    vmsg：%d 条，格式异常 %d，重复键 %d" % (len(lines), len(bad_fmt), len(dup)))
    if bad_fmt or dup:
        ok = False
        for l in bad_fmt[:3]:
            say("      ! %s" % l[:80])

    # 占位符一致性（%1$s 之类不能超出原文编号）
    bad_ph = []
    for l in lines:
        k, v = l.split(" = ", 1)
        nums = [int(n) for n in re.findall(r'%(\d+)\$', v)]
        if nums and sorted(set(nums)) != list(range(1, max(nums) + 1)):
            bad_ph.append(k)
    if bad_ph:
        ok = False
        say("    占位符编号异常 %d 条：%s" % (len(bad_ph), bad_ph[:3]))

    # .strings 语法（plutil）
    target_dir = tgt.lproj if tgt else os.path.join(HERE, "zh-Hans")
    files = [os.path.join(target_dir, f) for f in os.listdir(target_dir) if f.endswith(".strings")]
    bad = []
    for f in files:
        if run(["plutil", "-lint", f]).returncode != 0:
            bad.append(os.path.basename(f))
    say("    strings：%d 个文件，语法异常 %d" % (len(files), len(bad)))
    if bad:
        ok = False
        say("      ! %s" % ", ".join(bad[:5]))
    return ok


# ────────────────────────────── 命令 ──────────────────────────────
def cmd_install(argv: list[str]) -> int:
    target = DEFAULT_APP
    no_quit = False
    for i, a in enumerate(argv):
        if a == "--target" and i + 1 < len(argv):
            target = argv[i + 1]
        if a == "--no-quit":
            no_quit = True
    tgt = App(target)
    if not tgt.exists():
        say("找不到 %s" % tgt.lproj)
        return 1
    if not no_quit and not quit_fusion():
        return 1

    stamp = time.strftime("%Y%m%d-%H%M%S")
    bak = os.path.join(HERE, "backup", stamp)
    os.makedirs(bak, exist_ok=True)
    say("==> 备份到 backup/%s" % stamp)

    build(tgt, bak)
    if not verify(tgt):
        say("\n校验未通过。可执行 sudo python3 fzp.py uninstall 回滚。")
        return 1

    say("\n完成。改动 %d 个备份点，回滚：sudo python3 fzp.py uninstall" % len(os.listdir(bak)))
    say("提示：消息目录在启动时加载，请重新打开 VMware Fusion 后才生效。")
    return 0


def cmd_uninstall(argv: list[str]) -> int:
    target = DEFAULT_APP
    batch = None
    for i, a in enumerate(argv):
        if a == "--target" and i + 1 < len(argv):
            target = argv[i + 1]
        elif a == "--batch" and i + 1 < len(argv):
            batch = argv[i + 1]
        elif not a.startswith("-"):
            batch = a
    tgt = App(target)
    root = os.path.join(HERE, "backup")
    if not batch:
        batches = sorted(os.listdir(root)) if os.path.isdir(root) else []
        if not batches:
            say("没有可用备份")
            return 1
        batch = batches[-1]
    bak = os.path.join(root, batch)
    if not os.path.isdir(bak):
        say("找不到备份 %s" % batch)
        return 1
    if not quit_fusion():
        return 1

    say("==> 从 backup/%s 还原" % batch)
    for f in os.listdir(bak):
        src = os.path.join(bak, f)
        if f == "nib" and os.path.isdir(src):
            for d in os.listdir(src):
                dst = os.path.join(tgt.res, "Base.lproj", d)
                shutil.rmtree(dst, ignore_errors=True)
                shutil.copytree(os.path.join(src, d), dst)
            say("    Base.lproj nib 已还原")
        elif f == "Acknowledgments.txt.orig":
            shutil.copy2(src, os.path.join(tgt.res, "Acknowledgments.txt"))
            say("    Acknowledgments.txt 已还原")
        elif os.path.isfile(src):
            shutil.copy2(src, os.path.join(tgt.lproj, f))
    # 移除补丁新增、原本不存在的文件
    for name in ("EULA.rtf", "Credits.html", "Localizable.strings", "Acknowledgments.txt"):
        p = os.path.join(tgt.lproj, name)
        if os.path.exists(p) and not os.path.exists(os.path.join(bak, name)):
            os.remove(p)
    for f in os.listdir(os.path.join(HERE, "zh-Hans")):
        if not os.path.exists(os.path.join(bak, f)):
            p = os.path.join(tgt.lproj, f)
            if os.path.exists(p):
                os.remove(p)
    shutil.rmtree(tgt.msgdir, ignore_errors=True)
    say("    消息目录已移除")
    say("完成。请重新打开 VMware Fusion。")
    return 0


def cmd_status() -> int:
    tgt = App(DEFAULT_APP)
    if not tgt.exists():
        say("找不到 VMware Fusion")
        return 1
    say("应用：%s" % DEFAULT_APP)
    if os.path.exists(tgt.vmsg):
        n = open(tgt.vmsg, encoding="utf-8").read().count(" = ")
        say("消息目录：已安装，%d 条" % n)
        sig = signature()
        say("署名：%s" % ("已写入" if sig and sig in open(tgt.vmsg, encoding="utf-8").read() else "未写入"))
    else:
        say("消息目录：未安装")
    tables = [f for f in os.listdir(tgt.lproj) if f.endswith(".strings")]
    say("zh-Hans 表：%d 个" % len(tables))
    say("EULA：%s" % ("中英对照（已安装）" if os.path.exists(os.path.join(tgt.lproj, "EULA.rtf")) else "未安装"))
    ack = os.path.join(tgt.res, "Acknowledgments.txt")
    if os.path.exists(ack):
        say("致谢：%s" % ("已本地化" if "本产品包含开源软件" in read_text(ack) else "未本地化"))
    return 0


def cmd_package() -> int:
    out = os.path.join(os.path.dirname(HERE), "fusion-zh-patch-%s.zip" % time.strftime("%Y%m%d"))
    skip_dirs = {"backup", "__pycache__", ".git", "legacy"}
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for root, dirs, files in os.walk(HERE):
            dirs[:] = [d for d in dirs if d not in skip_dirs]
            for f in files:
                if f == ".DS_Store":
                    continue
                p = os.path.join(root, f)
                z.write(p, os.path.relpath(p, os.path.dirname(HERE)))
    size = os.path.getsize(out) / 1024
    say("已打包：%s（%.0f KB）" % (out, size))
    return 0


USAGE = __doc__ or ""


def main(argv: list[str]) -> int:
    if not argv or argv[0] in ("-h", "--help", "help"):
        print(USAGE)
        return 0
    cmd, rest = argv[0], argv[1:]
    if cmd == "install":
        return cmd_install(rest)
    if cmd == "uninstall":
        return cmd_uninstall(rest)
    if cmd == "status":
        return cmd_status()
    if cmd == "verify":
        return 0 if verify() else 1
    if cmd == "package":
        return cmd_package()
    say("未知命令：%s\n" % cmd)
    print(USAGE)
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
