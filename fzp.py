#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""VMware Fusion 26H1 简体中文补全补丁 —— 单一入口

用法:
    sudo python3 fzp.py install [--force] [--dry-run] [--target PATH] [--no-quit]
    sudo python3 fzp.py uninstall [--batch NAME]
         python3 fzp.py status        # 已装版本 / 是否最新 / 文件是否被改动 / 遗留文件
         python3 fzp.py verify        # 校验 .vmsg 与 .strings 格式（免 sudo）
         python3 fzp.py package       # 打包成 zip

设计要点
    1. 版本号 + 内容摘要：安装时写入 .fzp-manifest.json，记录每个文件的 sha256。
       同版本同内容 → 直接跳过；不同版本 → 备份后升级；已装版本更高 → 需 --force。
    2. 幂等与可回滚：清单记录每个文件是「新增」还是「覆盖」，
       卸载时新增的删掉、覆盖的从 backup 还原。
    3. 遗留清理：带本补丁标记、但不在新清单里的文件（旧版脚本留下的），
       安装时一并备份并移除。
    4. 测试隔离：--target 指向非默认 app 时，备份写到 /tmp，不污染仓库。
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
VERSION = "1.0.0"
DEFAULT_APP = "/Applications/VMware Fusion.app"
SIG_FILE = os.path.join(HERE, "signature.txt")
MANIFEST_NAME = ".fzp-manifest.json"
# 已验证的宿主产品版本；其他版本会要求 --force
SUPPORTED = {"26.0.0": {"name": "26H1", "builds": {"25388279"}}}
TESTED_ARCH = "arm64"          # 本项目在 Apple Silicon 上验证
TESTED_MACOS = (27, "27.x")    # 在 macOS 27.2 上验证
MSG_KEY_ABOUT = "msg.mac.aboutBox.trademarkGeneral"
OUR_MARKERS = ("fusion-zh-patch", "中文本地化", "中文参考译本")
REL_LPROJ = os.path.join("Contents", "Resources", "zh-Hans.lproj")
REL_MSGDIR = os.path.join("Contents", "Library", "messages", "zh-Hans")


# ────────────────────────────── 基础 ──────────────────────────────
class App:
    def __init__(self, path: str):
        self.path = path
        self.res = os.path.join(path, "Contents", "Resources")
        self.lproj = os.path.join(path, REL_LPROJ)
        self.msgdir = os.path.join(path, REL_MSGDIR)
        self.vmsg = os.path.join(self.msgdir, "vmware.vmsg")
        self.manifest = os.path.join(self.lproj, MANIFEST_NAME)
        self.is_default = os.path.abspath(path) == os.path.abspath(DEFAULT_APP)

    def exists(self) -> bool:
        return os.path.isdir(self.lproj)


def say(msg: str = "") -> None:
    print(msg, flush=True)


def sha256(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def run(cmd: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, capture_output=True, text=True)


def read_text(path: str) -> str:
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


def vparts(v: str) -> tuple:
    return tuple(int(x) for x in re.findall(r"\d+", v)[:3] or [0])


def quit_fusion() -> bool:
    pat = "VMware Fusion.app/Contents/MacOS/VMware Fusion"
    if not run(["pgrep", "-f", pat]).stdout.strip():
        return True
    say("==> 退出 VMware Fusion")
    run(["osascript", "-e", 'tell application "VMware Fusion" to quit'])
    for _ in range(30):
        if not run(["pgrep", "-f", pat]).stdout.strip():
            return True
        time.sleep(0.5)
    say("    Fusion 仍在运行；请先关闭虚拟机并手动退出")
    return False


# ────────────────────────────── 预检 ──────────────────────────────
def app_info(tgt: App) -> dict:
    info = {}
    plist = os.path.join(tgt.path, "Contents", "Info.plist")
    try:
        import plistlib
        d = plistlib.load(open(plist, "rb"))
        info["version"] = d.get("CFBundleShortVersionString", "?")
        info["build"] = d.get("CFBundleVersion", "?")
        info["min_os"] = d.get("LSMinimumSystemVersion", "?")
    except (OSError, ValueError):
        info["version"] = info["build"] = info["min_os"] = "?"
    macho = os.path.join(tgt.path, "Contents", "MacOS", "VMware Fusion")
    r = run(["lipo", "-archs", macho])
    info["archs"] = r.stdout.strip().split() if r.returncode == 0 else []
    return info


def host_info() -> dict:
    r = run(["sw_vers", "-productVersion"])
    return {"arch": run(["uname", "-m"]).stdout.strip(), "os": r.stdout.strip()}


def writable(tgt: App) -> tuple[bool, str]:
    """检测能否写入 app（macOS 14+ 受「App 管理」隐私权限控制）。"""
    probe = os.path.join(tgt.lproj, ".fzp-write-test")
    try:
        with open(probe, "w") as f:
            f.write("x")
        os.remove(probe)
        return True, ""
    except PermissionError as e:
        return False, getattr(e, "strerror", "Operation not permitted")
    except OSError as e:
        return False, str(e)


def preflight(tgt: App, force: bool = False, advisory: bool = False) -> bool:
    """返回是否允许继续安装。"""
    if not tgt.exists():
        say("✗ 找不到 VMware Fusion：%s" % tgt.path)
        return False
    info, host = app_info(tgt), host_info()
    ver = info["version"]
    supported = SUPPORTED.get(ver)
    ok = True

    say("── 预检 ──────────────────────────────────────")
    say("  VMware Fusion ：%s（build %s）" % (ver, info["build"]))
    say("  可执行架构     ：%s" % ("、".join(info["archs"]) or "未知"))
    say("  主机           ：%s / macOS %s" % (host["arch"], host["os"]))
    say("  本补丁适配     ：26H1（26.0.0，build 25388279），验证于 %s / macOS %s"
        % (TESTED_ARCH, TESTED_MACOS[1]))

    if not supported:
        say("  ⚠ 版本不匹配：本补丁为 26H1 制作，当前为 %s。" % ver)
        say("    词条 key 可能对不上，界面可能出现空白或错位。确认要继续请加 --force。")
        if not force:
            ok = False
    elif info["build"] not in supported["builds"]:
        say("  ⚠ build 号不同（%s）：同版本号的二次打包，通常可用，但未验证。" % info["build"])
        if not force:
            ok = False

    if host["arch"] != TESTED_ARCH:
        say("  ✗ 当前主机架构为 %s，本项目**只在 arm64（Apple Silicon）上实测通过**。" % host["arch"])
        say("    补丁本身只改语言资源、不碰代码，理论上与架构无关；但 Intel 环境未经验证，")
        say("    且被修改的 nib 存在两种编译变体，Intel/旧系统加载的可能不是我改的那份。")
        say("    确认要试请加 --force，并建议先 --dry-run 观察。")
        if not force:
            ok = False
    if "arm64" not in info["archs"] and host["arch"] == "arm64":
        say("  ✗ 该 Fusion 没有 arm64 切片，与 Apple Silicon 主机不匹配。")
        ok = False

    major = 0
    try:
        major = int(host["os"].split(".")[0])
    except ValueError:
        pass
    if major and major != TESTED_MACOS[0]:
        say("  ⚠ 当前 macOS %s 与验证环境（%s）不同，如遇异常请先卸载再反馈。" % (host["os"], TESTED_MACOS[1]))

    is_root = os.geteuid() == 0
    if not is_root:
        say("  %s 未以管理员身份运行；正式安装请用 sudo。"
            % ("·" if advisory else "✗"))
        if not advisory:
            ok = False
    else:
        good, err = writable(tgt)
        if not good:
            say("  ✗ 无法写入 app（%s）——多半是「App 管理」隐私权限未授权。" % err)
            say("    处理：系统设置 → 隐私与安全性 → App 管理 → 勾选你正在用的终端，")
            say("          然后完全退出该终端再重新打开（权限只在启动时读取）。")
            ok = False
        else:
            say("  写入权限       ：正常")
    say("──────────────────────────────────────────────")
    return ok


USAGE_HINT = """使用步骤：
  1) 首次使用先授权：系统设置 → 隐私与安全性 → App 管理 → 勾选你的终端
     （若列表里没有，先执行一次安装触发提示；或用「完全磁盘访问权限」代替）
  2) 保存虚拟机里的资料，退出 VMware Fusion
  3) cd 到本目录，执行 sudo python3 fzp.py install
  4) 重新打开 VMware Fusion 验证：关于窗口、设置面板、菜单
  回滚：sudo python3 fzp.py uninstall
"""


# ────────────────────────────── 清单 ──────────────────────────────
def load_manifest(tgt: App) -> dict | None:
    if not os.path.exists(tgt.manifest):
        return None
    try:
        return json.load(open(tgt.manifest, encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


def package_digest() -> str:
    """本包内容摘要：源文件路径 + sha256 的合并哈希。用于判断「内容是否一致」。"""
    h = hashlib.sha256()
    for rel in sorted(source_files()):
        h.update(rel.encode())
        h.update(sha256(os.path.join(HERE, rel)).encode())
    return h.hexdigest()[:16]


def source_files() -> list[str]:
    """会被写入 app 的源文件（相对仓库根）。"""
    out = []
    for d in ("zh-Hans", "merge", "v2"):
        base = os.path.join(HERE, d)
        if not os.path.isdir(base):
            continue
        for root, _dirs, files in os.walk(base):
            for f in files:
                if f.startswith("."):
                    continue
                out.append(os.path.relpath(os.path.join(root, f), HERE))
    out.append(os.path.join("vmsg", "vmware.vmsg"))
    out.append(os.path.join("legal", "eula_zh.txt"))
    out.append(os.path.join("legal", "Credits.html"))
    return out


def earliest_original(basename: str) -> str | None:
    """在历史备份里找该文件最早的副本——旧版安装留下的备份里通常是最原始的版本。"""
    root = os.path.join(HERE, "backup")
    if not os.path.isdir(root):
        return None
    for b in sorted(os.listdir(root)):
        p = os.path.join(root, b, basename)
        if os.path.isfile(p):
            return p
    return None


def detect_leftovers(tgt: App, keep: set[str]) -> list[str]:
    """带本补丁标记、但不在新清单里的文件（旧版脚本遗留）。"""
    left = []
    if not os.path.isdir(tgt.lproj):
        return left
    for f in sorted(os.listdir(tgt.lproj)):
        p = os.path.join(tgt.lproj, f)
        if not os.path.isfile(p) or f in keep or f == MANIFEST_NAME:
            continue
        try:
            head = read_text(p)[:4000]
        except (OSError, UnicodeDecodeError):
            continue
        if f in ("EULA.rtf", "Credits.html", "Acknowledgments.txt", "Localizable.strings") \
                or any(m in head for m in OUR_MARKERS):
            left.append(f)
    return left


# ────────────────────────────── 部署 ──────────────────────────────
def deploy(tgt: App, bak: str, dry: bool = False, has_manifest: bool = False) -> dict:
    """把补丁写入目标 app，返回写入记录。"""
    files: list[dict] = []
    notes: list[str] = []

    def put(rel: str, data_writer):
        """rel 相对 app 根；data_writer(dst) 负责写。"""
        dst = os.path.join(tgt.path, rel)
        existed = os.path.exists(dst)
        if existed:
            bdst = os.path.join(bak, os.path.basename(rel))
            os.makedirs(os.path.dirname(bdst), exist_ok=True)
            if not dry:
                src_bak = dst
                if not has_manifest:
                    old = earliest_original(os.path.basename(rel))
                    if old:
                        src_bak = old
                        notes.append("从历史备份取回原始版本：%s" % os.path.basename(rel))
                shutil.copy2(src_bak, bdst)
        if not dry:
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            data_writer(dst)
        files.append({"path": rel, "action": "modified" if existed else "added",
                      "sha256": sha256(dst) if not dry and os.path.exists(dst) else ""})

    # 1) 整表
    src_dir = os.path.join(HERE, "zh-Hans")
    tables = sorted(f for f in os.listdir(src_dir) if f.endswith(".strings"))
    say("==> .strings 整表 %d 张" % len(tables))
    for f in tables:
        s = os.path.join(src_dir, f)
        put(os.path.join(REL_LPROJ, f), lambda dst, s=s: shutil.copy2(s, dst))

    # 2) 增量补丁
    say("==> 合并增量补丁")
    mdir = os.path.join(HERE, "merge")
    for fn in sorted(os.listdir(mdir)):
        if not fn.endswith(".append.strings"):
            continue
        name = fn[: -len(".append.strings")] + ".strings"
        rel = os.path.join(REL_LPROJ, name)
        dst = os.path.join(tgt.path, rel)
        if not os.path.exists(dst):
            continue
        body = open(os.path.join(mdir, fn), encoding="utf-8").read().split("*/", 1)[1].strip()

        def merge(dst, body=body):
            cur = read_text(dst).rstrip("\n")
            have = set(re.findall(r'^"([^"]+)"\s*=', cur, re.M))
            add = [l for l in body.splitlines()
                   if re.match(r'^"[^"]+"\s*=', l) and re.findall(r'^"([^"]+)"', l)[0] not in have]
            open(dst, "w", encoding="utf-8").write(cur + "\n\n" + "\n".join(add) + "\n")
            say("    %-44s +%d 条" % (name.replace(".strings", ""), len(add)))

        put(rel, merge)

    # 3) 附加表 + nib
    say("==> v2 附加资源")
    loc = os.path.join(HERE, "v2", "Localizable.strings")
    if os.path.exists(loc):
        put(os.path.join(REL_LPROJ, "Localizable.strings"), lambda dst: shutil.copy2(loc, dst))
        say("    Localizable.strings")
    extra = os.path.join(HERE, "v2", "duiSettingsViewBrowser.extra.strings")
    if os.path.exists(extra):
        body = open(extra, encoding="utf-8").read().split("*/", 1)[1].strip()

        def merge_browser(dst, body=body):
            cur = read_text(dst) if os.path.exists(dst) else ""
            have = set(re.findall(r'^"([^"]+)"\s*=', cur, re.M))
            add = [l for l in body.splitlines()
                   if re.match(r'^"[^"]+"\s*=', l) and re.findall(r'^"([^"]+)"', l)[0] not in have]
            open(dst, "w", encoding="utf-8").write(cur.rstrip("\n") + "\n\n" + "\n".join(add) + "\n")
            say("    duiSettingsViewBrowser +%d 条" % len(add))

        put(os.path.join(REL_LPROJ, "duiSettingsViewBrowser.strings"), merge_browser)
    nib = os.path.join(HERE, "v2", "duiSettingsViewBrowser.nib")
    if os.path.isdir(nib):
        rel = os.path.join("Contents", "Resources", "Base.lproj", "duiSettingsViewBrowser.nib")
        dst = os.path.join(tgt.path, rel)
        if not dry:
            bdst = os.path.join(bak, "nib", "duiSettingsViewBrowser.nib")
            if os.path.isdir(dst):
                os.makedirs(os.path.dirname(bdst), exist_ok=True)
                shutil.copytree(dst, bdst)
            shutil.rmtree(dst, ignore_errors=True)
            shutil.copytree(nib, dst)
        files.append({"path": rel, "action": "modified", "sha256": ""})
        say("    nib：分组标题改为走本地化表")

    # 4) 消息目录 + 署名
    say("==> 消息目录")
    src_vmsg = os.path.join(HERE, "vmsg", "vmware.vmsg")
    if not dry:
        os.makedirs(tgt.msgdir, exist_ok=True)
        shutil.copy2(src_vmsg, tgt.vmsg)
        inject_signature(tgt.vmsg)
    n = open(src_vmsg, encoding="utf-8").read().count(" = ")
    say("    %d 条" % n)
    files.append({"path": os.path.join(REL_MSGDIR, "vmware.vmsg"),
                  "action": "added", "sha256": sha256(tgt.vmsg) if not dry else ""})

    # 5) 法律文本
    say("==> 中英对照法律文本")
    if not dry:
        r = subprocess.run([sys.executable, os.path.join(HERE, "legal", "build_legal.py"),
                            tgt.res, tgt.lproj, SIG_FILE], capture_output=True, text=True)
        if r.returncode != 0:
            say("    生成失败（不影响汉化）：%s" % (r.stderr or "").strip()[:150])
    for name in ("EULA.rtf", "Credits.html"):
        rel = os.path.join(REL_LPROJ, name)
        if os.path.exists(os.path.join(tgt.path, rel)) or not dry:
            files.append({"path": rel, "action": "added", "sha256": ""})
    ack_rel = os.path.join("Contents", "Resources", "Acknowledgments.txt")
    ack = os.path.join(tgt.path, ack_rel)
    if os.path.exists(ack):
        files.append({"path": ack_rel, "action": "modified", "sha256": ""})
        say("    Acknowledgments.txt（中英对照）")

    return {"files": files, "vmsg_entries": n, "notes": notes}


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
    text = text[: m.start()] + '%s = "%s（%s）"' % (MSG_KEY_ABOUT, m.group(1), sig) + text[m.end():]
    open(vmsg, "w", encoding="utf-8").write(text)
    say("    署名已写入关于窗口")


# ────────────────────────────── 校验 ──────────────────────────────
def verify(tgt: App | None = None, quiet: bool = False) -> bool:
    ok = True
    path = tgt.vmsg if (tgt and os.path.exists(tgt.vmsg)) else os.path.join(HERE, "vmsg", "vmware.vmsg")
    lines = [l for l in open(path, encoding="utf-8").read().splitlines() if l.strip()]
    bad = [l for l in lines if not re.match(r'^[A-Za-z0-9_.-]+ = ".*"$', l)]
    keys = [l.split(" = ")[0] for l in lines]
    dup = {k for k in keys if keys.count(k) > 1}
    bad_ph = []
    for l in lines:
        v = l.split(" = ", 1)[1]
        nums = [int(n) for n in re.findall(r'%(\d+)\$', v)]
        plain = re.findall(r'%(?!\d+\$)(?:s|d|u|f|lu|ld|lld|llu|zu|zd)', v)
        if nums and plain:
            bad_ph.append(keys[lines.index(l)])
        elif nums and sorted(set(nums)) != list(range(1, max(nums) + 1)):
            bad_ph.append(keys[lines.index(l)])
    if not quiet:
        say("    vmsg：%d 条，格式异常 %d，重复键 %d，占位符异常 %d"
            % (len(lines), len(bad), len(dup), len(bad_ph)))
    if bad or dup or bad_ph:
        ok = False
        for x in (bad[:2] + bad_ph[:2]):
            say("      ! %s" % str(x)[:80])

    d = tgt.lproj if tgt else os.path.join(HERE, "zh-Hans")
    fs = [os.path.join(d, f) for f in os.listdir(d) if f.endswith(".strings")]
    badf = [os.path.basename(f) for f in fs if run(["plutil", "-lint", f]).returncode != 0]
    if not quiet:
        say("    strings：%d 个，语法异常 %d" % (len(fs), len(badf)))
    if badf:
        ok = False
        say("      ! %s" % ", ".join(badf[:5]))
    return ok


# ────────────────────────────── 命令 ──────────────────────────────
def parse_args(argv: list[str], opts: tuple = ()) -> tuple[dict, set, list]:
    """解析 --opt VALUE 与布尔开关，返回 (opts, flags, positionals)。"""
    o, f, pos, i = {}, set(), [], 0
    while i < len(argv):
        a = argv[i]
        if a in opts and i + 1 < len(argv):
            o[a] = argv[i + 1]
            i += 2
        elif a.startswith("-"):
            f.add(a)
            i += 1
        else:
            pos.append(a)
            i += 1
    return o, f, pos
def cmd_install(argv: list[str]) -> int:
    o, f, _ = parse_args(argv, ("--target",))
    target = o.get("--target", DEFAULT_APP)
    force, dry, no_quit = "--force" in f, "--dry-run" in f, "--no-quit" in f
    tgt = App(target)
    if not tgt.exists():
        say("找不到 %s" % tgt.lproj)
        return 1

    cur = load_manifest(tgt)
    pkg = package_digest()
    say("本包版本 %s（内容摘要 %s）" % (VERSION, pkg))
    if cur:
        say("已装版本 %s（内容摘要 %s，%s）"
            % (cur.get("version", "?"), cur.get("digest", "?"), cur.get("installed_at", "?")))
        if not force:
            if vparts(cur.get("version", "0")) > vparts(VERSION):
                say("\n已装版本比本脚本更新，拒绝降级。确需降级请加 --force。")
                return 1
            if cur.get("version") == VERSION and cur.get("digest") == pkg:
                say("\n已是最新，无需安装（如需重装请加 --force）。")
                return 0
    else:
        say("检测到：尚未安装（或安装记录缺失，将作为全新安装处理）")

    if not preflight(tgt, force, advisory=dry):
        say("\n预检未通过，已中止（未改动任何文件）。用法与授权说明：python3 fzp.py doctor")
        return 1
    if dry:
        say("（--dry-run：只报告，不写文件）")
    if not no_quit and not dry and not quit_fusion():
        return 1

    stamp = time.strftime("%Y%m%d-%H%M%S")
    if tgt.is_default:
        bak = os.path.join(HERE, "backup", "%s-%s" % (VERSION, stamp))
    else:
        bak = tempfile.mkdtemp(prefix="fzp-backup-")
    os.makedirs(bak, exist_ok=True)
    say("==> 备份目录：%s" % bak)

    files = deploy(tgt, bak, dry, has_manifest=bool(cur))
    if files.get("notes"):
        say("==> 原始版本回填 %d 个文件（旧版安装无清单，已从历史备份取回）"
            % len(files["notes"]))
    if not dry:
        (tgt.lproj if os.path.isdir(tgt.lproj) else None)

    # 遗留清理
    keep = {os.path.basename(f["path"]) for f in files["files"]}
    left = detect_leftovers(tgt, keep)
    if left:
        say("==> 清理旧版遗留 %d 个：%s" % (len(left), ", ".join(left)))
        if not dry:
            for f in left:
                p = os.path.join(tgt.lproj, f)
                shutil.copy2(p, os.path.join(bak, "leftover-" + f))
                os.remove(p)

    if dry:
        return 0

    ok = verify(tgt)
    if not ok:
        say("\n校验未通过；可执行 sudo python3 fzp.py uninstall 回滚。")
        return 1

    manifest = {
        "tool": "fusion-zh-patch",
        "version": VERSION,
        "digest": pkg,
        "installed_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "app_path": tgt.path,
        "vmsg_entries": files["vmsg_entries"],
        "signature": signature(),
        "backup": os.path.basename(bak) if tgt.is_default else bak,
        "files": files["files"],
    }
    open(tgt.manifest, "w", encoding="utf-8").write(json.dumps(manifest, ensure_ascii=False, indent=1))
    say("\n完成。版本 %s，写入 %d 项，回滚：sudo python3 fzp.py uninstall"
        % (VERSION, len(files["files"])))
    say("提示：消息目录在启动时加载，请重新打开 VMware Fusion。")
    return 0


def cmd_uninstall(argv: list[str]) -> int:
    o, _f, pos = parse_args(argv, ("--target", "--batch"))
    target = o.get("--target", DEFAULT_APP)
    batch = o.get("--batch") or (pos[0] if pos else None)
    tgt = App(target)
    cur = load_manifest(tgt)

    if batch:
        bak = os.path.join(HERE, "backup", batch)
    elif cur:
        b = cur.get("backup", "")
        bak = b if os.path.isabs(b) else os.path.join(HERE, "backup", b)
    else:
        root = os.path.join(HERE, "backup")
        batches = sorted(os.listdir(root)) if os.path.isdir(root) else []
        bak = os.path.join(root, batches[-1]) if batches else ""
    if bak and not os.path.isdir(bak):
        bak = ""

    if not quit_fusion():
        return 1
    say("==> 回滚（备份：%s）" % (bak or "无，仅按清单删除新增文件"))

    if cur:
        for f in cur.get("files", []):
            dst = os.path.join(tgt.path, f["path"])
            name = os.path.basename(f["path"])
            src = os.path.join(bak, name) if bak else ""
            if f["action"] == "modified" and src and os.path.exists(src):
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                shutil.copy2(src, dst)
            elif f["action"] == "added" and os.path.exists(dst):
                if os.path.isdir(dst):
                    shutil.rmtree(dst, ignore_errors=True)
                else:
                    os.remove(dst)
        nib_bak = os.path.join(bak, "nib", "duiSettingsViewBrowser.nib") if bak else ""
        if nib_bak and os.path.isdir(nib_bak):
            d = os.path.join(tgt.res, "Base.lproj", "duiSettingsViewBrowser.nib")
            shutil.rmtree(d, ignore_errors=True)
            shutil.copytree(nib_bak, d)
            say("    nib 已还原")
    else:
        say("    无安装清单，仅移除消息目录与已知文件")
        shutil.rmtree(tgt.msgdir, ignore_errors=True)

    # 遗留文件还原
    if bak and os.path.isdir(bak):
        for f in os.listdir(bak):
            if f.startswith("leftover-"):
                shutil.copy2(os.path.join(bak, f), os.path.join(tgt.lproj, f[len("leftover-"):]))
                say("    已还原遗留文件 %s" % f[len("leftover-"):])

    shutil.rmtree(tgt.msgdir, ignore_errors=True)
    if os.path.exists(tgt.manifest):
        os.remove(tgt.manifest)
    say("完成。请重新打开 VMware Fusion。")
    return 0


def cmd_status() -> int:
    tgt = App(DEFAULT_APP)
    if not tgt.exists():
        say("找不到 VMware Fusion")
        return 1
    say("应用      ：%s" % DEFAULT_APP)
    say("本包版本  ：%s（内容摘要 %s）" % (VERSION, package_digest()))
    cur = load_manifest(tgt)
    if not cur:
        n = open(tgt.vmsg, encoding="utf-8").read().count(" = ") if os.path.exists(tgt.vmsg) else 0
        say("已装版本  ：无清单（%s）" % ("检测到 %d 条消息目录，属旧版脚本安装" % n if n else "未安装"))
    else:
        say("已装版本  ：%s（%s）" % (cur.get("version", "?"), cur.get("installed_at", "?")))
        say("版本状态  ：%s" % ("已是最新" if cur.get("version") == VERSION and cur.get("digest") == package_digest()
                               else ("比本脚本新" if vparts(cur.get("version", "0")) > vparts(VERSION) else "可升级")))
        drift, missing = [], 0
        for f in cur.get("files", []):
            p = os.path.join(tgt.path, f["path"])
            if not f.get("sha256"):
                continue
            if not os.path.exists(p):
                missing += 1
            elif sha256(p) != f["sha256"]:
                drift.append(os.path.basename(f["path"]))
        say("完整性    ：%d 个文件被改动%s%s"
            % (len(drift), "，" if drift else "，", ", ".join(drift[:4]) if drift else "全部一致")
            + ("；%d 个缺失" % missing if missing else ""))
        say("消息条数  ：%s" % cur.get("vmsg_entries", "?"))
        say("署名      ：%s" % (cur.get("signature") or "无"))
    if os.path.exists(tgt.vmsg):
        say("实际消息  ：%d 条" % open(tgt.vmsg, encoding="utf-8").read().count(" = "))
    ack = os.path.join(tgt.res, "Acknowledgments.txt")
    if os.path.exists(ack):
        say("致谢页    ：%s" % ("已本地化" if "本产品包含开源软件" in read_text(ack) else "未本地化"))
    if cur:
        left = detect_leftovers(tgt, {os.path.basename(f["path"]) for f in cur.get("files", [])})
        if left:
            say("遗留文件  ：%s（下次 install 会自动备份并清理）" % ", ".join(left))
    else:
        mine = detect_leftovers(tgt, set())
        if mine:
            say("受管文件  ：%d 个（旧版安装，尚无清单；下次 install 会纳入版本管理）" % len(mine))
    return 0


def cmd_package() -> int:
    out = os.path.join(os.path.dirname(HERE), "fusion-zh-patch-%s-v%s.zip"
                       % (time.strftime("%Y%m%d"), VERSION))
    skip = {"backup", "__pycache__", ".git", "legacy"}
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for root, dirs, files in os.walk(HERE):
            dirs[:] = [d for d in dirs if d not in skip]
            for f in files:
                if f in (".DS_Store",) or f.startswith("."):
                    continue
                p = os.path.join(root, f)
                z.write(p, os.path.relpath(p, os.path.dirname(HERE)))
    say("已打包：%s（%.0f KB）" % (out, os.path.getsize(out) / 1024))
    return 0


def cmd_doctor() -> int:
    tgt = App(DEFAULT_APP)
    say("VMware Fusion 简体中文补丁 · 环境体检")
    say("")
    preflight(tgt, force=True, advisory=True)
    say("")
    if os.geteuid() != 0:
        say("提示：当前以普通用户运行，「写入权限」一项未检测；安装时请用 sudo。")
        say("")
    say(USAGE_HINT)
    return 0


def cmd_prune(argv: list[str]) -> int:
    """清理历史备份：保留最早一个（含最原始的版本）与最近 N 个。"""
    o, _f, _p = parse_args(argv, ("--keep",))
    keep_n = int(o.get("--keep", 3))
    root = os.path.join(HERE, "backup")
    if not os.path.isdir(root):
        say("没有备份目录")
        return 0
    items = sorted(os.listdir(root))
    if len(items) <= keep_n + 1:
        say("备份数 %d，无需清理" % len(items))
        return 0
    drop = items[1:-keep_n] if keep_n else items[1:]
    failed = 0
    for d in drop:
        try:
            shutil.rmtree(os.path.join(root, d))
        except PermissionError:
            failed += 1
    kept = [d for d in items if not os.path.exists(os.path.join(root, d)) or d in items]
    left = sorted(os.listdir(root))
    say("已删除 %d 个旧备份" % (len(drop) - failed))
    if failed:
        say("  %d 个删不掉（属主是 root）：请用 sudo python3 fzp.py prune --keep %d" % (failed, keep_n))
    say("当前保留 %d 个：%s" % (len(left), ", ".join(left)))
    return 0


def main(argv: list[str]) -> int:
    if not argv or argv[0] in ("-h", "--help", "help"):
        print(__doc__)
        return 0
    cmd, rest = argv[0], argv[1:]
    return {
        "install": cmd_install,
        "uninstall": cmd_uninstall,
        "status": lambda _a: cmd_status(),
        "verify": lambda _a: 0 if verify() else 1,
        "package": lambda _a: cmd_package(),
        "prune": cmd_prune,
        "doctor": lambda _a: cmd_doctor(),
    }.get(cmd, lambda _a: (say("未知命令：%s\n" % cmd), print(__doc__), 1)[-1])(rest)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
