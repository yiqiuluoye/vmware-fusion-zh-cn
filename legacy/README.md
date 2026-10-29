# legacy

早期按批次拆分的一次性构建脚本（gen_patch*.py / gen_vmsg.py / translations_v*.py）
以及最初的 install.sh / uninstall.sh。

**不再需要**：`fzp.py` 是唯一入口，产物（`vmsg/`、`zh-Hans/`、`merge/`、`v2/`）已经是
可直接维护的数据文件。若要从零重建译文，可参考这里的字典；否则可以整个目录删掉。
