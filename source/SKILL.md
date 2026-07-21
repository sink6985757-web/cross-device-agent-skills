---
name: source
description: 跨 Windows、Linux、macOS 的單一專案生命週期技能。當使用者說 source、初始化、開工、收工、繼續、下一步、工作到哪、換電腦、換作業系統、部署技能或同步專案時使用；以可恢復狀態機、相對路徑與權威檔鎖定統一 GitHub、chezmoi、Obsidian、Notion 與可選 CDN connector。
---

# Source

以腳本為準，不在對話中重寫 SOP。

## 執行

1. Windows 執行 `./source.ps1`；Linux／macOS 執行 `./source.sh`。
2. 無參數時依 `.source/state.json` 自動選擇：未初始化 → `init`；`READY` → `start`；其餘 → `next`。
3. 明確口令對應：初始化 → `init`、開工 → `start`、收工 → `finish`、下一步 → `next`。
4. 不得手改 `.source/state.json` 或 `handoff.md`；它們只能由 engine 產生。
5. 全新電腦、套件管理器或必要絕對路徑有疑問時讀 [platforms.md](references/platforms.md)。

```text
Windows:       ./source.ps1 -Action doctor
Linux/macOS:  ./source.sh doctor
```

## 權威閘門

- `.source/authority.json` 與 `.source/authority.sha256` 定義不可直接修改的檔案。
- 正式修改必須先執行 `authority-unlock --yes`，完成後執行 `authority-seal --yes`；一般工作不得解除唯讀。
- canonical JSON 只保存 root-relative 路徑；`~` 與 OS 絕對路徑只允許在 runtime 解析。
- 若權威 signature、hash、唯讀權限或路徑檢查失敗，標示 `BLOCKED`，不得收工。

## Connector

腳本處理本地、Git、GitHub、Skill 與 chezmoi。只有狀態為 `PENDING_AGENT` 時才讀 [connectors.md](references/connectors.md)，完成外部動作後執行 `complete`。

## 不變條件

- 不自動 pull、不提交未知 untracked 或敏感檔；衝突先備份。
- private repo 與明確認證為預設；不保存 token、cookie、credential 或裝置絕對路徑。
- Prompt 頁永遠只讀；Notion 同主題同週只更新原 Page ID。
- 不覆寫既有專案檔；缺工具或權限時保存 checkpoint 與唯一下一步。
