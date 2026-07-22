---
name: startup
description: 專案開工與接續。當使用者說開工、startup、開始工作、繼續、下一步或上次做到哪時使用；只讀 AGENTS.md、handoff.md 與 Git 狀態，再依固定模板回報，不修改專案。
---

# Startup

固定使用同目錄 `TEMPLATE.md`；本技能只有讀取與回報。

## 流程

1. 找到專案根目錄，辨識本次 Agent 名稱與 runtime 本機電腦名稱；Windows 讀取 `[Environment]::MachineName`，Linux／macOS 執行 `hostname`，失敗就寫 `UNKNOWN`。再讀取 `AGENTS.md`、`handoff.md`；任一缺少就標示 `PARTIAL`，建議先執行 `initial`，不得自行補建。
2. 摘要目標、目前狀態、下一步與注意事項，並分開列出本次 Agent／電腦及 `handoff.md` 記錄的上次 Agent／電腦；不全文複述兩個檔案。
3. 若有 Git，執行 read-only `git status --short --branch`；遠端存在時可 `git fetch`，但不得自動 pull、merge、checkout 或修改檔案。
4. 若 `AGENTS.md` 登記 Obsidian，只列 vault-relative 路徑；只有 handoff 明確需要或使用者要求時才讀詳細筆記。
5. 依 `TEMPLATE.md` 回報，下一步最多三項；完成後等待使用者選擇，不自行展開其他工作。

## 不做

- 不修改 `AGENTS.md`、`handoff.md`、Obsidian 或 Git。
- 不根據電腦名稱判斷同步狀態。
- 不宣稱未 fetch／未回讀的遠端狀態已驗證。
