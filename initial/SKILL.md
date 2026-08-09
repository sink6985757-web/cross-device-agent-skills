---
name: initial
description: 初始化單一專案與本機 Agent 環境。當使用者說初始化專案、initial、init、開新專案或部署生命週期技能時使用；建立或保留 AGENTS.md、README.md、CHANGELOG.md、handoff.md，部署共用技能並回讀驗證，不覆寫既有內容，也不整合外部知識庫。
---

# Initial

只處理第一次部署或既有專案缺件修復。本檔同時包含操作規則、依賴關係與固定輸出，不依賴另一份模板。

## 權威與相依

| 角色 | 權威／路徑 | 定義 |
|---|---|---|
| 公開安裝來源 | `https://github.com/sink6985757-web/cross-device-agent-skills` | `initial`／`startup`／`shutdown` 的發行權威 |
| 執行來源 | `~/.agents/skills/initial/SKILL.md` | Agent 實際讀取的安裝副本 |
| Full Core | `https://github.com/sink6985757-web/cross-device-agent-workflow-core` | 首次部署、完整治理與四技能相容檢查 |
| ReadyGate | `~/.agents/skills/readygate/SKILL.md` | 批次、高風險、發布、搬移、封存與權限變更閘門 |
| 下一流程 | `../startup/SKILL.md` | 初始化完成後的日常開工 |

## 專案四檔契約

| 檔案 | 責任 | Initial 動作 |
|---|---|---|
| `AGENTS.md` | 穩定規則、權威、邊界 | 缺少才建立 |
| `README.md` | GitHub 人類安裝、Agent／Tool 安裝、使用與公開版本文案 | 缺少才建立；資料不足留待確認 |
| `CHANGELOG.md` | 每次收工的近期修改、驗證與 delivery 狀態 | 缺少才建立 |
| `handoff.md` | 當下狀態、下一步、風險與唯一續跑點 | 缺少才建立 |

外部筆記、Notion、Obsidian 或其他知識庫不屬於本契約；只有獨立、明確提出的任務才可處理。

## 流程

1. 確認專案 Git 根目錄；讀取既有 `README.md`、`AGENTS.md`、`CHANGELOG.md`、`handoff.md` 與 `git status --short --branch`。任何既有檔案都不得直接覆寫。
2. 在 runtime 偵測 OS、Git、`gh auth status`、`~/.agents/skills`、本次 Agent 與本機電腦名稱。Windows 使用 `[Environment]::MachineName`，Linux／macOS 使用 `hostname`；失敗寫 `UNKNOWN` 並標示 `PARTIAL`。不得讀取 token、`.env`、credential cache 或裝置私密資料。
3. 檢查 `initial`、`startup`、`shutdown` 是否各只有 `SKILL.md` 且版本相容。Full Core profile 另檢查 `readygate`；公開 Lite profile 不強制安裝 ReadyGate。
4. 已存在但內容不同的共用 Skill 不得直接覆蓋；先顯示來源、版本與差異，取得明確更新授權。Agent 不原生支援 `~/.agents/skills` 時，只建立薄轉接，不複製另一份設計權威。
5. 依下列內嵌骨架建立缺少的專案四檔。沒有證據的名稱、版本、安裝命令與時程保留 `<待確認>`，不得猜測。
6. Git 尚未初始化時，只有在使用者授權後才建立 `main` 與最小 `.gitignore`。建立 remote、commit、push、公開範圍或權限變更必須交由確認工作單／ReadyGate。
7. 回讀全部建立內容；檢查相對路徑、UTF-8、`git diff --check`、敏感資訊模式與未知檔案，最後回報 `VERIFIED`／`PARTIAL`／`BLOCKED`。

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

## 整合
- GitHub：<repository｜NOT_CONFIGURED>
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
- GitHub：<VERIFIED｜LOCAL_ONLY｜BLOCKED｜NOT_CONFIGURED>
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
- Git／GitHub：<狀態>
- 尚待處理：<最多三項｜無>
```

## 不做

- 不覆寫既有專案檔、不建立 public repository。
- 不保存裝置絕對路徑、email、token 或 credential。
- 不自動 commit、push、發布、搬移、封存或變更權限。
- 不讀寫 Notion、Obsidian 或其他外部知識庫。
