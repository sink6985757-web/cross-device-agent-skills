# 交接檔（handoff.md）

> 任何 Agent、任何電腦接手前**必讀**；收工時**必更新**。本檔只放交接必需的精簡資訊，詳細脈絡放 Obsidian（若有 L3），正式結論、決策、風險與狀態依 Knowledge Master 規則寫入 Notion（若有 L4）。

## ⏯️ 目前做到哪

已由 Codex 在 YULIN-SFG16-72 接續 Hermes 於 DESKTOP-P5NQS9D 的交接，實際完成一次「開工→工作→收工」跨電腦、跨 Agent 循環：

- 開工時讀取 L1 交接、確認 L2 Git 遠端同步，並重新讀取 L4 Knowledge Master 與主 Prompt
- 工作階段驗證三個 repo Skill 與 `~/.agents/skills` 正式安裝版 SHA-256 一致，frontmatter 與治理護欄全數通過
- 收工更新 L1 藍圖與交接、L3 Obsidian 詳細紀錄，並把 L4 開工檢查點更新回同一個 W30 Page ID

## 🚦 目前狀態

跨電腦與跨 Agent 的完整循環已驗證通過；Git diff 檢查通過、敏感檔名掃描為 0，Prompt 修改數為 0。L1～L4 均可續接，本次 Git push 與 L4 最終回讀正在收工流程中完成。

## ➡️ 下一步

1. 補測明確 `READ_ONLY` 的 Notion 零寫入情境
2. 在一次後續 `AUTO_SAVE` 中再次確認同週同頁最小更新
3. 視需要在拋棄式測試專案跑一次 `project-init` 初始化驗證

## ⚠️ 注意事項

- 專案位於 Google 雲端硬碟；不要在兩台電腦同時編輯，以免產生衝突副本。
- Git 必須設定 `windows.appendAtomically=false`，避免 GDrive 同步造成寫入問題。
- `.env`、金鑰與 credentials 檔案不得提交。
- L4 每次必須重新讀取 Knowledge Master 共用公約與正式主題 Prompt；Prompt 頁只讀。
- 同週 `00_system` 只更新原 Page ID，不建立 v2／最新版／修正版。
- 目前 PowerShell 缺少 `System.Globalization.ISOWeek` 型別；週次計算改用 `Calendar.GetWeekOfYear` 相容路徑。

## 🕐 最後更新

- 時間：2026-07-21 21:47
- 更新者：Codex @ YULIN-SFG16-72
- Git push：待推（cross-device-agent-skills main）
- Notion：`00_system｜AUTO_SAVE｜2026-W30｜00_system｜待完成收工更新`
