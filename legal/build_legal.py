#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""在安装时生成中英对照的 EULA.rtf 与 Credits.html。

EULA 的英文原文**不随仓库分发**：本脚本从本机已安装的 VMware Fusion
读取 English.lproj/EULA.rtf，转成纯文本后与 legal/eula_zh.txt（本项目的
中文译本）拼接，生成「中文在上、英文原文在下」的 RTF。

用法: build_legal.py <Resources目录> <输出目录> [signature.txt]
"""
import os, subprocess, sys, html, tempfile

APP_RES = sys.argv[1]
OUT = sys.argv[2]
SIG = sys.argv[3] if len(sys.argv) > 3 else None
HERE = os.path.dirname(os.path.abspath(__file__))

def app_text(name):
    """从已安装 app 里取原始英文文档，转纯文本。"""
    for lproj in ("English.lproj", "Base.lproj"):
        p = os.path.join(APP_RES, lproj, name)
        if os.path.exists(p):
            if name.endswith(".rtf"):
                return subprocess.run(["textutil", "-convert", "txt", "-stdout", p],
                                      capture_output=True, text=True).stdout
            return open(p, encoding="utf-8", errors="replace").read()
    return ""

def build_eula():
    en = app_text("EULA.rtf")
    if not en.strip():
        print("    跳过 EULA：找不到原始英文文档")
        return
    zh = open(os.path.join(HERE, "eula_zh.txt"), encoding="utf-8").read()
    merged = zh.rstrip() + "\n\n" + en
    with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False, encoding="utf-8") as f:
        f.write(merged); tmp = f.name
    subprocess.run(["textutil", "-convert", "rtf", "-inputencoding", "UTF-8",
                    "-output", os.path.join(OUT, "EULA.rtf"), tmp], check=True)
    os.unlink(tmp)
    print("    EULA.rtf（中文译本 + 本机读取的英文原文）")

def build_credits():
    p = os.path.join(HERE, "Credits.html")
    t = open(p, encoding="utf-8").read()
    body = ""
    if SIG and os.path.exists(SIG):
        body = "".join("<p>%s</p>" % html.escape(l)
                       for l in open(SIG, encoding="utf-8").read().strip().splitlines() if l.strip())
    open(os.path.join(OUT, "Credits.html"), "w", encoding="utf-8").write(
        t.replace("<!--SIGNATURE-->", body))
    print("    Credits.html（含署名）")

def build_ack():
    """「致谢」按钮打开的是 Resources/Acknowledgments.txt（根目录，非本地化）。

    两边都写：根目录改成中英对照（兜底），同时在 zh-Hans.lproj 放一份
    （若代码走 bundle 本地化查找，则会优先命中）。
    """
    zh = "本产品包含开源软件。适用的许可证与版权信息，请参阅 Broadcom 客户支持门户。"
    en = ("This product incorporates open source software. For applicable license and\n"
          "copyright information, please refer to the Broadcom customer support portal.")
    sig = ""
    if SIG and os.path.exists(SIG):
        sig = "\n\n" + "\n".join(l for l in open(SIG, encoding="utf-8").read().strip().splitlines() if l.strip())
    text = zh + "\n\n" + en + sig + "\n"
    for path in (os.path.join(APP_RES, "Acknowledgments.txt"), os.path.join(OUT, "Acknowledgments.txt")):
        try:
            open(path, "w", encoding="utf-8").write(text)
        except PermissionError:
            print("    跳过 %s（权限不足）" % path)
    print("    Acknowledgments.txt（中英对照，已写入资源根目录与 zh-Hans）")


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    build_eula()
    build_credits()
    build_ack()
