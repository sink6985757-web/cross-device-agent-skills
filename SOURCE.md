# SOURCE：跨系統唯一入口

只需依作業系統執行同一個 Source 概念：

```text
Windows       ./source.ps1
Linux/macOS   ./source.sh
```

無參數會自動判定：沒有 state → 初始化；`READY` → 開工；工作中／等待外部 → 顯示 checkpoint 與唯一下一步。

## 全新電腦一鍵部署

私有 repository 的首次登入不能繞過。先完成 `gh auth login`，或由已授權的 Google Drive／USB 取得本 repository，再執行一次 bootstrap。

### Windows

```powershell
$sourceBootstrap = Join-Path $env:TEMP ("source-" + [Guid]::NewGuid())
gh repo clone sink6985757-web/cross-device-agent-skills $sourceBootstrap
& "$sourceBootstrap\source.ps1" -Action bootstrap -ProjectRoot "<專案路徑>" -Yes
```

缺少 Python 時，`-Yes` 允許透過 winget 安裝官方 Python 套件。

### Linux／macOS

```bash
source_bootstrap="$(mktemp -d)"
gh repo clone sink6985757-web/cross-device-agent-skills "$source_bootstrap"
"$source_bootstrap/source.sh" bootstrap --project-root "<專案路徑>" --yes
```

Linux 支援 apt、dnf、pacman、zypper、apk；macOS 使用 Homebrew。`--yes` 才允許安裝 Python、Git、gh、chezmoi。安裝後會部署五個 managed skills、Agent adapter、Source launchers、authority manifest 與 checkpoint。

## 日常口令

| 意圖 | Windows | Linux／macOS |
|---|---|---|
| 自動／續接 | `./source.ps1` | `./source.sh` |
| 下一步 | `./source.ps1 -Action next` | `./source.sh next` |
| 檢查 | `./source.ps1 -Action doctor` | `./source.sh doctor` |
| 收工 | `./source.ps1 -Action finish -CommitMessage "成果" -Yes` | `./source.sh finish --commit-message "成果" --yes` |

## 路徑規則

| 類型 | 規則 |
|---|---|
| 專案 canonical JSON | 只能使用專案 root-relative 路徑，例如 `docs/spec.md` |
| 個人共用核心 | 只能使用 home-relative 表示，例如 `~/.agents/skills` |
| Runtime | 可解析磁碟機、mount point、`$HOME`、temp、Git／chezmoi 實際位置，但不得回寫 canonical JSON |
| URL／Page ID | 是外部識別，不是裝置檔案路徑，可以保存 |
| 禁止 | `C:\Users\...`、`/home/name/...`、`/Users/name/...`、UNC 等裝置綁定路徑 |

`doctor` 會遞迴檢查 config、state、authority；任何持久化絕對路徑都會 `BLOCKED`。跨機資訊只保存 OS 類型，不保存電腦名稱。

## 不可直接修改的權威層

| 類別 | 檔案 | 寫入者 |
|---|---|---|
| `PROTECTED` | `SOURCE.md`、`AGENTS.md`、`.source/config.json`、launchers、Git 文字／排除規則 | 僅 formal change |
| `GENERATED` | `.source/state.json`、`handoff.md`、`.source/runtime/` | 僅 Source engine |
| `PROJECT_WORK` | authority manifest 未列入的專案工作檔 | 使用者／Agent 依任務修改 |
| `EXTERNAL_READ_ONLY` | Notion 主 Prompt | 永不修改 |

`PROTECTED` 由 `.source/authority.json`、`.source/authority.sha256` 與 SHA-256 鎖定；支援權限的檔案系統再套用 OS 唯讀。Google Drive 等不保留唯讀 attribute 的虛擬掛載會顯示 `HASH_ENFORCED`，任何未封存變更仍會阻止開工與收工。正式變更流程：

```text
authority-unlock --yes → 修改核准檔案 → 測試 → authority-seal --yes → doctor
```

任何 signature／hash 不符或 formal change 未封存都不能完成收工；支援實體唯讀但鎖失效時同樣 `BLOCKED`。

## Connector 邊界

- Git／GitHub／Skill／chezmoi：engine 執行並驗證。
- GDrive：只做 runtime 偵測，不保存實際 mount path。
- Notion／Obsidian：Agent 回讀成功才回填 `VERIFIED`；Prompt 永遠只讀。
- CDN：provider／target 未設定時保持 `NOT_CONFIGURED`，不猜測部署位置。
