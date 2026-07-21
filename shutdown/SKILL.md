---
name: shutdown
description: 收工同步助手（四層級自動偵測）。當使用者說「收工」、「結束了」、「下班」、「準備換電腦」、「同步」、「先到這裡」、「換電腦繼續做」等任何要結束工作並保存進度的請求時，請一定要使用此技能。本技能更新 agents.md 與 handoff.md、git commit + push、補充 Obsidian 詳細紀錄，並依 Notion Knowledge Master 規則合併正式成果。
---

# 收工同步助手（四層級）

對話結束前，把這次的工作保存到專案建到的每一層：

| 層級 | 收工動作 | 給誰看 |
|------|---------|--------|
| L1 本地 | 更新 `agents.md` 進度＋改寫 `handoff.md` | 下一個 session 的任何 Agent、任何電腦 |
| L2 GitHub | commit + push | 版本歷史＋雲端備份 |
| L3 Obsidian | 詳細紀錄寫進 `專案工作流程.md` | 未來需要完整脈絡的自己 |
| L4 Notion | 依 Knowledge Master 共用公約與主 Prompt 合併同週唯一正式紀錄 | 跨專案、跨工具可重用的正式結論與治理狀態 |

## 核心原則

1. **開工是「讀」、收工是「寫」**——handoff.md 是收工的必寫項，這是跨電腦／跨 Agent 交接的生命線
2. **不在 vacuum 中執行**——先從對話脈絡盤點今天做了什麼
3. **只動需要動的**——沒實質進度（只是問問題、沒改檔案）就不跑同步
4. **有疑問先問人**——commit 前先給訊息草稿等點頭；不確定要不要 add 的檔案先問
5. **精簡與詳細分家**——handoff.md 只放交接必需資訊，完整脈絡（決策原因、踩坑細節）寫 Obsidian，兩邊不重複
6. **正式成果受 Knowledge Master 治理**——每次 L4 寫入先讀共用公約與唯一正式主題的主 Prompt；Prompt 頁只讀
7. **AUTO_SAVE 是預設**——除非使用者明確指定 `READ_ONLY`／不要寫入，收工產生的可重用成果必須合併到同週唯一 Notion Page ID

## 層級偵測（收工看「這個專案」建到哪層）

- **L1**：專案有 `agents.md`／`handoff.md` → 更新（沒有就提議先跑「初始化專案」）
- **L2**：專案有 `.git` → commit + push
- **L3**：`agents.md` 登記了 Obsidian 路徑，且這台電腦的 Obsidian MCP 可用 → 寫詳細紀錄
- **L4**：`agents.md` 登記 Knowledge Master、正式主題與主 Prompt，且 Notion 工具可讀權威入口 → 依 ACTION 合併正式成果

> 低層級電腦打開高層級專案：做得到的照做，做不到的在 handoff.md 註明（例：「本次在無 Obsidian 的電腦收工，L3 筆記未更新」），回到高層級電腦時補。L4 不依賴 L3；Notion 可用時仍應獨立完成。

## 收工 SOP（依序執行）

### L1：更新藍圖與交接檔（永遠執行）

1. **盤點本次成果**：從對話歷史摘要——完成了哪些檔案、做了什麼決定、踩了什麼坑
2. **更新 `agents.md`**：
   - 路線圖 checklist：勾掉完成項、新增發現的待辦
   - 「資料夾結構」有新增檔案就補
3. **改寫 `handoff.md`**（整份重寫，不是往下堆）：
   - ⏯️ 目前做到哪：本次最後完成的動作
   - 🚦 目前狀態：可運行？哪些做一半？
   - ➡️ 下一步：具體、可執行的 1-3 項
   - ⚠️ 注意事項：新踩的坑、暫時 workaround
   - 🕐 最後更新：時間＋更新者（Agent 名 @ `$env:COMPUTERNAME`）＋ Git push 狀態（先寫「待推」，L2 完成後回填）
   - Notion：正式主題＋ACTION＋頁面標題＋新增／更新＋狀態（先寫「待同步」，L4 完成後回填）

### L2：git 同步（專案有 `.git` 才做）

4. `git status --short` 看變動 → 擬**繁體中文** commit 訊息（標題：動詞＋對象；正文 3-5 條 bullet 描述變動＋為什麼）→ **給使用者過目，點頭再 commit**
5. commit → `git push`
6. **回填 handoff.md 的 Git push 欄**：成功 → `✅ 已推`；失敗 → `❌ 未推（原因）`，並在回報中標紅提醒（沒推成功，另一台電腦就拿不到 GitHub 備份）
7. 不要 add：`.claude/`、`.env`、API key、untracked 的不明新檔（先問）

### L3：Obsidian 詳細紀錄（可用才做）

8. 更新 `<vault>/<資料夾名>/專案工作流程.md`：
   - 「⏯️ 上次做到哪」段：同步 handoff 摘要
   - 「🗓️ 最近更動紀錄」表格：加一行（日期＋摘要＋同步狀態）
   - 「🕳️ 踩坑筆記」：有新坑就依分類補（含原因與解法，這裡寫詳細版）
   - 決策紀錄：本次做了什麼取捨、為什麼（handoff 不放這些，放這裡）
9. 表格超過 30 行 → 提醒使用者歸檔到 `歷史日誌.md`

### L4：Notion Knowledge Master（有登記且可讀才做）

10. 寫入前重新讀取 Knowledge Master：`https://app.notion.com/p/6474dc5067fa49a98a339275ab8a8539`，再依 `agents.md` 對應與本次主要目的確認唯一正式主題
11. 讀取該主題的 `Prompt｜主題` 作為只讀執行規則；Prompt 修改數必須是 0
12. 判斷 ACTION：使用者明確指定 `READ_ONLY`／不要寫入／只回答 → `READ_ONLY`；否則 → `AUTO_SAVE`
13. `AUTO_SAVE` 時，以 Asia/Taipei 日期決定 `YYYY-Www`，搜尋同主題同週唯一頁：
    - 已存在 → 保留 Page ID 與未要求變更的內容，以最小範圍更新本次成果
    - 不存在 → 在正式主題下建立 `YYYY-Www｜正式主題`
14. 正式紀錄包含：範圍與狀態、證據、已完成／未執行、實際異動、錯誤與影響、回滾、安全續跑點、下一步；區分事實、推論與缺口，標示 `VERIFIED`／`PARTIAL`／`BLOCKED`
15. 寫入後回讀頁面與父頁，確認唯一 Page ID、內容與位置；回填 `handoff.md` 的 Notion 欄。`READ_ONLY` 不改 Notion、不建立 Log；工具失敗要記 `BLOCKED` 與原因

### 回報（層級 checklist）

```
✅ L1 本地：agents.md 進度已更新、handoff.md 已改寫（更新者：<Agent> @ <電腦名>）
✅ L2 GitHub：<repo> 已 commit + push（<commit 標題>）
✅ L3 Obsidian：專案工作流程.md 已補紀錄
✅ L4 Notion：<判斷主題｜ACTION｜寫入位置｜頁面標題｜新增或更新｜VERIFIED／PARTIAL／BLOCKED>
⚠️ 手動處理：<例：本次新增了 ~/.xxx_api_key，另一台電腦要手動建>
```

沒做到的項目用 ⚠️ 或 ❌ 並說明原因。若本次改過 `~/.claude/`／`~/.claude-skills/` 的全域設定或技能，提醒跑 chezmoi 同步（`chezmoi re-add` ＋ push）。

## 不該做的事

- ❌ 對「沒實質進度」的對話也跑同步
- ❌ 沒更新 handoff.md 就收工（那是下次開工的唯一線索）
- ❌ commit message 寫「更新」、「修改」這種沒資訊的字
- ❌ 自動 add untracked 的新檔或敏感檔（要使用者確認）
- ❌ 把該寫進 Obsidian 的長篇細節塞進 handoff.md（交接檔要保持一頁內讀完）
- ❌ 未讀 Knowledge Master 共用公約與主 Prompt 就寫 Notion，或修改 `Prompt｜…`
- ❌ 建立 v2／最新版／修正版或同主題同週重複頁；應更新唯一既有 Page ID
- ❌ 只在聊天視窗回報正式成果而省略 `AUTO_SAVE`，或在 `READ_ONLY` 下建立 Log
- ❌ 在 Notion 保存 Secret、Token、帳密、公司機密、裝置內部路徑或未公開技術內容

## 與開工（startup）的對偶關係

| 面向 | 收工 | 開工 |
|------|------|------|
| agents.md / handoff.md | **寫入** | **讀出** |
| Git 動作 | add + commit + push | status + fetch（不 pull） |
| Obsidian | 寫詳細紀錄 | 只列路徑、需要才讀 |
| Notion | 依 Knowledge Master ACTION 合併正式成果 | 先讀規則；`AUTO_SAVE` 合併續接分析，`READ_ONLY` 零寫入 |
| 對外副作用 | 推 GitHub、改檔案、更新 Notion | L1～L3 無；L4 僅依 Knowledge Master ACTION |

## 注意事項

- 所有訊息使用**繁體中文**
- GDrive 內的 repo 首次操作若遇 git 寫入錯誤：`git config windows.appendAtomically false`
- 本 skill 在 `~/.claude-skills/`，搭配 chezmoi 跨電腦同步；修改後記得 `chezmoi re-add ~/.claude-skills/shutdown/SKILL.md`
