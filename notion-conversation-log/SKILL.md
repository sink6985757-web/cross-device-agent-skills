---
name: notion-conversation-log
description: Source pipeline 的 Notion 對話紀錄相容入口。當對話結束需要保存正式成果或系統錯誤時使用；有 Source 專案就只完成 notion connector，沒有 Source 才依 Knowledge Master 即時規則分流，避免重複收件匣頁。
---

# Notion Conversation Log

1. 若專案有 `.source/config.json`，先看 notion checkpoint；`NEEDS_SETUP` 依 `../source/references/notion-bootstrap.md` 授權，否則只更新 Source 登記的同週唯一正式頁並回填 checkpoint。
2. 若沒有 Source，先用 Notion connector 重讀 Knowledge Master 與正式主題 Prompt；`READ_ONLY` 零寫入，其他依 `AUTO_SAVE` 更新唯一既有頁。
3. 只有未完成、無法分類或工具受阻時才進收件匣；system error 依目前 Knowledge Master 規則路由，不使用靜態 Page ID 取代即時權威。
4. 不直接讀 `.env` 或操作 API key；Prompt 頁只讀，不建立 v2／最新版／修正版。
