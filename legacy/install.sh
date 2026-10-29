#!/bin/bash
# VMware Fusion 26H1 简体中文补全 —— 安装脚本
#
#   sudo ./install.sh                 # 装到 /Applications/VMware Fusion.app（需退出 Fusion）
#        ./install.sh --target /tmp/X.app --no-sign   # 装到副本、不重签名（测试用）
#   sudo ./uninstall.sh               # 从 backup/ 还原
#
# 做的事：① 补 21 个整缺的 .strings；② 给 6 个文件补 19 条缺失 key；
#         ③ 修复 1 个「BOM 与内容编码不符」导致整表失效的文件；④ 重新做 ad-hoc 签名。
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
TARGET="/Applications/VMware Fusion.app"
SIGN=0   # 默认不签名：只替换 .strings 资源不会影响可执行文件签名与 entitlements
QUIT=1

while [ $# -gt 0 ]; do
  case "$1" in
    --target) TARGET="$2"; QUIT=0; shift 2 ;;
    --resign) SIGN=1; shift ;;
    --no-quit) QUIT=0; shift ;;
    *) echo "未知参数: $1"; exit 1 ;;
  esac
done

LPRJ="$TARGET/Contents/Resources/zh-Hans.lproj"
BASEDIR="$TARGET/Contents/Resources/Base.lproj"
MSGDIR="$TARGET/Contents/Library/messages/zh-Hans"
[ -d "$LPRJ" ] || { echo "找不到 $LPRJ"; exit 1; }

if [ "$QUIT" = "1" ]; then
  if pgrep -f "VMware Fusion.app/Contents/MacOS/VMware Fusion" >/dev/null; then
    echo "==> 退出 VMware Fusion…"
    osascript -e 'tell application "VMware Fusion" to quit' >/dev/null 2>&1
    for _ in $(seq 1 30); do
      pgrep -f "VMware Fusion.app/Contents/MacOS/VMware Fusion" >/dev/null || break
      sleep 0.5
    done
    pgrep -f "VMware Fusion.app/Contents/MacOS/VMware Fusion" >/dev/null && {
      echo "Fusion 仍在运行，请手动退出后重试（虚拟机正在运行的话先关机）"; exit 1; }
  fi
fi

STAMP="$(date +%Y%m%d-%H%M%S)"
BAK="$HERE/backup/$STAMP"
mkdir -p "$BAK"
echo "==> 备份原文件到 $BAK"
for f in "$HERE"/zh-Hans/*.strings; do
  b="$(basename "$f")"
  [ -f "$LPRJ/$b" ] && cp -p "$LPRJ/$b" "$BAK/$b"
done
for f in "$HERE"/merge/*.append.strings; do
  b="$(basename "$f" .append.strings).strings"
  cp -p "$LPRJ/$b" "$BAK/$b"
done
# v2：设置窗口相关（nib 与两张额外的表）
cp -p "$LPRJ/duiSettingsViewBrowser.strings" "$BAK/" 2>/dev/null
if [ -f "$LPRJ/Localizable.strings" ]; then cp -p "$LPRJ/Localizable.strings" "$BAK/"; fi
if [ -d "$BASEDIR/duiSettingsViewBrowser.nib" ]; then
  mkdir -p "$BAK/nib"
  cp -Rp "$BASEDIR/duiSettingsViewBrowser.nib" "$BAK/nib/"
  cp -Rp "$BASEDIR/plSettingsViewAddDevice.nib" "$BAK/nib/" 2>/dev/null
fi
ls "$BAK" | wc -l | xargs echo "    备份条目数:"

echo "==> 写入中文资源"
cp "$HERE"/zh-Hans/*.strings "$LPRJ"/

echo "==> v2：设置窗口文案 + 分组标题"
cp "$HERE/v2/Localizable.strings" "$LPRJ"/Localizable.strings
python3 - "$HERE" "$LPRJ" <<'PY'
import sys, os, re
HERE, LPRJ = sys.argv[1], sys.argv[2]
add = open(os.path.join(HERE, "v2", "duiSettingsViewBrowser.extra.strings"), encoding="utf-8").read()
body = add.split("*/", 1)[1].strip()
tgt = os.path.join(LPRJ, "duiSettingsViewBrowser.strings")
def dec(b):
    if b[:2] in (b"\xff\xfe", b"\xfe\xff"):
        try:
            t = b[2:].decode("utf-8")
            if "\x00" not in t: return t
        except UnicodeDecodeError: pass
        return b.decode("utf-16")
    if b[:3] == b"\xef\xbb\xbf": return b[3:].decode("utf-8")
    try:
        t = b.decode("utf-8")
        if "\x00" not in t: return t
    except UnicodeDecodeError: pass
    return b.decode("utf-16-le", errors="replace")
cur = dec(open(tgt, "rb").read()) if os.path.exists(tgt) else ""
have = set(re.findall(r'^"([^"]+)"\s*=', cur, re.M))
lines = [l for l in body.splitlines() if re.match(r'^"[^"]+"\s*=', l) and re.findall(r'^"([^"]+)"', l)[0] not in have]
open(tgt, "w", encoding="utf-8").write(cur.rstrip("\n") + "\n\n" + "\n".join(lines) + "\n")
print("    并入 duiSettingsViewBrowser 表 %d 条" % len(lines))
PY
echo "==> v4：生成中英对照的法律文本（EULA / 商标声明）"
for f in EULA.rtf Credits.html; do
  [ -f "$LPRJ/$f" ] && cp -p "$LPRJ/$f" "$BAK/$f"
done
[ -f "$TARGET/Contents/Resources/Acknowledgments.txt" ] && \
  cp -p "$TARGET/Contents/Resources/Acknowledgments.txt" "$BAK/Acknowledgments.txt.orig"
python3 "$HERE/legal/build_legal.py" "$TARGET/Contents/Resources" "$LPRJ" "$HERE/signature.txt" || \
  echo "    （法律文本生成失败，跳过；不影响其余汉化）"

echo "==> v3：写入消息目录 messages/zh-Hans/vmware.vmsg"
mkdir -p "$MSGDIR"
cp "$HERE/vmsg/vmware.vmsg" "$MSGDIR/vmware.vmsg"
echo "    $(grep -c ' = ' "$MSGDIR/vmware.vmsg") 条消息"
python3 "$HERE/legal/apply_signature.py" "$MSGDIR/vmware.vmsg" "$HERE/signature.txt"
if [ -d "$HERE/v2/duiSettingsViewBrowser.nib" ]; then
  rm -rf "$BASEDIR/duiSettingsViewBrowser.nib"
  cp -Rp "$HERE/v2/duiSettingsViewBrowser.nib" "$BASEDIR/"
  echo "    nib 已替换（分组标题改为走本地化表）"
fi

python3 - "$HERE" "$LPRJ" <<'PY'
import sys, os
HERE, LPRJ = sys.argv[1], sys.argv[2]

def decode(b):
    """健壮解码：处理 BOM 与内容编码不一致的坏文件。"""
    if b[:2] == b"\xff\xfe" or b[:2] == b"\xfe\xff":
        # 优先按 UTF-8 试（坏文件特征：UTF-16 BOM + UTF-8 内容）
        try:
            t = b[2:].decode("utf-8")
            if "\x00" not in t:
                return t, "utf-8(去伪BOM)"
        except UnicodeDecodeError:
            pass
        return b.decode("utf-16"), "utf-16"
    if b[:3] == b"\xef\xbb\xbf":
        return b[3:].decode("utf-8"), "utf-8(去BOM)"
    try:
        t = b.decode("utf-8")
        if "\x00" not in t:
            return t, "utf-8"
    except UnicodeDecodeError:
        pass
    for enc in ("utf-16-le", "utf-16-be"):
        try:
            t = b.decode(enc)
            if "\x00" not in t:
                return t, enc
        except Exception:
            pass
    raise SystemExit("无法识别编码: %s" % LPRJ)

for fn in sorted(os.listdir(os.path.join(HERE, "merge"))):
    if not fn.endswith(".append.strings"):
        continue
    tgt = os.path.join(LPRJ, fn[: -len(".append.strings")] + ".strings")
    add = open(os.path.join(HERE, "merge", fn), encoding="utf-8").read()
    body = add.split("*/", 1)[1].strip()
    txt, how = decode(open(tgt, "rb").read())
    merged = txt.rstrip("\n") + "\n\n" + body + "\n"
    open(tgt, "w", encoding="utf-8").write(merged)
    print("    合并 %-46s (原编码 %s)" % (fn[: -len(".append.strings")], how))
PY

echo "==> 校验 strings 语法"
FAIL=0
for f in "$LPRJ"/*.strings "$BASEDIR/duiSettingsViewBrowser.nib/keyedobjects.nib"; do
  plutil -lint "$f" >/dev/null 2>&1 || { echo "    语法错误: $(basename "$f")"; FAIL=1; }
done
[ "$FAIL" = "0" ] || { echo "校验失败，请用 uninstall.sh 回滚"; exit 1; }
echo "    全部通过"

if [ "$SIGN" = "1" ]; then
  echo "==> 重新签名（ad-hoc）——注意：会丢掉 hypervisor / device-access 等 entitlements"
  echo "    除非系统拒绝启动，否则不要用这个开关"
  codesign -d --entitlements :- "$TARGET" > "$BAK/../entitlements-$STAMP.plist" 2>/dev/null
  codesign --force --deep --sign - --entitlements "$BAK/../entitlements-$STAMP.plist" "$TARGET" 2>&1 | sed 's/^/    /'
  codesign --verify --verbose=2 "$TARGET" 2>&1 | tail -3 | sed 's/^/    /'
fi

echo
echo "==> 完成。打开 Fusion 验证："
echo "    open -a \"$TARGET\""
echo "    回滚：sudo $HERE/uninstall.sh"
