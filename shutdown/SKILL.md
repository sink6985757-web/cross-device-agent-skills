---
name: shutdown
description: 專案收工、版本紀錄與交接。當使用者說收工、shutdown、結束、同步、下班或換電腦時使用；每次更新 CHANGELOG.md 與 handoff.md，穩定規則改變才更新 AGENTS.md，GitHub delivery 前更新 README.md，並由確認工作單或 ReadyGate 放行外部動作。
---

# Shutdown

本檔同時包含操作規則、相依關係與固定輸出。「收工」只授權可回復的專案內交接與版本紀錄，不自動授權 commit、push、release、搬移、封存或權限變更。

## 權威與相依

| 角色 | 來源 | 定義 |
|---|---|---|
| 公開來源 | `https://github.com/sink6985757-web/cross-device-agent-skills` | 三技能發行權威 |
| 執行來源 | `~/.agents/skills/shutdown/SKILL.md` | Agent 實際讀取副本 |
| 前一流程 | `../startup/SKILL.md` | 日常唯讀開工 |
| 外部放行 | `~/.agents/skills/readygate/SKILL.md` | commit、push、公開交付、搬移、封存、權限與批次治理 |
| Full Core | `https://github.com/sink6985757-web/cross-device-agent-workflow-core` | 四技能 profile 與完整治理 |

## 寫入契約

| 檔案 | 何時更新 |
|---|---|
| `CHANGELOG.md` | 每次收工都更新近期修改、驗證、delivery 狀態 |
| `handoff.md` | 每次收工都重寫為目前狀態與唯一續跑點 |
| `AGENTS.md` | 只有穩定規則、權威、結構或路線圖改變時 |
| `README.md` | 準備 GitHub delivery 時，更新人類／Agent 安裝文案、目前公開版本與最近公開修改 |

外部筆記與知識庫不屬於 Shutdown 寫入面。

## 流程

1. 讀取 `AGENTS.md`、`README.md`、`CHANGELOG.md`、`handoff.md`、本次對話與 `git status --short --branch`；辨識本次 Agent 與 runtime 電腦名稱。缺檔、未知變更或敏感資訊風險一律標示 `PARTIAL`／`BLOCKED`，不得補造結果。
2. 盤點本次實際完成、驗證、未完成、風險與下一步。先更新 `CHANGELOG.md` 的最新版本節，再更新精簡 `handoff.md`。
3. 只有穩定契約改變時更新 `AGENTS.md`。如果沒有 GitHub delivery 授權，`CHANGELOG.md` 與 `handoff.md` 記錄 `LOCAL_ONLY`，README 不因例行收工而製造假發布。
4. 如果確認工作單包含 GitHub delivery：
   - 先更新 README 的安裝文案、目前發布版本與最近公開修改。
   - 檢查 diff、未知檔、secret、credential、測試與 rollback。
   - 依工作單／ReadyGate Delivery Gate 決定是否 stage、commit、push、tag 或 release。
   - 回讀遠端 SHA／PR／release 後，才把 delivery 寫成 `VERIFIED`。
5. 批次 repository、公開發布、搬移、封存、權限變更或非既有 remote 一律使用 Full Core／ReadyGate；`BLOCKED` 不得 override。
6. GitHub delivery 後若回填 handoff／changelog 產生第二個 commit，仍須在相同授權範圍內驗證並推送；不得假報同步成功。
7. 依固定回報輸出每層狀態與唯一續跑點。

## `CHANGELOG.md` 最新節格式

```markdown
## [<版本｜Unreleased>] - <YYYY-MM-DD>

### Changed
- <本次實際修改>

### Validation
- <測試、回讀或限制>

### Delivery
- GitHub：<LOCAL_ONLY｜PENDING_GATE｜VERIFIED commit SHA／PR／release｜NOT_CONFIGURED>
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
- GitHub：<VERIFIED｜LOCAL_ONLY｜PENDING_GATE｜BLOCKED｜NOT_CONFIGURED>
```

## 固定回報

```markdown
# 收工報告

- 整體：<VERIFIED｜PARTIAL｜BLOCKED>
- Agent／電腦：<Agent> @ <電腦>
- 本地：<完成內容>
- CHANGELOG：<版本節與狀態>
- README：<未變更｜已更新公開文案>
- GitHub：<repository、commit／PR／release 或 LOCAL_ONLY>
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
- 不把「收工」解讀為未確認的 GitHub delivery 或封存授權。
