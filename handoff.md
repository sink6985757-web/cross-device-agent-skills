# 交接檔（handoff.md）

> 任何 Agent、任何電腦接手前**必讀**；收工時**必更新**。本檔只放交接必需的精簡資訊，詳細脈絡放 Obsidian（若有 L3），正式結論、決策、風險與狀態依 Knowledge Master 規則寫入 Notion（若有 L4）。

## ⏯️ 目前做到哪

已完成新電腦（DESKTOP-P5NQS9D）的 chezmoi 安裝與三技能部署：
- 安裝 chezmoi v2.71.1，初始化本機 source repo
- 將 project-init、startup、shutdown 部署到 `~/.agents/skills/`（chezmoi 管理）及 Hermes 技能目錄
- chezmoi source 已 push 到 GitHub `sink6985757-web/dotfiles`（master）

## 🚦 目前狀態

本機四層環境已就緒，可在 DESKTOP-P5NQS9D 上正常使用 project-init／startup／shutdown 三技能。同台電腦的下一對話可直接「開工」續接。跨電腦驗證尚未完成。

## ➡️ 下一步

1. 在另一台電腦執行 `chezmoi init --apply https://github.com/sink6985757-web/dotfiles.git`，拉取三技能
2. 實際執行一次完整的「開工→工作→收工」循環，驗證 L4 Notion 路由
3. 補測 `READ_ONLY` 零寫入與 `AUTO_SAVE` 同頁更新情境

## ⚠️ 注意事項

- 專案位於 Google 雲端硬碟；不要在兩台電腦同時編輯，以免產生衝突副本。
- Git 必須設定 `windows.appendAtomically=false`，避免 GDrive 同步造成寫入問題。
- `.env`、金鑰與 credentials 檔案不得提交。
- L4 每次必須重新讀取 Knowledge Master 共用公約與正式主題 Prompt；Prompt 頁只讀。
- 同週 `00_system` 只更新原 Page ID，不建立 v2／最新版／修正版。
- Notion 不得保存 Secret、Token、帳密、公司或客戶機密、裝置內部路徑與未公開技術內容。
- 本機無 Obsidian，L3 筆記待回有 Obsidian 的電腦補建。

## 🕐 最後更新

- 時間：2026-07-21 20:58
- 更新者：Hermes @ DESKTOP-P5NQS9D
- Git push：✅ 已推（cross-device-agent-skills main）
- Notion：`00_system｜未執行（Knowledge Master 不可讀，待回有 Notion connector 的電腦處理）`