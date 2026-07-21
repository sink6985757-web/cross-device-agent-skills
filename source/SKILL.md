---
name: source
description: 單一入口的專案生命週期技能。當使用者說 source、初始化、開工、收工、繼續、下一步、工作到哪、換電腦、部署技能或同步專案時使用。以可恢復狀態機統一初始化、續接、GitHub、技能部署、chezmoi、Obsidian、Notion 與可選 CDN connector。
---

# Source

以腳本為準，不在對話中重寫整套 SOP。

## 執行

1. 在專案根目錄執行 `./source.ps1`；若根目錄沒有 launcher，執行本 Skill 的 `scripts/source.ps1`。
2. 無參數時讓腳本依狀態自動選擇：未初始化 → `init`；`READY` → `start`；工作中或中斷 → `next`。
3. 明確口令對應：初始化 → `init`、開工 → `start`、收工 → `finish`、下一步／工作到哪 → `next`。
4. 只依 `.source/config.json` 與 `.source/state.json` 判斷狀態；不得手工臆測已完成步驟。

```powershell
./source.ps1                         # 自動初始化／開工／續接
./source.ps1 -Action doctor          # 權限、工具與狀態檢查
./source.ps1 -Action finish -CommitMessage "完成具體成果"
```

## 外部 Connector

腳本能直接處理本地、Git、GitHub、技能安裝與 chezmoi。若狀態顯示 `PENDING_AGENT`，才讀 [connectors.md](references/connectors.md)，完成 Notion／Obsidian／CDN 動作後執行：

```powershell
./source.ps1 -Action complete -Connector notion -ConnectorStatus VERIFIED
```

## 不變條件

- 不覆寫既有檔案；衝突先備份或標示 `BLOCKED`。
- 不自動 `git pull`，不提交未知 untracked 或敏感檔。
- 私有 repo 為預設；權限不足時保存 checkpoint 與唯一下一步。
- Prompt 頁只讀；Notion 同主題同週只更新原 Page ID。
- canonical 檔只保存 root-relative 路徑；裝置絕對路徑只在執行時解析。
- 外部副作用需符合使用者本次授權；未授權時只輸出 dry-run／下一步。
