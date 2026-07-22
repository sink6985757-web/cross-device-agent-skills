---
name: initial
description: 初始化單一專案與本機 Agent 環境。當使用者說初始化專案、initial、init、開新專案、部署三技能或建立 AGENTS.md／handoff.md 時使用；偵測可用工具，以 checklist 部署必要檔案，不覆寫既有內容。
---

# Initial

只處理「第一次部署」；固定使用同目錄 `TEMPLATE.md`。

## 流程

1. 確認專案根目錄，讀取既有 `README.md`、`AGENTS.md`、`handoff.md` 與 Git 狀態；已有檔案不得直接覆寫。
2. 在 runtime 偵測 OS、Git、`gh auth status`、共用技能目錄、已安裝 Agent、可用 Obsidian vault 與本機電腦名稱。Windows 讀取 `[Environment]::MachineName`，Linux／macOS 執行 `hostname`；失敗就寫 `UNKNOWN` 並標示 `PARTIAL`，不得猜測。不得讀取或保存 token、`.env`、credential cache 或裝置絕對路徑。
3. 檢查 `initial`、`startup`、`shutdown` 是否存在於 `~/.agents/skills`：
   - 已存在且相同：保留。
   - 已存在但不同：先備份，再由使用者確認是否更新。
   - 不存在：從目前核准的 repository 安裝。
4. Agent 不原生支援 `~/.agents/skills` 時，只建立 symlink／junction 或設定外部技能目錄，不複製另一份 Skill。
5. 依 `TEMPLATE.md` 建立缺少的 `AGENTS.md` 與 `handoff.md`；在初始化報告與 `handoff.md` 分別寫入本次 Agent 名稱及本機電腦名稱。專案名稱、目標與時程沒有證據時留待確認，不得猜測。
6. Git 可用但尚未初始化時建立 `main`；只建立最小 `.gitignore`。`gh` 已登入且使用者授權發布時，才建立 private remote。
7. 若找到 Obsidian vault，建立或更新 `<專案名>/專案工作流程.md`，並只把 vault-relative 路徑寫進 `AGENTS.md`；找不到就標示 `NOT_CONFIGURED`。
8. 逐項回讀所有建立內容，最後用 `TEMPLATE.md` 的部署 checklist 回報 `VERIFIED`／`PARTIAL`／`BLOCKED`。

## 不做

- 不覆寫既有專案檔。
- 不建立 public repository。
- 不保存裝置絕對路徑、email 或認證；電腦名稱只寫入交接、固定回報與 Obsidian 最近更動，不作為同步成功證據。
- 不安裝 `source`、Hub、Notion adapter、runtime engine 或 session database。
