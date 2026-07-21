---
name: project-init
description: Source pipeline 的初始化相容入口。當使用者說初始化專案、開新專案、建立專案藍圖或 init 專案時使用；把執行交給 source 狀態機，不重複載入完整 SOP。
---

# Project Init

1. 讀取 `../source/SKILL.md`。
2. 執行專案根目錄 `./source.ps1 -Action init`；沒有 launcher 時執行 `../source/scripts/source.ps1 -Action init -ProjectRoot <root>`。
3. 已初始化時只顯示狀態，不覆寫。
4. 依腳本 checkpoint 處理權限或 connector 缺口。
