# 批次重新命名研究報告

此專案提供 `rename_reports.py`，可掃描資料夾內的 PDF / Word 報告並嘗試改名為：

`ticker_股票名稱_日期_券商名稱`

例如：
- `2330_台積電_20260425_元大.pdf`
- `NVDA_NVIDIA_20260425_Morgan Stanley.docx`

## 安裝

```bash
pip install pypdf python-docx
```

## 用法

先預覽（不會改名）：

```bash
python rename_reports.py /path/to/reports
```

確認結果後正式套用：

```bash
python rename_reports.py /path/to/reports --apply
```

若目標檔名已存在且你想覆蓋：

```bash
python rename_reports.py /path/to/reports --apply --overwrite
```

## 備註

- `.pdf` 使用 `pypdf` 讀前兩頁文字。
- `.docx` 使用 `python-docx` 讀前 80 段。
- `.doc` 會先嘗試以文字方式讀取，若是二進位舊格式可能辨識率較差。
- 若無法完整擷取 `ticker/股票名稱/日期/券商名稱`，會略過並顯示原因。
