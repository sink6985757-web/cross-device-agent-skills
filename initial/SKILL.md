---
name: initial
description: 第一次初始化單一專案、修復既有專案缺件或部署本機生命週期技能。當使用者說初始化專案、initial、init、開新專案或部署生命週期技能時使用；建立缺少的四檔與可攜式生命週期 manifest，驗證實際 Git 根與既有 GitHub remote，並依 manual 或 standing_scoped checkpoint policy 停在確認點或建立可回讀的初始化保底。完成後停止，不把 Initial 當成日常開工，也不建立 GitHub repository 或整合外部知識庫。
---


當本次對話或已確認工作單已明列更新、commit／push 與驗收範圍，沿用該授權完成，不為相同動作重複提問；未涵蓋的動作仍停在確認點。Startup 維持唯讀，完成讀取報告後可轉入已授權的獨立工作階段。
# Initial

只處理第一次部署、既有專案缺件修復，或使用者明確要求的生命週期技能部署。本檔同時包含操作規則、依賴關係與固定輸出；跨專案共同欄位由 Full Core manifest schema 定義，專案本身仍以自己的 Git repository 為版本權威。

## 精確定義與進出條件

- **進入 Initial**：新專案尚未建立生命週期四檔、既有專案缺少其中一檔，或使用者明確要求安裝／修復共用技能。
- **不要進入 Initial**：四檔已存在且只是要開始今天的工作；此時直接使用 `startup`。
- **允許寫入**：只建立缺少的四檔與 `.agents/project-lifecycle.json`；既有檔案、manifest 或 runtime Skill 內容不同時，先顯示差異並取得明確更新授權。
- **完成標準**：缺件已建立或差異已明確交棒，全部建立內容已回讀，實際 Git top-level、remote identity、安全、可攜性與 checkpoint 結果都有證據。
- **硬停止點**：`manual` 模式在本機初始化後停在 checkpoint 確認點；既有 manifest 明確設為 `standing_scoped` 時，只有全部限制通過才可建立 scoped commit、非 force push 並回讀遠端 SHA。兩種模式都不得自動接著執行日常工作。
- **下一流程**：日常接續使用 `startup`；工作結束使用 `shutdown`；高風險或外部動作按需使用 ReadyGate。

## 權威與相依

| 角色 | 權威／路徑 | 定義 |
|---|---|---|
| 公開安裝來源 | `https://github.com/sink6985757-web/cross-device-agent-skills` | `initial`／`startup`／`shutdown` 的發行權威 |
| 執行來源 | `~/.agents/skills/initial/SKILL.md` | Agent 實際讀取的安裝副本 |
| Full Core | `https://github.com/sink6985757-web/cross-device-agent-workflow-core` | 首次部署、完整治理與四技能相容檢查 |
| ReadyGate | `~/.agents/skills/readygate/SKILL.md` | 批次、高風險、發布、搬移、封存與權限變更閘門 |
| 可攜式契約 | Full Core `.schemas/project-lifecycle.schema.json` | 定義 Part 路由、專案 Git 邊界、checkpoint policy 與 rollback；各專案部署為 `.agents/project-lifecycle.json` |
| 下一流程 | `../startup/SKILL.md` | 初始化完成後的日常開工 |

## Part、Project 與裝置邊界

- `Part` 只是權威系統的分類／路由值，不是固定的 Part 9，也不自動等於資料夾、repository 或 branch。
- `Project` 才是實際執行單位；每次以 `git rev-parse --show-toplevel` 驗證唯一 Git 根。若一個 Part 內有多個 repository，每個 repository 都有自己的 manifest 與版本歷史。
- canonical manifest 只保存 `/` 分隔的專案相對路徑。裝置名稱、絕對路徑、登入狀態與 credential 只留在 runtime 或已忽略的 `policy.local.yaml`。
- manifest 的 authority revision 使用不可變 tag 或 commit；不得以會漂移的本機 checkout 路徑當權威。

## 專案四檔契約

| 檔案 | 責任 | Initial 動作 |
|---|---|---|
| `AGENTS.md` | 穩定規則、權威、邊界 | 缺少才建立 |
| `README.md` | GitHub 人類安裝、Agent／Tool 安裝、使用與公開版本文案 | 缺少才建立；資料不足留待確認 |
| `CHANGELOG.md` | 每次收工的近期修改、驗證與 delivery 狀態 | 缺少才建立 |
| `handoff.md` | 當下狀態、下一步、風險與唯一續跑點 | 缺少才建立 |

外部筆記、Notion、Obsidian 或其他知識庫不屬於本契約；只有獨立、明確提出的任務才可處理。

## 流程

1. 執行 `git rev-parse --show-toplevel` 確認實際專案 Git 根；讀取既有 `.agents/project-lifecycle.json`、`README.md`、`AGENTS.md`、`CHANGELOG.md`、`handoff.md` 與 `git status --short --branch`。Part 路由不得取代 Git top-level；任何既有檔案都不得直接覆寫。
2. 在 runtime 偵測 OS、Git、`gh auth status`、`~/.agents/skills`、本次 Agent 與本機電腦名稱。Windows 使用 `[Environment]::MachineName`，Linux／macOS 使用 `hostname`；失敗寫 `UNKNOWN` 並標示 `PARTIAL`。不得讀取 token、`.env`、credential cache 或裝置私密資料。
3. 檢查 `initial`、`startup`、`shutdown` 是否各只有 `SKILL.md` 且版本相容。Full Core profile 另檢查 `readygate`；公開 Lite profile 不強制安裝 ReadyGate。
4. 已存在但內容不同的共用 Skill 不得直接覆蓋；先顯示來源、版本與差異，取得明確更新授權。Agent 不原生支援 `~/.agents/skills` 時，只建立薄轉接，不複製另一份設計權威。
5. 依下列內嵌骨架建立缺少的專案四檔；依 Full Core template 產生缺少的 `.agents/project-lifecycle.json`，先保留 `checkpoint.mode=manual`。沒有證據的 repository、revision、路徑、版本與時程不得猜測。
6. 驗證 manifest schema、Git top-level、`project.github_repository` 與既有 remote identity。沒有 remote、remote 指錯、detached HEAD、無 upstream、diverged、未知 untracked、secret、驗證失敗或 allowlist 外變更時停止並標 `PARTIAL`／`BLOCKED`。
7. Git 尚未初始化時，只有在本次確認工作單授權後才建立 `main` 與最小 `.gitignore`。建立 GitHub repository、變更 remote／權限或公開範圍永遠不在 standing scope 內。
8. 執行 checkpoint：
   - `manual`：列出精確 allowlist、預計 branch 與 rollback，停下等待本次 commit／push 授權。
   - `standing_scoped`：只對 manifest allowlist 內已確認檔案建立 scoped commit，push 目前工作 branch，禁止 force；以遠端 SHA 回讀成功才標 `VERIFIED`。
   - push 或回讀失敗：保留本機 commit 與 refs，標 `PARTIAL`，不得重寫歷史或改推別的 remote。
9. 回讀全部建立內容；檢查 UTF-8、`git diff --check`、敏感資訊與未知檔案，最後回報 `VERIFIED`／`PARTIAL`／`BLOCKED` 並停止。

## Checkpoint policy

| 模式 | Initial 行為 |
|---|---|
| `manual` | 預設值；本機完成後停在 checkpoint 確認點，不把「初始化」推定為外部授權 |
| `standing_scoped` | 只有該專案已提交 manifest 事先明定 remote、目前工作 branch、allowlist 與禁止動作，且所有安全條件通過，才可自動 commit／push／remote readback |

變更 `checkpoint.mode`、GitHub repository、remote、branch policy、allowlist 或 authority revision 本身不是日常 checkpoint；必須先由確認工作單／ReadyGate 放行。

## 內嵌骨架

### `AGENTS.md`

```markdown
# <專案名稱>

## 目標
<一句話；未知就寫待確認>

## 專案結構
- `README.md`：人類與 Agent／Tool 安裝、使用及公開版本文案。
- `CHANGELOG.md`：每次收工的近期修改與 delivery 狀態。
- `handoff.md`：目前狀態、下一步與唯一續跑點。

## 共用規則
1. 每次開工先讀本檔、`handoff.md` 與 Git 狀態。
2. 保留既有修改；不提交 secret、credential 或未知檔案。
3. canonical 路徑使用專案相對路徑。
4. 每次收工更新 `CHANGELOG.md` 與 `handoff.md`。
5. GitHub delivery 前更新 `README.md`，並依工作單／ReadyGate 放行。

## 生命週期路由

- `initial`：只負責第一次治理結構、缺件修復或技能部署；完成後停止。
- `startup`：每次開工唯讀回報，完成後等待工作選擇。
- `shutdown`：每次收工更新版本紀錄與交接；是否 checkpoint 由專案 manifest 的 `manual`／`standing_scoped` 決定。
- `ReadyGate`：只在高風險、不可逆或外部交付工作按需插入。

## 整合
- GitHub：<repository｜NOT_CONFIGURED>
- 生命週期 manifest：`.agents/project-lifecycle.json`
- 外部知識庫：`ON_DEMAND_ONLY`，不屬於專案生命週期。
```

### `README.md`

```markdown
# <專案名稱>

<用途摘要；未知就寫待確認>

## 人類安裝
<可驗證的安裝步驟；未知就寫待確認>

## Agent／Tool 安裝
<可驗證的自動化安裝或使用入口；未知就寫待確認>

## 使用
<最小可執行方式>

## 版本
- 目前發布：<版本｜尚未發布>
- 最近公開修改：<摘要｜尚未發布>

## 協作檔案
- `AGENTS.md`：穩定規則。
- `CHANGELOG.md`：近期版本紀錄。
- `handoff.md`：目前交接狀態。
```

### `CHANGELOG.md`

```markdown
# Changelog

## [Unreleased] - <YYYY-MM-DD>

### Changed
- 專案初始化。

### Validation
- <已執行驗證｜尚待驗證>

### Delivery
- GitHub：`LOCAL_ONLY`
```

### `handoff.md`

```markdown
# Handoff

## 目前做到哪
專案初始化完成。

## 目前狀態
- 可執行：<是／否／待確認>
- 已驗證：<內容>
- 未完成：<內容｜無>

## 下一步
1. <最小可執行步驟>

## 注意事項
- <風險｜無>

## 最近更新
- 時間：<YYYY-MM-DD HH:mm timezone>
- 更新者：<Agent>
- 電腦：<runtime 名稱｜UNKNOWN>
- 成果 commit：<SHA｜未提交｜NOT_CONFIGURED>
- GitHub：<VERIFIED remote SHA｜PENDING_CHECKPOINT｜BLOCKED｜NOT_CONFIGURED>
```

## 固定回報

```markdown
# 初始化報告

- 專案：<名稱>
- 狀態：<VERIFIED｜PARTIAL｜BLOCKED>
- Agent／電腦：<Agent> @ <電腦>
- 四檔：<AGENTS／README／CHANGELOG／handoff 狀態>
- 三技能：<版本與來源>
- ReadyGate：<VERIFIED｜Lite 不需要｜PARTIAL>
- Manifest：<VALID manual｜VALID standing_scoped｜PARTIAL｜NOT_CONFIGURED>
- Git／GitHub：<top-level、remote identity、branch、checkpoint SHA／狀態>
- 尚待處理：<最多三項｜無>
```

## 不做

- 不覆寫既有專案檔、不建立 GitHub repository。
- 不保存裝置絕對路徑、email、token 或 credential。
- 不 force push、不自動 merge／rebase、不切換到其他 remote，不建立 tag／release、不合併 PR、不刪除／封存或變更權限。
- 不 clone 到非空目錄；要查看舊版時建立 restore branch，已發布錯誤使用 `git revert`，不得用舊內容覆蓋目前工作樹。
- 不讀寫 Notion、Obsidian 或其他外部知識庫。
