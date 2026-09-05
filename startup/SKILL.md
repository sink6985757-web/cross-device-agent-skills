---
name: startup
description: 每次專案開工或接續時使用的唯讀入口。當使用者說開工、startup、開始工作、繼續、下一步或上次做到哪時，讀取專案 manifest、AGENTS.md、handoff.md 與 Git 狀態，必要時 fetch 並把本機狀態對照最後一個 GitHub checkpoint SHA，依固定格式回報後停止等待；不建立空 commit、不 pull／merge／rebase、不執行工作，也不修改專案內容。
---


當本次對話或已確認工作單已明列更新、commit／push 與驗收範圍，沿用該授權完成，不為相同動作重複提問；未涵蓋的動作仍停在確認點。Startup 維持唯讀，完成讀取報告後可轉入已授權的獨立工作階段。
# Startup

本檔同時包含操作規則、相依關係與固定輸出。Startup 對專案內容永遠唯讀；`git fetch` 只允許更新遠端追蹤 refs，不能被解讀為工作樹已同步。

## 精確定義與輸出邊界

- **進入 Startup**：每次開始或接續一個已初始化專案，不論是否換 Agent 或電腦。
- **不要進入 Startup**：新專案缺少必要四檔時只做唯讀判定，標示 `PARTIAL` 並路由到 `initial`，不得自行補檔。
- **允許動作**：讀取必要入口、驗證 Git top-level／remote identity、摘要目前狀態，必要時做 `git fetch`；不得建立空 commit 或把 fetch 解讀為同步完成。
- **完成標準**：使用者能從一份開工報告知道目前目標、上次做到哪、Git 狀態、風險與最多三個下一步。
- **硬停止點**：開工報告輸出後立即停止並等待使用者選擇或確認工作；即使同一句同時提出實作要求，Startup 本身仍不寫入。
- **下一流程**：範圍明確的小型工作可在後續執行；重大返工、高風險、不可逆或外部交付工作先進 ReadyGate。

## 權威與相依

| 角色 | 來源 | 定義 |
|---|---|---|
| 公開來源 | `https://github.com/sink6985757-web/cross-device-agent-skills` | 三技能發行權威 |
| 執行來源 | `~/.agents/skills/startup/SKILL.md` | Agent 實際讀取副本 |
| 前一流程 | `../initial/SKILL.md` | 缺少必要檔案時建議使用 |
| 後一流程 | `../shutdown/SKILL.md` | 工作結束時更新版本與交接 |
| 高風險路由 | `~/.agents/skills/readygate/SKILL.md` | 只有任務風險需要時提示，不在 Startup 內啟動寫入 |
| 可攜式契約 | `.agents/project-lifecycle.json` | 由 Full Core schema 定義的 Part→Project 路由、GitHub identity 與 checkpoint policy |

## 讀取契約

必讀：

1. `.agents/project-lifecycle.json`：Part 路由、實際專案 identity、remote、相對路徑與 checkpoint policy。
2. `AGENTS.md`：穩定規則與權威。
3. `handoff.md`：上次狀態與下一步。
4. `git status --short --branch`：本機工作樹。

選讀：

- `CHANGELOG.md` 最近一節：只有 handoff 要求確認近期版本，或使用者詢問版本時。
- `README.md`：只有任務涉及安裝、使用方法或公開文案時。

外部筆記與知識庫不屬於 Startup 讀取面。

## 流程

1. 以 `git rev-parse --show-toplevel` 找到實際專案 Git 根；Part 名稱或上層資料夾不得替代此邊界。辨識本次 Agent 與 runtime 電腦名稱；失敗寫 `UNKNOWN`，且不得把裝置資訊寫進 canonical manifest。
2. 讀取並驗證必讀檔；manifest、`AGENTS.md` 或 `handoff.md` 任一缺少就標示 `PARTIAL`，建議執行 `initial`，不得自行建立。
3. 驗證 manifest 的 `project.github_repository` 與指定 remote identity；remote 不存在標 `PARTIAL`，指向其他 repository 標 `BLOCKED`。
4. 有正確 remote 時可 `git fetch --prune`；不得 pull、merge、rebase、checkout、stage、commit、push 或修改檔案。未 fetch 或 fetch 失敗就把遠端狀態標 `UNKNOWN`。
5. 比較 `HEAD...@{upstream}`、目前 branch、工作樹與最後遠端 SHA，依下列路由回報；Startup 不用空 commit 製造紀錄：
   - `CLEAN_SYNCED`：本機與 GitHub checkpoint 一致，可進下一項工作。
   - `DIRTY`：先辨識／保存既有修改；不得被遠端內容覆蓋。
   - `AHEAD`：有尚未 push 的本機 commit；先完成 checkpoint 或明確保留。
   - `BEHIND`：只有工作樹乾淨且無本機領先時，後續才可經授權使用 `pull --ff-only`；Startup 本身不執行。
   - `DIVERGED`：停止，保存 local／remote refs，交由確認工作單決定整合；不得 auto merge／rebase。
   - `WRONG_REMOTE`／`DETACHED_HEAD`／`NO_UPSTREAM`：停止，修正 identity／branch policy 前不工作。
6. 摘要目標、上次狀態、checkpoint SHA、風險與最多三個下一步，然後等待使用者選擇。後續任務涉及重大返工、發布、搬移、封存、權限或其他高風險操作時再路由 Full Core／ReadyGate。

## 固定回報

```markdown
# 開工報告

- 專案：<名稱>
- 狀態：<VERIFIED｜PARTIAL｜BLOCKED>
- 本次 Agent／電腦：<Agent> @ <電腦>
- 目標：<AGENTS.md 摘要>

## 上次做到哪
- 上次 Agent／電腦：<handoff 記錄｜UNKNOWN>
<最多三句摘要>

## Git
- Git 根：<已驗證 top-level｜WRONG_GIT_ROOT｜NOT_CONFIGURED>
- 工作樹：<乾淨｜有 N 項變更｜NOT_CONFIGURED>
- 遠端：<identity 與 fetch 狀態>
- Checkpoint：<CLEAN_SYNCED｜DIRTY｜AHEAD N｜BEHIND N｜DIVERGED｜WRONG_REMOTE｜UNKNOWN> @ <remote SHA｜UNKNOWN>

## 版本
- 最近紀錄：<CHANGELOG 最近一節｜本次不需讀取｜NOT_CONFIGURED>

## 建議下一步
1. <最優先>
2. <可選>
3. <可選>

## 注意事項
- <風險、ReadyGate 提示或無>
```

## 不做

- 不修改 `AGENTS.md`、`README.md`、`CHANGELOG.md`、`handoff.md` 或工作樹；除允許的 fetch remote refs 外，不改 Git state。
- 不建立空 commit 只為表示「今天有開工」。Startup 的對照紀錄是開工報告中的遠端 checkpoint SHA。
- 不讀寫 Notion、Obsidian 或其他外部知識庫。
- 不根據電腦名稱判斷同步成功。
- 不宣稱未 fetch／未回讀的遠端狀態已驗證。
