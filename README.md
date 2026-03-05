# Outlook 股市法說會行事曆（台股/美股/日股/陸股）

這個小工具可以幫你產生一份可匯入 Outlook 的 `.ics` 行事曆檔，並用「市場分類」標記事件：

- 台股（TW）
- 美股（US）
- 日股（JP）
- 陸股（CN）

你可以在 Outlook 先建立對應分類並指定顏色，匯入後就能用不同顏色顯示不同市場。

---

## 1) 準備法說會資料（CSV）

請編輯 `stock_calendar/events.csv`，欄位如下：

- `subject`：事件標題（例如：TSMC Q2 Earnings Call）
- `market`：`TW` / `US` / `JP` / `CN`
- `date`：日期，格式 `YYYY-MM-DD`
- `time`：時間，格式 `HH:MM`（24 小時制）
- `timezone`：事件原始時區（例如 `Asia/Taipei`、`America/New_York`）
- `duration_minutes`：持續分鐘數（例如 `60`）
- `description`：備註（可留空）

> 時區請用 IANA 時區名稱，避免夏令時間換算錯誤。

---

## 2) 產生 ICS 檔

```bash
python3 scripts/generate_stock_calendar.py \
  --input stock_calendar/events.csv \
  --output stock_calendar/stock_earnings_calendar.ics
```

---

## 3) 匯入 Outlook（建立獨立行事曆）

1. 打開 Outlook（網頁版或桌面版）。
2. 建立一個新行事曆，例如：`Stock Earnings`。
3. 以「匯入」功能匯入 `stock_calendar/stock_earnings_calendar.ics`。

---

## 4) 設定不同市場不同顏色

### 建議分類與顏色

- `TW-Market`：綠色
- `US-Market`：藍色
- `JP-Market`：紫色
- `CN-Market`：紅色

本工具會在每筆事件中寫入 `CATEGORIES`：

- TW → `TW-Market`
- US → `US-Market`
- JP → `JP-Market`
- CN → `CN-Market`

在 Outlook 將這些分類指定顏色後，事件即可依市場顯示不同顏色。

---

## 5) 之後如何更新

- 每次更新 `events.csv` 後，重新執行腳本產生新的 `.ics`。
- 在 Outlook 重新匯入或覆蓋既有事件。

---

## 注意事項

- Outlook 對於 `CATEGORIES` 的顏色顯示，取決於你帳號中的分類設定。
- 法說會資料來源建議使用公司 IR 網站、交易所公告，或可信財經資料供應商。
