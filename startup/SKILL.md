---
name: startup
description: 開工接續助手（四層級自動偵測）。當使用者說「開工」、「開始工作」、「我來了」、「上次做到哪」、「我們繼續」、「接下來呢」、「接續工作」、「來吧」等任何要接續上次工作的請求時，請一定要使用此技能。本技能讀取 agents.md 與 handoff.md、檢查 git 狀態、辨識跨電腦交接，並依 Notion Knowledge Master 的共用公約與正式主題 Prompt 續接工作。
---

# 開工接續助手（四層級）

新對話開始時，幫使用者快速進入「上次做到哪」的脈絡，避免從零開始解釋。

## 核心原則

1. **L1～L3 開工只讀**——不改本地檔案、不主動 pull；L4 是否寫入由 Knowledge Master ACTION 決定
2. **不主動 `git pull`**（避免覆蓋本地未 commit 變動，只提醒「要不要 pull」）
3. **30 分鐘內 fetch 過就跳過**（避免單台多對話冗餘）
4. **Obsidian 有需要才讀**——L3 筆記是詳細背景資料，開工預設不讀、只列出路徑
5. **Notion 先讀規則再續接**——每次 L4 操作先讀 Knowledge Master 共用公約與唯一正式主題的主 Prompt；Prompt 頁只讀
6. **明確 READ_ONLY 優先**——只有使用者明確說不要寫入／只回答／`READ_ONLY` 時，L4 完全不寫；否則完成可重用的續接分析或規劃後依 `AUTO_SAVE` 合併到同週唯一頁
7. 跟收工（shutdown）技能是**對偶關係**：收工保存完整進度、開工讀出並建立本次安全續跑點

## 層級偵測（開工看「這個專案」建到哪層）

- **L1**：專案有 `agents.md`／`handoff.md` → 讀
- **L2**：專案有 `.git` → 做 git 檢查
- **L3**：`agents.md` 同步層級表登記了 Obsidian 路徑，且 Obsidian MCP 可用 → 列出筆記路徑（不主動讀）
- **L4**：`agents.md` 登記 Knowledge Master、正式主題與主 Prompt，且 Notion 工具可讀權威入口 → 依 ACTION 讀取或寫回

> 注意：偵測依據是「專案有什麼」，不是「電腦有什麼」。低層級電腦打開高層級專案時做得到的照做、做不到的註明（優雅降級）。L4 不依賴 L3；即使本機沒有 Obsidian，只要 Notion 可用仍可執行 L4。

## 開工 SOP（依序執行）

### L1：讀藍圖與交接檔（永遠執行）

1. **讀 `agents.md`**：專案目標、路線圖進度、工作約定（摘要，不全文倒出）
2. **讀 `handoff.md`**：上次做到哪、目前狀態、下一步、注意事項
3. **檢查「最後更新」欄**：
   - 若**更新者的電腦名 ≠ 這台電腦**（PowerShell 比對 `$env:COMPUTERNAME`）→ 特別標示「⚠️ 上次在另一台電腦（名稱）收工」，並確認 GDrive 同步已完成（看 handoff.md 檔案時間戳是否與交接檔內時間吻合；若本地檔案明顯過舊，提醒等 GDrive 同步完再開工）
   - 若 handoff.md 的更新時間比 agents.md 舊很多 → 提醒「上次可能沒有正式收工」

**Fallback（舊專案相容）**：若專案沒有 `agents.md`／`handoff.md`：
- 有 Obsidian MCP → 改讀 `<vault>/<資料夾名>/專案工作流程.md` 或 `工作筆記.md` 的「上次做到哪」段
- 讀完提議：「這個專案還沒有 agents.md＋handoff.md，要不要用『初始化專案』補建？」（提議即可，不主動建）

### L2：git 檢查（專案有 `.git` 才做）

4. **本地狀態**：`git status --short`
   - clean → 「本地工作區乾淨」
   - 有未 commit 變動 → 列出，提醒「上次有未完成的修改，要繼續還是放棄？」
5. **遠端狀態**（30 分鐘判斷）：
   ```bash
   [ -n "$(find .git/FETCH_HEAD -mmin -30 2>/dev/null)" ] || git fetch origin 2>/dev/null
   BEHIND=$(git rev-list HEAD..origin/HEAD --count 2>/dev/null || echo 0)
   ```
   - `BEHIND` > 0 → 提醒「遠端有 N 個新 commit，要 `git pull` 嗎？」**不主動 pull**
6. **交叉比對防呆**：若 handoff.md 寫「Git push：✅」但遠端沒有對應的新 commit → 警告「上次收工可能沒推成功，建議先確認再動工」

### L3：Obsidian 筆記（有登記才列，不主動讀）

7. 在報告中列出筆記路徑（例：`<資料夾名>/專案工作流程.md`），註明「需要詳細背景時我再去讀」
8. 只有兩種情況才主動讀：handoff.md 的「下一步」明確指向筆記內容，或使用者要求

### L4：Notion Knowledge Master（有登記且可讀才做）

9. 每次重新讀取 Knowledge Master：`https://app.notion.com/p/6474dc5067fa49a98a339275ab8a8539`；不得只依本地快照推定規則
10. 依 `agents.md` 的 L4 對應與本次主要目的確認唯一正式主題，再讀該主題的 `Prompt｜主題`；Prompt 頁只讀，修改數必須是 0
11. 判斷 ACTION：使用者明確指定 `READ_ONLY`／不要寫入／只回答 → `READ_ONLY`；否則 → `AUTO_SAVE`
12. 以 Asia/Taipei 日期計算 `YYYY-Www`，搜尋同主題同週唯一頁並讀取現況：
    - 已有 `YYYY-Www｜正式主題` → 沿用原 Page ID
    - 沒有且本次產生可重用的續接分析或規劃 → 在正式主題下建立
13. `AUTO_SAVE` 時，把本次確認的範圍、現況、證據、安全續跑點與下一步更新到同週頁；保留既有內容，只做最小範圍更新。來源不足或工具受阻標示 `PARTIAL`／`BLOCKED`，不得假裝成功
14. `READ_ONLY` 時只回覆，不改 Notion、不建立 Log；Notion 工具不可用時標示 L4 `BLOCKED`，L1～L3 仍照常完成

### 報告 + 建議下一步

給使用者**結構化摘要**（不要冗長）：

```
📂 專案：<資料夾名>（第 N 層級）
📘 上次做到哪：<handoff 摘要 1-2 句>（<時間>，<更新者> @ <電腦名>）
🔧 本地 git：<clean｜有 N 個未 commit 變動｜—（L1 專案）>
🌐 遠端：<最新｜落後 N commits，建議 git pull｜—>
🧠 Obsidian：<筆記路徑，需要時再讀｜—>
🧭 Notion：<正式主題｜ACTION｜寫入位置｜頁面標題｜新增或更新／未寫入｜VERIFIED／PARTIAL／BLOCKED>
➡️ 建議下一步：
   1. <handoff「下一步」第 1 項>
   2. <可選：第 2 項>

要從哪個方向開始？
```

最後**等使用者選方向**，不要自己擅自繼續。

## 不該做的事

- ❌ 主動 `git pull`（會撞本地未 commit 變動）
- ❌ 修改 `agents.md`／`handoff.md`／Obsidian 筆記（那是收工的事；Notion 依 Knowledge Master ACTION 另行判定）
- ❌ 沒有交接檔時硬建一個（先問使用者）
- ❌ 開工就把 Obsidian 筆記全文讀進來（違反「有需要才讀」的分層設計）
- ❌ 把藍圖與交接檔內容**全文倒出來**（要摘要、保持精簡）
- ❌ 未讀 Knowledge Master 共用公約與主 Prompt 就寫 Notion，或修改 `Prompt｜…`
- ❌ 為同主題同週另建 v2／最新版／修正版；必須更新唯一既有 Page ID
- ❌ 在 Notion 保存 Secret、Token、帳密、公司機密、裝置內部路徑或未公開技術內容

## 與收工（shutdown）的對偶關係

| 面向 | 收工 | 開工 |
|------|------|------|
| 主要動作 | 摘要今天做什麼 | 摘要上次做什麼 |
| agents.md / handoff.md | **寫入** | **讀出** |
| Git 動作 | add + commit + push | status + fetch（不 pull） |
| Obsidian | 寫詳細紀錄 | 只列路徑、需要才讀 |
| Notion | 依 Knowledge Master ACTION 合併正式成果 | 先讀規則；`AUTO_SAVE` 合併續接分析，`READ_ONLY` 零寫入 |
| 對外副作用 | 推 GitHub、改檔案、更新 Notion | L1～L3 無；L4 僅依 Knowledge Master ACTION |

## 注意事項

- 所有訊息使用**繁體中文**
- 本 skill 在 `~/.claude-skills/`，搭配 chezmoi 跨電腦同步；修改後記得 `chezmoi re-add ~/.claude-skills/startup/SKILL.md`
- 若與全域 CLAUDE.md 的文字版 SOP 重疊：**以本 skill 為準**（skill 是顯性觸發、文字 SOP 是 fallback）
