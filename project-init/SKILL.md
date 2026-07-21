---
name: project-init
description: 專案初始化技能（四層級自動偵測）。當使用者說「初始化專案」、「專案初始化」、「幫這個專案做初始化」、「開新專案」、「建立專案藍圖」、「幫我 init 專案」等要為當前資料夾建立專案基礎建設的請求時，請一定要使用此技能。本技能依工具鏈啟用 L1 本地、L2 GitHub、L3 Obsidian 與 L4 Notion Knowledge Master。
---

# 專案初始化技能（四層級自動偵測）

## 設計理念

一套技能、四個層級。**這台電腦接上什麼工具，就啟用哪些層級**——不用問使用者「你要第幾層級」。L4 可獨立於 L3 啟用；缺少中間工具時要優雅降級，不得阻止其他可用層級。

四層資訊的定位與讀取頻率不同：

| 層級 | 平台 | 建立的東西 | 讀取時機 |
|------|------|-----------|---------|
| L1 本地 | 專案資料夾（建議放 GDrive） | `agents.md`（專案藍圖）＋`handoff.md`（交接檔） | **每個 session 都讀** |
| L2 GitHub | 私有 repo | git 版本控制＋雲端備份 | 指定才讀 |
| L3 Obsidian | 第二大腦 vault | `專案工作流程.md`（詳細筆記） | 有需要才讀 |
| L4 Notion | Knowledge Master | 正式主題的 Prompt 與唯一週期紀錄 | 先讀規則；成果依 ACTION 寫回 |

> 為什麼藍圖叫 `agents.md` 而不是 `CLAUDE.md`？因為 AGENTS.md 是跨 Agent 開放標準——Claude Code、Codex、Gemini CLI、OpenCode 都讀得懂。專案層的檔案刻意用開放格式，任何 Agent 接手都能無縫工作。

## 層級偵測（初始化看「這台電腦」有什麼）

依序檢查，決定本次能建到第幾層級：

1. **L1**：無條件可建
2. **L2**：跑 `gh auth status`，成功（已登入 GitHub CLI）→ 可建
3. **L3**：Obsidian MCP 工具（`mcp__obsidian__*`）可用 → 可建
4. **L4**：Notion 工具可用，且能讀取下列權威入口 → 可建
   - Knowledge Master：`https://app.notion.com/p/6474dc5067fa49a98a339275ab8a8539`

檢查完先告訴使用者可啟用哪些層級，再開始執行。若 Notion 工具存在但權威入口讀取失敗，L4 標示 `BLOCKED`，不可猜測規則或改寫其他頁代替。

## L4 Knowledge Master 治理不變條件

L4 的權威規則永遠以 Knowledge Master 當下內容為準；本技能只保存必要的執行護欄，不能用靜態副本取代即時讀取。

1. 每次 L4 操作先讀 Knowledge Master 共用公約，再判斷唯一正式主題並讀取其 `Prompt｜主題`；Prompt 頁只讀。
2. 使用者未明確指定 `READ_ONLY`／不要寫入時，完成可重用的查詢、分析、整理、規劃或產出後，ACTION 預設為 `AUTO_SAVE`。
3. 寫入前以 Asia/Taipei 日期決定週次，搜尋同事件、同期間、同主題紀錄；存在就更新原 Page ID，不存在才建立 `YYYY-Www｜正式主題`。
4. 有正式主題就直接寫入該主題；只有未完成、無法分類、來源不足或工具受阻時才寫入 `90_index` 的收件匣，並標示 `PARTIAL`／`BLOCKED`。
5. Google Drive 保存原始檔、附件、程式、資料集與大型輸出；Notion 只保存正式結論、索引、決定、風險與狀態。
6. 不寫入 Secret、Token、帳密、公司或客戶機密、裝置內部路徑及未公開技術內容；事實、推論與缺口分開，狀態只能是 `VERIFIED`、`PARTIAL` 或 `BLOCKED`。
7. 完成回報固定包含：判斷主題｜ACTION｜寫入位置｜頁面標題｜新增或更新｜狀態。

## 初始化 SOP（依序執行）

### L1：本地藍圖（永遠執行）

1. **掃描資料夾現況**：列出既有檔案，若已有 `agents.md` 或 `handoff.md` → 停下來問使用者是否要覆蓋
2. **詢問使用者**：專案名稱、一句話目標、關鍵時程（沒有就留白，不要硬編）
3. **建立 `agents.md`**：用 `templates/agents.template.md` 為底，填入實際內容；「資料夾結構」區塊由掃描結果自動生成
4. **建立 `handoff.md`**：用 `templates/handoff.template.md` 為底，「目前做到哪」填「專案初始化完成」，更新者填 Agent 名＋電腦名（PowerShell 用 `$env:COMPUTERNAME` 取得）
5. 若路徑含「雲端硬碟」或「My Drive」→ 提醒使用者確認 Google 雲端硬碟桌面版的同步圖示已打勾（檔案要真的躺在雲端，換電腦才拿得到）

### L2：GitHub（gh 已登入才做，否則跳過並註明）

6. **git 初始化**：
   ```bash
   git init
   git config user.email "<你的email>"
   git config user.name "<你的GitHub帳號>"
   git config windows.appendAtomically false   # GDrive 上跑 git 的必要設定，避免寫入錯誤
   ```
7. **建立 `.gitignore`**（GDrive 專用）：
   ```
   desktop.ini
   *.tmp
   ~$*
   .env
   *.key
   credentials.*
   ```
8. **初始 commit**：`git add .` → `git commit -m "初始化專案：<專案名稱>"`
9. **建立私有 repo**：問使用者偏好的英文 repo 名，然後
   ```bash
   gh repo create <你的GitHub帳號>/<repo-name> --private --source=. --push
   ```
10. **回填 `agents.md`** 同步層級表的 GitHub 欄（repo 網址）

### L3：Obsidian（MCP 可用才做，否則跳過並註明）

11. 在 vault 根目錄建立與專案資料夾**同名**的資料夾
12. 建立 `<資料夾名>/專案工作流程.md`，內容包含：專案背景與詳細脈絡、決策紀錄（為什麼這樣做）、素材與相關筆記連結、🕳️ 踩坑筆記、🗓️ 最近更動紀錄表格（第一行寫今天的初始化）
13. **回填 `agents.md`** 同步層級表的 Obsidian 欄（vault 內路徑）

### L4：Notion Knowledge Master（可讀權威入口才做）

14. 重新讀取 Knowledge Master 共用公約，依專案主要目的判斷唯一正式主題；專案治理、同步、備份與 Agent 工作流預設路由到 `00_system`，其他專案不得硬套此主題
15. 讀取正式主題下唯一 `Prompt｜主題`，只作規則輸入，**不得修改 Prompt 頁**
16. 以 Asia/Taipei 日期計算 `YYYY-Www`，搜尋該主題同週唯一週期頁：
    - 已存在 → 保留 Page ID 與未要求變更的內容，更新初始化成果、決策、風險與下一步
    - 不存在 → 在正式主題下建立 `YYYY-Www｜正式主題`
17. 寫入內容只放可重用的正式結果與 Google Drive／GitHub 連結，不放 Secret、Token、帳密或裝置內部路徑；標示 `VERIFIED`／`PARTIAL`／`BLOCKED`
18. **回填 `agents.md`** 的 L4 欄、正式主題與主 Prompt；在 `handoff.md` 記錄 Notion ACTION、頁名、更新／新增及狀態

### 回報

給使用者一個層級 checklist：

```
🏗️ 本專案初始化至第 N 層級
✅ L1 本地：agents.md ＋ handoff.md
✅ L2 GitHub：<你的GitHub帳號>/<repo>（私有）
⚠️ L3 Obsidian：未建（這台電腦沒有 Obsidian MCP，之後可在有 Obsidian 的電腦說「補建第三層級」）
✅ L4 Notion：<正式主題>｜AUTO_SAVE｜<寫入位置>｜<頁面標題>｜<新增或更新>｜<狀態>
```

## 不該做的事

- ❌ 未經確認就覆蓋既有的 `agents.md`／`handoff.md`
- ❌ 電腦沒 gh／Obsidian／Notion 時報錯中斷（正確行為：跳過該層級、在回報中註明原因）
- ❌ 把 `.env`、API key 之類敏感檔 commit 進 git
- ❌ 建 public repo（預設一律 private，使用者明說才轉公開）
- ❌ 修改 `Prompt｜…`、建立 v2／最新版／修正版或同週重複 Notion 紀錄
- ❌ 未先讀 Knowledge Master 共用公約與主 Prompt 就寫 Notion，或在 `READ_ONLY` 下建立 Log

## 注意事項

- 所有訊息與檔案內容使用**繁體中文**
- 本 skill 在 `~/.claude-skills/`，搭配 chezmoi 跨電腦同步；修改後記得 `chezmoi re-add ~/.claude-skills/project-init/`
- 之後的日常循環交給搭檔技能：開工（startup）續接、收工（shutdown）同步；兩者的 L4 行為都必須遵守 Knowledge Master ACTION 與週期合併規則
