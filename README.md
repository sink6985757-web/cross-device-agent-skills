# 跨電腦專案管理三技能 × 四層級（cross-device-agent-skills）

> 三師爸「AI Agent 基本功」EP06 懶人包：讓你的專案在**任何電腦、任何 Agent** 之間無縫接續。
> 三個口令搞定一切：「**初始化專案**」「**開工**」「**收工**」。

## 這包裡有什麼

| 技能 | 口令 | 做什麼 |
|------|------|--------|
| `project-init` | 「初始化專案」 | 建立本地藍圖與交接檔，自動接上 GitHub、Obsidian 與 Notion Knowledge Master |
| `startup` | 「開工」 | 讀取上次進度、git 狀態及 L4 正式主題規則，產生可續接的下一步 |
| `shutdown` | 「收工」 | 更新交接、commit + push、補 Obsidian 細節，並依 Knowledge Master 規則合併到 Notion 正式週期紀錄 |

## 四個層級：工具接到哪，技能就做到哪

這三個技能會**自動偵測**你的工具鏈，不用選版本：

| 層級 | 需要安裝 | 你會得到 |
|------|---------|---------|
| **L1 本地** | 什麼都不用（建議專案放 Google 雲端硬碟資料夾） | `agents.md`＋`handoff.md`，跨電腦靠雲端硬碟同步 |
| **L2 +GitHub** | [GitHub CLI](https://cli.github.com/)（`gh auth login` 登入） | 版本控制＋雲端備份，貼網址就能分享專案 |
| **L3 +Obsidian** | Obsidian＋Obsidian MCP | 專案詳細筆記（第二大腦） |
| **L4 +Notion** | Notion connector，且可讀 [Knowledge Master](https://app.notion.com/p/6474dc5067fa49a98a339275ab8a8539) | 依唯一正式主題與主 Prompt 保存結論、決策、風險、狀態與週期紀錄 |

四層資訊各有不同責任——這是整套設計的核心：

- `agents.md`＋`handoff.md`：**每個 session 都讀**（放交接必需的精簡資訊）
- GitHub：**指定才讀**（備份與歷史）
- Obsidian：**有需要才讀**（完整脈絡與細節）
- Notion：**先讀治理規則再寫正式成果**（同事件、同期間、同主題只保留一頁）

L4 不複製一套靜態規則：每次執行都以 Knowledge Master 的共用公約與對應 `Prompt｜主題` 為權威。除非使用者明確指定 `READ_ONLY`／不要寫入，完成可重用的查詢、分析、規劃或產出後，預設 `AUTO_SAVE`。

## 安裝

```bash
git clone https://github.com/sink6985757-web/cross-device-agent-skills.git
```

把 `project-init/`、`startup/`、`shutdown/` 三個資料夾複製到你的全域技能目錄：

- Claude Code：`~/.claude/skills/`

然後跟你的 Agent 說一句：

> 「把剛裝的三個技能裡的 `<你的GitHub帳號>` 和 `<你的email>` 占位符，換成我的 GitHub 帳號和 email」

（只有 `project-init` 會用到，L1 使用者可跳過這步。）

若要啟用 L4，請另外連接 Notion，並確認 Agent 可讀 Knowledge Master。Notion 內的 Prompt 頁維持只讀；技能只建立或更新正式紀錄。

## 典型的一天

```
早上（家裡電腦）
  你：「開工」
  Agent：📂 專案 xxx（第 4 層級）
         📘 上次做到哪：完成了報名表單（昨天 22:10，Claude Code @ 學校電腦）
         ⚠️ 上次在另一台電腦收工，GDrive 已同步完成
         🧭 Notion：00_system｜AUTO_SAVE｜2026-W30｜00_system｜VERIFIED
         ➡️ 建議下一步：1. 接 Firebase 寫入 …

  （工作中……）

晚上
  你：「收工」
  Agent：✅ L1：agents.md 進度已更新、handoff.md 已改寫
         ✅ L2：已 commit + push「新增報名表單 Firebase 寫入」
         ✅ L4：00_system｜AUTO_SAVE｜更新 2026-W30｜00_system｜VERIFIED
```

## 兩個核心檔案

- **`agents.md`**（專案藍圖）：用 AGENTS.md 開放標準命名——Claude Code、Codex、Gemini CLI、OpenCode 都讀得懂，換 Agent 不用改檔案
- **`handoff.md`**（交接檔）：記錄「目前做到哪／下一步／注意事項／**最後更新者＋電腦名＋有沒有 push**」。不管是**換電腦**還是**換 Agent** 接手，都先讀這個檔

範本在 `project-init/templates/`，初始化技能會自動套用。

## 常見問題

**Q：專案資料夾一定要放 Google 雲端硬碟嗎？**
L1 的跨電腦同步就是靠雲端硬碟桌面版（要裝應用程式，不能只用網頁版）。不放 GDrive 也能用這三個技能，但跨電腦就得完全依賴 L2 的 git push／pull。

**Q：在 GDrive 資料夾跑 git 會出錯？**
初始化技能會自動設定 `git config windows.appendAtomically false`，這是 GDrive＋git 的已知坑。

**Q：兩台電腦可以同時開工同一個專案嗎？**
不建議——GDrive 會產生衝突副本。開工技能會顯示上次收工的電腦與時間，幫你避開這個情況。

**Q：我只有其中一台電腦裝 Obsidian，怎麼辦？**
沒關係，這正是自動偵測的用途：沒 Obsidian 的電腦收工時會在 handoff.md 註明「L3 未更新」，回到有 Obsidian 的電腦再補。

**Q：L4 會不會每次建立一堆重複 Notion 頁？**
不會。寫入前會先判斷唯一正式主題、讀取該主題的主 Prompt，再依 Asia/Taipei 週次搜尋既有頁；同事件、同期間、同主題只更新原 Page ID。只有明確 `READ_ONLY` 時完全不寫入。

**Q：Google Drive、Obsidian 與 Notion 分別放什麼？**
Google Drive 保存原始檔、附件、程式、資料集與大型輸出；Obsidian 保存專案詳細脈絡；Notion 只保存正式結論、索引、Prompt、決定、風險與狀態。Secret、Token、帳密、公司機密與未公開內部路徑不得寫入 Notion。

---

📺 完整教學：三師爸「AI Agent 基本功」EP06——如何跨電腦進行你的專案
