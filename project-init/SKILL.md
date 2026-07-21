---
name: project-init
description: Source pipeline 的初始化相容入口。當使用者說初始化專案、開新專案、建立專案藍圖或 init 專案時使用；把執行交給 source 狀態機，不重複載入完整 SOP。
---

# Project Init

1. 讀取 `../source/SKILL.md`。
2. 全新多專案環境執行 `hub-init`，再用 `child-create --child-name <名稱>` 建立隔離子專案；單一既有專案才用 `init`。
3. 已初始化時只顯示狀態，不覆寫；空白 Obsidian 建本地 vault，空白 Notion 留 `NEEDS_SETUP`，不得假裝已授權。
4. 依腳本 checkpoint 處理權限或 connector 缺口。
