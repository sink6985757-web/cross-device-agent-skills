# Notion 空白環境建置

Source 可以準備 checkpoint，但不能在未授權帳號下建立 Notion workspace。

1. 執行 `connector-bootstrap`；確認 `.source/connectors/notion.json` 為 `NEEDS_SETUP`。
2. 使用 Notion connector 完成登入與授權。
3. 在使用者指定的 Knowledge Master 下建立或選擇專案頁；已有同主題、同週頁面時更新原 Page ID，不重複新增。
4. Prompt 頁只讀，不得修改內容或屬性。
5. 回讀頁面確認後執行：

```text
Source complete --connector notion --connector-status VERIFIED --external-id <page-id>
```

只把 Page ID／URL 寫入 canonical config 或 state；token、cookie 與裝置 cache 永不寫入專案。
