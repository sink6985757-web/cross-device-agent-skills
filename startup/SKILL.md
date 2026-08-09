---
name: startup
description: 專案開工與接續。當使用者說開工、startup、開始工作、繼續、下一步或上次做到哪時使用；唯讀 AGENTS.md、handoff.md 與 Git 狀態，必要時只讀 CHANGELOG.md 最近一節，依固定格式回報，不修改任何專案或外部系統。
---

# Startup

本檔同時包含操作規則、相依關係與固定輸出。Startup 永遠唯讀。

## 權威與相依

| 角色 | 來源 | 定義 |
|---|---|---|
| 公開來源 | `https://github.com/sink6985757-web/cross-device-agent-skills` | 三技能發行權威 |
| 執行來源 | `~/.agents/skills/startup/SKILL.md` | Agent 實際讀取副本 |
| 前一流程 | `../initial/SKILL.md` | 缺少必要檔案時建議使用 |
| 後一流程 | `../shutdown/SKILL.md` | 工作結束時更新版本與交接 |
| 高風險路由 | `~/.agents/skills/readygate/SKILL.md` | 只有任務風險需要時提示，不在 Startup 內啟動寫入 |

## 讀取契約

必讀：

1. `AGENTS.md`：穩定規則與權威。
2. `handoff.md`：上次狀態與下一步。
3. `git status --short --branch`：本機工作樹。

選讀：

- `CHANGELOG.md` 最近一節：只有 handoff 要求確認近期版本，或使用者詢問版本時。
- `README.md`：只有任務涉及安裝、使用方法或公開文案時。

外部筆記與知識庫不屬於 Startup 讀取面。

## 流程

1. 找到專案 Git 根；辨識本次 Agent 與 runtime 電腦名稱。Windows 使用 `[Environment]::MachineName`，Linux／macOS 使用 `hostname`；失敗寫 `UNKNOWN`。
2. 讀取必讀檔；`AGENTS.md` 或 `handoff.md` 任一缺少就標示 `PARTIAL`，建議執行 `initial`，不得自行建立。
3. 摘要目標、目前狀態、上次 Agent／電腦、下一步與注意事項，不全文重述檔案。
4. 有 remote 時可 `git fetch`；不得 pull、merge、checkout、stage、commit 或修改檔案。未 fetch 就明寫遠端未驗證。
5. 若任務涉及批次治理、公開發布、搬移、封存、權限或其他高風險操作，在建議下一步標示應使用 Full Core／ReadyGate。
6. 依固定回報輸出，下一步最多三項，然後等待使用者選擇。

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
- 工作樹：<乾淨｜有 N 項變更｜NOT_CONFIGURED>
- 遠端：<一致｜領先 N｜落後 N｜未 fetch｜NOT_CONFIGURED>

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

- 不修改 `AGENTS.md`、`README.md`、`CHANGELOG.md`、`handoff.md` 或 Git。
- 不讀寫 Notion、Obsidian 或其他外部知識庫。
- 不根據電腦名稱判斷同步成功。
- 不宣稱未 fetch／未回讀的遠端狀態已驗證。
