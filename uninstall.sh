#!/bin/bash
# VMware Fusion 26H1 简体中文补全 —— 回滚脚本
#   sudo ./uninstall.sh                 # 用最近一次备份还原
#   sudo ./uninstall.sh 20261029-103500 # 指定备份批次
#        ./uninstall.sh --target /tmp/X.app --no-sign --batch <名>
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
TARGET="/Applications/VMware Fusion.app"
SIGN=0   # 默认不签名
BATCH=""

while [ $# -gt 0 ]; do
  case "$1" in
    --target) TARGET="$2"; shift 2 ;;
    --resign) SIGN=1; shift ;;
    --batch) BATCH="$2"; shift 2 ;;
    -*) echo "未知参数: $1"; exit 1 ;;
    *) BATCH="$1"; shift ;;
  esac
done

LPRJ="$TARGET/Contents/Resources/zh-Hans.lproj"
if [ -z "$BATCH" ]; then
  BATCH="$(ls -1 "$HERE/backup" 2>/dev/null | sort | tail -1)"
fi
[ -n "$BATCH" ] && [ -d "$HERE/backup/$BATCH" ] || { echo "没有可用备份"; exit 1; }

if pgrep -f "VMware Fusion.app/Contents/MacOS/VMware Fusion" >/dev/null; then
  echo "==> 退出 VMware Fusion…"
  osascript -e 'tell application "VMware Fusion" to quit' >/dev/null 2>&1
  for _ in $(seq 1 30); do
    pgrep -f "VMware Fusion.app/Contents/MacOS/VMware Fusion" >/dev/null || break
    sleep 0.5
  done
fi

echo "==> 从 backup/$BATCH 还原到 $LPRJ"
cp -p "$HERE/backup/$BATCH"/*.strings "$LPRJ"/
if [ -f "$HERE/backup/$BATCH/Localizable.strings" ]; then
  cp -p "$HERE/backup/$BATCH/Localizable.strings" "$LPRJ"/
else
  rm -f "$LPRJ/Localizable.strings"
fi
BASEDIR="$TARGET/Contents/Resources/Base.lproj"
if [ -d "$HERE/backup/$BATCH/nib/duiSettingsViewBrowser.nib" ]; then
  rm -rf "$BASEDIR/duiSettingsViewBrowser.nib"
  cp -Rp "$HERE/backup/$BATCH/nib/duiSettingsViewBrowser.nib" "$BASEDIR"/
  echo "    已还原 Base.lproj/duiSettingsViewBrowser.nib"
fi

# 还原时删掉「原本不存在、由补丁新增」的文件
for f in "$HERE"/zh-Hans/*.strings; do
  b="$(basename "$f")"
  [ -f "$HERE/backup/$BATCH/$b" ] || { rm -f "$LPRJ/$b"; echo "    移除新增文件 $b"; }
done

for f in EULA.rtf Credits.html; do
  if [ -f "$HERE/backup/$BATCH/$f" ]; then cp -p "$HERE/backup/$BATCH/$f" "$LPRJ/$f"; else rm -f "$LPRJ/$f"; fi
done
if [ -f "$HERE/backup/$BATCH/Acknowledgments.txt.orig" ]; then
  cp -p "$HERE/backup/$BATCH/Acknowledgments.txt.orig" "$TARGET/Contents/Resources/Acknowledgments.txt"
fi
rm -f "$LPRJ/Acknowledgments.txt"
rm -rf "$TARGET/Contents/Library/messages/zh-Hans"
echo "    已移除 messages/zh-Hans"

if [ "$SIGN" = "1" ]; then
  echo "==> 重新签名"
  codesign --force --deep --sign - "$TARGET" 2>&1 | sed 's/^/    /'
  codesign --verify --verbose=2 "$TARGET" 2>&1 | tail -3 | sed 's/^/    /'
fi
echo "==> 回滚完成"
