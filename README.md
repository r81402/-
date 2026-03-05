# 給完全新手：Outlook 股市法說會行事曆（超簡單版）

你要的效果是：
- 在 Outlook 裡有一個「獨立」行事曆（例如叫 `Stock Earnings`）
- 裡面有台股/美股/日股/陸股法說會時間
- 不同市場用不同顏色

下面照著做就好，不需要懂程式。

---

## 你只要做 3 件事

1. 填資料（CSV）
2. 按一個指令產生行事曆檔（ICS）
3. 匯入 Outlook + 設定顏色

---

## 第 0 步：先確認你有檔案

你目前專案裡要有這 2 個檔案：

- `stock_calendar/events.csv`（你要填寫的法說會清單）
- `scripts/generate_stock_calendar.py`（幫你轉檔的工具）

---

## 第 1 步：打開並填寫 `events.csv`

打開 `stock_calendar/events.csv`，每一行是一個法說會。

欄位意思（照順序）：

- `subject`：標題（例：TSMC Q2 Earnings Call）
- `market`：市場（只能填 `TW` / `US` / `JP` / `CN`）
- `date`：日期（格式 `2026-07-16`）
- `time`：時間（24 小時制，格式 `14:00`）
- `timezone`：時區（例：`Asia/Taipei`、`America/New_York`）
- `duration_minutes`：持續幾分鐘（例：`60`）
- `description`：備註（可空白）

> 重點：日期、時間格式一定要照上面。

---

## 第 2 步：產生 Outlook 可匯入檔（ICS）

在專案資料夾開啟終端機，貼上這行：

```bash
python3 scripts/generate_stock_calendar.py --input stock_calendar/events.csv --output stock_calendar/stock_earnings_calendar.ics
```

看到這句就成功：

`Generated stock_calendar/stock_earnings_calendar.ics with X events.`

---

## 第 3 步：匯入 Outlook（建立獨立行事曆）

### Outlook 網頁版（建議）

1. 打開 Outlook 行事曆。
2. 左側選「新增行事曆」，名稱填：`Stock Earnings`。
3. 找到「匯入行事曆 / Import calendar」。
4. 上傳檔案：`stock_calendar/stock_earnings_calendar.ics`。
5. 匯入目標行事曆選剛剛建的 `Stock Earnings`。

### Outlook 桌面版

1. 開啟 Outlook 行事曆。
2. 新增行事曆（名稱 `Stock Earnings`）。
3. 用「匯入」功能匯入 `stock_earnings_calendar.ics`。

---

## 第 4 步：設定不同市場不同顏色

這個工具已經幫你把分類寫好了：

- `TW-Market`（台股）
- `US-Market`（美股）
- `JP-Market`（日股）
- `CN-Market`（陸股）

你只要在 Outlook 的「分類」中幫它們上色，例如：

- `TW-Market` → 綠色
- `US-Market` → 藍色
- `JP-Market` → 紫色
- `CN-Market` → 紅色

設定一次就好，之後事件會自動顯示顏色。

---

## 以後更新（超簡單）

每次你有新法說會：

1. 改 `events.csv`
2. 重跑一次第 2 步指令
3. 重新匯入 Outlook

---

## 最常見 3 個錯誤（直接對照）

1. **跑指令失敗：找不到 python3**
   - 先安裝 Python 3，或改用 `python` 試試看。

2. **時間跑掉**
   - `timezone` 要填正確（例如台灣要用 `Asia/Taipei`）。

3. **沒有顏色**
   - 需要在 Outlook 手動把 `TW-Market` / `US-Market` / `JP-Market` / `CN-Market` 指定顏色。

---

## 檔案說明

- `stock_calendar/events.csv`：你的事件清單（你最常改這個）
- `scripts/generate_stock_calendar.py`：轉檔工具
- `stock_calendar/stock_earnings_calendar.ics`：產生給 Outlook 匯入的檔案
