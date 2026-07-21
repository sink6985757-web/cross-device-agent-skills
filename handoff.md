# 交接檔（handoff.md）

> 任何 Agent、任何電腦接手前**必讀**；收工時**必更新**。本檔只放交接必需的精簡資訊，詳細脈絡放 Obsidian。

## ⏯️ 目前做到哪

已完成 L4 Knowledge Master 整合與名稱統一，更新 `project-init`、`startup`、`shutdown`、初始化範本、README、專案藍圖及 Obsidian。三個 Skill 亦已同步到 `~/.agents/skills` 並交由 chezmoi 管理；本週仍更新唯一 Notion 正式紀錄 `2026-W30｜00_system`，Prompt 修改數為 0。

## 🚦 目前狀態

本地四層流程與跨 Agent 共用主庫均已完成；Knowledge Master 標題與共用公約已使用新名稱，Prompt 保持只讀。GitHub 與 Notion 正在執行本次正式收工同步，驗證通過後回填最終 commit 與狀態。

## ➡️ 下一步

1. 在另一台電腦執行 `chezmoi init --apply sink6985757-web`，驗證 10 個共用 Skill 與各 Agent adapter。
2. 在另一個 Agent 上測試初始化、開工與收工的 L4 路由。
3. 分別驗證一次明確 `READ_ONLY` 的零寫入與 `AUTO_SAVE` 的同頁更新。

## ⚠️ 注意事項

- 專案位於 Google 雲端硬碟；不要在兩台電腦同時編輯，以免產生衝突副本。
- Git 必須設定 `windows.appendAtomically=false`，避免 GDrive 同步造成寫入問題。
- `.env`、金鑰與 credentials 檔案不得提交。
- L4 每次必須重新讀取 Knowledge Master 共用公約與正式主題 Prompt；Prompt 頁只讀；Prompt 目前仍有舊名稱文字，未經獨立授權不得修改。
- 同週 `00_system` 只更新 [2026-W30｜00_system](https://app.notion.com/p/3a4367cc4e4c81239ac3d61ce049d370) 原 Page ID，不建立 v2／最新版／修正版。
- Notion 不得保存 Secret、Token、帳密、公司或客戶機密、裝置內部路徑與未公開技術內容。

## 🕐 最後更新

- 時間：2026-07-21 20:25
- 更新者：Codex @ YULIN-SFG16-72
- Git push：⏳ 待推（技能專案與 dotfiles 名稱同步）
- Notion：`00_system｜AUTO_SAVE｜2026-W30｜00_system｜待更新`
