---
name: shutdown
description: 每次專案工作結束時執行版本紀錄、交接與 GitHub checkpoint。當使用者說收工、shutdown、結束、同步、下班或換電腦時使用；每次更新 CHANGELOG.md 與 handoff.md，穩定規則改變才更新 AGENTS.md，公開文案改變才更新 README.md。依 `.agents/project-lifecycle.json` 的 manual 或 standing_scoped policy 停在確認點，或對既有正確 remote 執行 allowlist 內 scoped commit、非 force push 與遠端回讀；不建立 repository、不 merge／rebase、不 tag／release。
---


當本次對話或已確認工作單已明列更新、commit／push 與驗收範圍，沿用該授權完成，不為相同動作重複提問；未涵蓋的動作仍停在確認點。Startup 維持唯讀，完成讀取報告後可轉入已授權的獨立工作階段。
# Shutdown

本檔同時包含操作規則、相依關係與固定輸出。`manual` 是預設，單獨說「收工」只授權可回復的專案內交接；只有專案已經以受治理 manifest 設定 `standing_scoped`，例行收工才包含事先授權的窄範圍 checkpoint。任何模式都不授權 release、搬移、封存或權限變更。

## 精確定義與交付邊界

- **進入 Shutdown**：每次工作階段結束、換電腦，或需要把目前狀態整理成下一位 Agent 可直接接續的交接。
- **固定寫入**：每次更新 `CHANGELOG.md` 與 `handoff.md`；即使工作未完成，也要忠實記錄 `PARTIAL`／`BLOCKED` 與唯一續跑點。
- **條件寫入**：穩定規則、權威或架構改變才更新 `AGENTS.md`；只有正在準備已授權的 GitHub delivery 才更新 `README.md` 公開文案。
- **完成標準**：本次修改、驗證、未完成、風險、checkpoint／delivery 狀態與下一步都能被回讀，且未知檔案沒有被 stage 或覆寫；已 push 時必須有遠端 SHA readback。
- **硬停止點**：`manual` 完成本機交接後以 `LOCAL_ONLY`／`PENDING_CHECKPOINT` 停止；`standing_scoped` 遇到任何限制不符即以 `PARTIAL`／`BLOCKED` 停止，不得擴大 allowlist 或換 remote 繞過。
- **ReadyGate 接點**：修改 standing policy，或要求 release、搬移、封存、權限、批次治理及 denylist 動作時，只有已確認工作單與 Delivery Gate 涵蓋的動作可以繼續。

## 權威與相依

| 角色 | 來源 | 定義 |
|---|---|---|
| 公開來源 | `https://github.com/sink6985757-web/cross-device-agent-skills` | 三技能發行權威 |
| 執行來源 | `~/.agents/skills/shutdown/SKILL.md` | Agent 實際讀取副本 |
| 前一流程 | `../startup/SKILL.md` | 日常唯讀開工 |
| 外部放行 | `~/.agents/skills/readygate/SKILL.md` | commit、push、公開交付、搬移、封存、權限與批次治理 |
| Full Core | `https://github.com/sink6985757-web/cross-device-agent-workflow-core` | 四技能 profile 與完整治理 |
| 專案 policy | `.agents/project-lifecycle.json` | Part→Project 路由、實際 GitHub identity、checkpoint 模式、allowlist 與 rollback |

## 寫入契約

| 檔案 | 何時更新 |
|---|---|
| `CHANGELOG.md` | 每次收工都更新近期修改、驗證、delivery 狀態 |
| `handoff.md` | 每次收工都重寫為目前狀態與唯一續跑點 |
| `AGENTS.md` | 只有穩定規則、權威、結構或路線圖改變時 |
| `README.md` | 準備 GitHub delivery 時，更新人類／Agent 安裝文案、目前公開版本與最近公開修改 |

外部筆記與知識庫不屬於 Shutdown 寫入面。

## 流程

1. 讀取 `.agents/project-lifecycle.json`、`AGENTS.md`、`README.md`、`CHANGELOG.md`、`handoff.md`、本次對話與 Git 狀態；以 `git rev-parse --show-toplevel` 驗證實際專案邊界。Part 只做路由。缺檔、錯 remote、未知變更或敏感資訊風險一律標示 `PARTIAL`／`BLOCKED`。
2. 盤點本次實際完成、驗證、未完成、風險與下一步。先更新 `CHANGELOG.md` 的最新版本節，再更新精簡 `handoff.md`。
3. 只有穩定契約改變時更新 `AGENTS.md`；只有安裝、使用、公開版本或最近公開修改真的改變時更新 README。例行 checkpoint 不是 release，不得製造假發布文案。
4. 驗證 manifest、remote identity、目前工作 branch、upstream、diff、測試、secret、未知 untracked、allowlist、large-file policy 與 rollback：
   - `WRONG_REMOTE`、`DIVERGED`、`DETACHED_HEAD`、`NO_UPSTREAM`、unknown untracked、allowlist 外變更、secret 或測試失敗：停止。
   - `BEHIND`：即使乾淨也不在 Shutdown auto pull；先回到明確的 ff-only 同步流程。
   - GitHub repository 不存在：標 `PARTIAL`，建立 repository 另走 ReadyGate。
5. 依 checkpoint mode 執行：
   - `manual`：顯示只含 allowlist 的 staging plan、目前 branch、commit 目的與 rollback，停在 `PENDING_CHECKPOINT` 等待本次授權。
   - `standing_scoped`：只 stage allowlist 內且已辨識的本次變更；建立 scoped commit，非 force push 目前工作 branch，再用 remote ref／GitHub readback 驗證 SHA。不得自動 merge 到 default branch。
   - push 失敗：本機 commit 保留為 `PARTIAL`；不得 amend／reset／換 remote 反覆覆蓋歷史。
6. 發布、tag／release、PR merge、建立 repository、force push、auto merge／rebase、刪除／封存、權限與批次遷移一律不在 standing scope；只有獨立工作單／ReadyGate 可處理。
7. 已 push checkpoint 後若回填 handoff／changelog 產生第二個差異，必須在同一 allowlist 內再次 checkpoint 並回讀；否則不得宣稱完全同步。
8. 依固定回報輸出每層狀態與唯一續跑點。

## 回滾與同步規則

- 已發布的錯誤使用新的 `git revert` commit，不用 reset／force push 消除遠端歷史。
- 要查看舊 SHA 時建立 restore branch；不得把舊 checkout 直接覆蓋目前分支。
- 只有 `BEHIND`、工作樹乾淨且沒有本機領先時，才可在獨立同步步驟使用 `pull --ff-only`。
- `DIVERGED` 時保存 local 與 remote refs，停止並由工作單決定整合。
- clone 只進空目錄；不 clone 到現有專案上方或內部以免形成巢狀／覆蓋衝突。

## `CHANGELOG.md` 最新節格式

```markdown
## [<版本｜Unreleased>] - <YYYY-MM-DD>

### Changed
- <本次實際修改>

### Validation
- <測試、回讀或限制>

### Delivery
- GitHub：<LOCAL_ONLY｜PENDING_CHECKPOINT｜VERIFIED checkpoint SHA｜BLOCKED｜NOT_CONFIGURED>
```

## `handoff.md` 格式

```markdown
# Handoff

## 目前做到哪
<最後成果，最多三句>

## 目前狀態
- 可執行：<是／否／PARTIAL>
- 已驗證：<內容>
- 未完成：<內容｜無>

## 下一步
1. <最小可執行步驟>
2. <可選>
3. <可選>

## 注意事項
- <風險、workaround 或無>

## 最近更新
- 時間：<YYYY-MM-DD HH:mm timezone>
- 更新者：<Agent>
- 電腦：<runtime 名稱｜UNKNOWN>
- 成果 commit：<SHA｜未提交｜NOT_CONFIGURED>
- GitHub：<VERIFIED checkpoint SHA｜LOCAL_ONLY｜PENDING_CHECKPOINT｜BLOCKED｜NOT_CONFIGURED>
```

## 固定回報

```markdown
# 收工報告

- 整體：<VERIFIED｜PARTIAL｜BLOCKED>
- Agent／電腦：<Agent> @ <電腦>
- 本地：<完成內容>
- CHANGELOG：<版本節與狀態>
- README：<未變更｜已更新公開文案>
- Checkpoint policy：<manual｜standing_scoped｜NOT_CONFIGURED>
- GitHub：<repository、branch、remote checkpoint SHA 或 LOCAL_ONLY／PENDING_CHECKPOINT>
- AGENTS：<未變更｜已更新>
- handoff：<已更新並回讀>

## 回滾
- <commit、備份或還原方法>

## 唯一續跑點
1. <下一次開工直接執行的第一步>
```

## 不做

- 不提交未知檔案、secret、credential 或私人資料。
- 不把長篇歷史塞進 `handoff.md`；歷史放 `CHANGELOG.md`／Git。
- 不讀寫 Notion、Obsidian 或其他外部知識庫。
- 不把 `manual` 模式的「收工」解讀為 GitHub push；`standing_scoped` 也只涵蓋既有 identity-matching remote、目前工作 branch 與 manifest allowlist。
