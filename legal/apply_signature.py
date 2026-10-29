#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把署名追加到「关于 VMware Fusion」窗口的版权段落末尾。

做法：改写已安装的 messages/zh-Hans/vmware.vmsg 里
msg.mac.aboutBox.trademarkGeneral 这一条，追加「（中文本地化：xxx）」。
幂等：已在文中则跳过。
"""
import os, re, sys

vmsg, sig = sys.argv[1], sys.argv[2]
KEY = "msg.mac.aboutBox.trademarkGeneral"

sig_line = ""
if os.path.exists(sig):
    for line in open(sig, encoding="utf-8"):
        if line.strip():
            sig_line = line.strip()
            break
if not sig_line:
    sys.exit(0)

text = open(vmsg, encoding="utf-8").read()
m = re.search(r'^%s = "(.*)"$' % re.escape(KEY), text, re.M)
if not m:
    print("    跳过署名：消息目录里没有 %s" % KEY)
    sys.exit(0)
if sig_line in m.group(1):
    print("    署名已在关于窗口文案中")
    sys.exit(0)

new_val = m.group(1) + "（%s）" % sig_line
text = text[:m.start()] + '%s = "%s"' % (KEY, new_val) + text[m.end():]
open(vmsg, "w", encoding="utf-8").write(text)
print("    署名已写入关于窗口：…（%s）" % sig_line)
