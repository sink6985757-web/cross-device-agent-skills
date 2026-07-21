# Platform deployment contract

只有部署或診斷 OS adapter 時讀本檔。

## 支援範圍

| OS | 入口 | 必要 | 自動安裝器 |
|---|---|---|---|
| Windows 10/11 | `source.ps1` | PowerShell 5.1+、Python 3、Git | winget 安裝 Python；Git／gh／chezmoi 由 doctor 檢查 |
| Debian／Ubuntu | `source.sh` | POSIX shell、Python 3、Git | apt |
| Fedora／RHEL | `source.sh` | POSIX shell、Python 3、Git | dnf |
| Arch | `source.sh` | POSIX shell、Python 3、Git | pacman |
| openSUSE | `source.sh` | POSIX shell、Python 3、Git | zypper |
| Alpine | `source.sh` | POSIX shell、Python 3、Git | apk |
| macOS | `source.sh` | POSIX shell、Python 3、Git | Homebrew；不存在時以官方安裝器建立 |

套件安裝會修改 OS，只有明確 `-Yes`／`--yes` 才執行。其他 Linux 發行版保持 `BLOCKED`，不得猜套件命令。

## 路徑權威

- 專案內保存：只用 root-relative 路徑。
- 個人共用核心：文件使用 `~/.agents/skills`；執行時才把 `~` 解析成 home。
- Agent adapter：Unix 的 `~/.claude/skills` 只建立 symlink；衝突不覆寫。Windows 使用既有 adapter installer。
- 專案根目錄可由命令列傳入絕對路徑，但 engine 只在記憶體使用，不回寫 config／state／authority。

以下是必要的 runtime-only 絕對路徑例外，不是 canonical state：

- Windows 的 winget package 實際安裝位置與 temp 目錄。
- Linux 的 package manager、`sudo`、home、mount point 與 temp 解析結果。
- Apple Silicon Homebrew 的 `/opt/homebrew/bin/brew` 與 Intel Homebrew 的 `/usr/local/bin/brew` fallback。
- `git`、`gh`、`python3`、`chezmoi source-path` 回傳的可執行檔或工作目錄。

所有 runtime 訊息寫入 checkpoint 前都必須轉成 `~`、`.` 或 `<runtime-path>`。

## 權限與換機

1. GitHub／Notion 首次登入必須由使用者完成；不複製 credential。
2. `bootstrap` 安裝 skill、adapter、launcher、config、state 與 authority gate。
3. Windows 使用 read-only attribute；Linux／macOS 移除 owner／group／other write bits。Google Drive 等不支援唯讀的掛載改由 signature＋hash 強制攔截並顯示 `HASH_ENFORCED`。
4. Git checkout 不保留唯讀屬性時，第一次正常 Source 動作會在 hash 通過後重新套用 lock；檔案系統不支援時不假裝成功。
5. 下一台電腦只依 Git、root-relative state 與 connector checkpoint 續接，不依原電腦名稱或磁碟路徑。
