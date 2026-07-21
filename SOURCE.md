# SOURCE：唯一入口

你只需要記一個入口：

```powershell
./source.ps1
```

它會自動判定：

```text
沒有狀態 → 初始化
READY    → 開工
WORKING  → 顯示中斷點與下一步
等待外部 → 顯示尚缺的 Notion／Obsidian／CDN checkpoint
```

## 全新電腦／全新專案

唯一不可省略的是 GitHub 身分驗證；私有 repo 不應繞過權限。

```powershell
gh auth login
$sourceBootstrap = Join-Path $env:TEMP ("source-" + [Guid]::NewGuid())
gh repo clone sink6985757-web/cross-device-agent-skills $sourceBootstrap
& "$sourceBootstrap\source.ps1" -Action bootstrap -ProjectRoot "<你的專案路徑>" -Yes
```

`bootstrap` 會安裝 `source` 與四個相容轉接 Skill、建立 Agent adapters、初始化專案狀態與安全檔案；缺少可選工具時保留 checkpoint，不會讓已完成層級回滾。

## 日常口令

| 口令 | 等同動作 |
|---|---|
| `source`／「下一步」 | `./source.ps1 -Action next` |
| 「初始化」 | `./source.ps1 -Action init` |
| 「開工」 | `./source.ps1 -Action start` |
| 「收工」 | `./source.ps1 -Action finish -CommitMessage "具體成果"` |
| 「檢查」 | `./source.ps1 -Action doctor` |

`project-init`、`startup`、`shutdown` 仍可觸發，但都只轉接到同一個 `source` 狀態機；`notion-conversation-log` 也只轉接到同一個 Notion checkpoint，不再建立重複 Log。

## Canonical state

- `.source/config.json`：可攜設定；只允許 root-relative 路徑與公開識別。
- `.source/state.json`：phase、revision、session、connector checkpoint、唯一下一步。
- `handoff.md`：由 state 產生的給人看摘要。
- `AGENTS.md`：讓不同 Agent 自動找到本入口。

不要手工改 state。中斷、權限不足或工具缺少時，再執行 `./source.ps1` 就會從 checkpoint 接續。

## Connector 邊界

- Git／GitHub／Skill／chezmoi：腳本可驗證並執行。
- GDrive：只偵測，不保存裝置絕對路徑。
- Notion／Obsidian：由 Agent connector 完成後回填狀態；Prompt 永遠只讀。
- CDN：目前沒有 provider／target，狀態固定 `NOT_CONFIGURED`；設定完整前不會猜測部署。

## 安全保證

- 既有檔案不覆寫；Skill 衝突先備份，必須加 `-Yes` 才替換。
- 不自動 pull、不提交未知 untracked、不提交敏感檔。
- repo 預設 private；驗證失敗標示 `PARTIAL`／`BLOCKED`，不假裝成功。
- canonical 設定不保存磁碟絕對路徑、token、cookie 或 credentials。
