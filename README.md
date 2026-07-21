# Source：跨電腦、跨 Agent 的專案工作流

> 對人只保留三個口令：**初始化專案、開工、收工**；對系統只保留一個核心：`source.py`。

這個版本延續早期 Co-Agent 模板「低認知負擔、精簡交接、詳細脈絡分層保存」的優點，再以 Source 狀態機補上跨平台、可恢復、權威鎖、Hub／Child 隔離與誠實降級。

## 先記住這三句

| 你說 | Source 動作 | 結果 |
|---|---|---|
| `初始化專案` | `init`；多專案環境使用 `hub-init`／`child-create` | 建立不覆寫既有檔案的專案骨架 |
| `開工` | `start`；中斷後使用 `next` | 讀取 checkpoint、檢查 Git 與 session lease |
| `收工` | `finish`，再完成必要 connector | 保存 checkpoint、private GitHub 備份與外部紀錄 |

`project-init`、`startup`、`shutdown` 與 `notion-conversation-log` 都只是薄入口；真正邏輯只存在於 `source/scripts/source.py`，避免多份 SOP 漂移。

## 四層資訊，各做一件事

| 層級 | 保存內容 | 讀取時機 | 失敗時 |
|---|---|---|---|
| L1 專案 | `AGENTS.md`、`.source/state.json`、GENERATED `handoff.md` | 每次 Source 動作 | 核心層，不能略過 |
| L2 GitHub | private Git、版本與回滾點 | 開工檢查、收工推送 | 明確標示 `BLOCKED`／`PARTIAL` |
| L3 Obsidian | 決策原因、踩坑、詳細時間線 | 需要完整脈絡時 | 保留 checkpoint，稍後補寫 |
| L4 Notion | Knowledge Master 的正式結論與週期頁 | 正式治理與跨專案索引 | 未回讀不得標 `VERIFIED` |

Google Drive 只負責檔案同步，不被當成分散式鎖。每個 Child 擁有自己的 Git、state、session log 與 lease；Hub 只接收 UUID append-only event，避免多台電腦共用同一個可變 state 或 Git index。

## 與原始 Co-Agent 模板的混合方式

保留的概念：

- 三個自然語言口令，使用者不必記住完整工具鏈。
- 精簡 checkpoint 與詳細 Obsidian 脈絡分家。
- GitHub 預設 private；缺工具時優雅降級，不假裝完成。
- 任何 Agent 都先讀共同入口，不綁定單一 AI 產品。

新版基準取代的部分：

- 不再由三個 Skill 各自保存一份長 SOP；全部交給單一 Python engine。
- 不把電腦名稱、磁碟路徑或 credential 寫入 canonical state。
- 不手改 `.source/state.json` 或 `handoff.md`；兩者只能由 engine 產生。
- 不用「上一台電腦名稱」推測併發安全；改用 Child 隔離、active lease 與 mutation lock。
- Connector 使用 `VERIFIED`、`PARTIAL`、`BLOCKED`、`NOT_CONFIGURED` 等實際狀態，總覽不得掩蓋未完成項目。

概念參考：[mathruffian-dot/cross-device-agent-skills](https://github.com/mathruffian-dot/cross-device-agent-skills)。參考庫未附授權檔；本專案只採用高階設計概念，文件與實作均依 Source 架構重寫。

## 安裝

### 必要條件

- Git
- Python 3
- Windows PowerShell 5.1+，或 Linux／macOS 的 POSIX shell

選用：

- `gh`：登入與建立 private GitHub repository
- `chezmoi`：同步 `~/.agents` 共用核心
- Obsidian、Notion connector：啟用 L3／L4

### Windows

```powershell
gh auth login
gh repo clone sink6985757-web/cross-device-agent-skills
Set-Location .\cross-device-agent-skills
.\source.ps1 -Action bootstrap -Yes
.\source.ps1 -Action doctor
```

沒有 `gh` 時，可在已具備 GitHub 認證的環境使用 `git clone`。`-Yes` 只授權支援的依賴與技能部署；不會保存 token 或覆寫既有專案檔。

### Linux／macOS

```bash
gh auth login
gh repo clone sink6985757-web/cross-device-agent-skills
cd cross-device-agent-skills
./source.sh bootstrap --yes
./source.sh doctor
```

部署後，共用 Skill 的正式位置是 `~/.agents/skills`。Agent 專屬目錄只使用薄轉接或原生 discovery，不複製另一份 Skill。

## 建立與使用專案

最簡單的方式是直接對 Agent 說「初始化專案」、「開工」或「收工」。需要明確 CLI 時：

### 單一專案

```powershell
# Windows；在目標專案資料夾執行
& "$HOME\.agents\skills\source\scripts\source.ps1" -Action init -ProjectRoot (Get-Location).Path -ProjectName "我的專案"
.\source.ps1 -Action start
.\source.ps1 -Action finish -CommitMessage "完成可驗證成果"
```

```bash
# Linux／macOS；在目標專案資料夾執行
python3 "$HOME/.agents/skills/source/scripts/source.py" init --project-root "$PWD" --project-name "我的專案"
./source.sh start
./source.sh finish --commit-message "完成可驗證成果"
```

初始化採 `copy-if-missing`：已有 `SOURCE.md`、`AGENTS.md` 或其他專案檔時不覆寫。若要同時建立 private GitHub repository，加入 Windows `-CreateRemote -Yes` 或 Unix `--create-remote --yes`。

### Hub／Child 多專案

```powershell
.\source.ps1 -Action hub-init -ProjectName "我的工作主幹"
.\source.ps1 -Action child-create -ChildName "第一個專案"
Set-Location .\projects\第一個專案
.\source.ps1
```

```bash
./source.sh hub-init --project-name "我的工作主幹"
./source.sh child-create --child-name "第一個專案"
cd projects/第一個專案
./source.sh
```

無參數 Source 會依 state 自動選擇 `init`、`start` 或 `next`。主幹管理者可用 `hub-status` 查看全局，以 `hub-sync --yes` 收斂 Child 事件。

## 權威、回滾與安全

- `PROTECTED`：只能 `authority-unlock --yes → 修改 → 測試 → authority-seal --yes`。
- `GENERATED`：只能由 Source engine 寫入。
- canonical JSON 只保存 root-relative 路徑、URL 與外部 ID。
- 不提交 `.env`、API key、token、cookie、私鑰、credential cache 或未知 untracked 檔。
- Google Drive 不支援持久唯讀時顯示 `HASH_ENFORCED`，仍由 signature＋SHA-256 強制驗證。
- 每次交接前執行 `doctor`；完整細節見 [SOURCE.md](SOURCE.md)。

## 驗證

```powershell
python .\tests\source.tests.py
python .\tests\hub.tests.py
powershell -NoProfile -ExecutionPolicy Bypass -File .\tests\source.tests.ps1
.\source.ps1 -Action doctor
```

CI 會在 Windows、Ubuntu 與 macOS 重跑生命週期、Hub／Child、adapter 與 diff hygiene 測試。
