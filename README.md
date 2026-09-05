# Cross-Device Agent Skills

## 固定來源與專案部署

以下 source checkpoint 已於 2026-09-05 推送並回讀；各專案 manifest 固定到這些包含 v2 契約的 commit。

| 來源 | Repository | Commit |
|---|---|---|
| core | `sink6985757-web/cross-device-agent-workflow-core` | `0816aa2d53569d062f6448b874e8ddebf923abb0` |
| lifecycle | `sink6985757-web/cross-device-agent-skills` | `7a377045b613ed4b9b1e7e5a17c1251dbd213ddf` |
| readygate | `sink6985757-web/readygate-skill-chatgpt-app` | `b7756661c98b69ca8766bfdfec833eb54ff74b4c` |

`newday` manual pilot 已通過；active chezmoi source、runtime 與 Drive dotfiles mirror 的四技能雜湊一致。Template 已填入可回讀 authority SHA，部署新 Project 時仍須填寫實際 repository identity／routing，不可沿用 example/project。

## 2026-09-05 維護更新

本次 source 更新包含initial／startup／shutdown 的 manifest、remote checkpoint 與授權延續契約。版本以 Git commit 識別；既有發行 tag 保持不變。當本次對話或已確認工作單已明列更新、commit／push 與驗收範圍，沿用該授權完成，不為相同動作重複提問；未涵蓋的動作仍停在確認點。Startup 維持唯讀，完成讀取報告後可轉入已授權的獨立工作階段。

目前交接與驗收範圍見 [handoff.md](handoff.md)，歷史變更見 [CHANGELOG.md](CHANGELOG.md)。

跨裝置專案生命週期的公開 Lite 套件，只包含三個自足技能：`initial`、`startup`、`shutdown`。適合 Codex、Claude、Gemini、Hermes 或其他能讀取 Markdown 技能的 Agent。

目前 GitHub 發行版：`v1.1.1`
GitHub `main` 候選版本：`v2.0.0`（source 已 push；尚未 tag／Release）

## 套件內容

```text
cross-device-agent-skills/
├─ initial/SKILL.md
├─ startup/SKILL.md
├─ shutdown/SKILL.md
├─ AGENTS.md
├─ CHANGELOG.md
├─ handoff.md
└─ README.md
```

每個技能目錄只允許一個 `SKILL.md`。流程、相依、模板與固定輸出全部內嵌，不再使用 `TEMPLATE.md`。

## 三技能的精確定義

| 技能 | 進入條件 | 核心責任 | 允許寫入 | 硬停止點 |
|---|---|---|---|---|
| `initial` | 新專案第一次建立治理結構、既有專案缺件，或明確部署技能 | 建立／驗證四檔與 portable manifest，確認實際 Git root、remote identity 及 bootstrap checkpoint | 建立缺件；`manual` 停在確認點，`standing_scoped` 通過限制後可 commit／push／readback | 初始化報告與 checkpoint 結果完成即停止，不自動開始日常工作 |
| `startup` | 每次開始或接續一個既有專案 | 唯讀 manifest、`AGENTS.md`、`handoff.md`，fetch 並對照最後 GitHub checkpoint | 不修改專案內容；不建立空 commit | 開工報告完成即停止；dirty／ahead／behind／diverged／wrong remote 各自路由 |
| `shutdown` | 每次工作階段結束、換電腦或需要留下交接 | 記錄修改與驗證，依 manifest 建立可回滾的 GitHub checkpoint | 每次更新 changelog／handoff；`manual` 等確認，`standing_scoped` 只處理 allowlist | 遠端 SHA 回讀才完成；超出 standing scope 就停止並進 ReadyGate |

標準路由：

```text
新專案／治理缺件 → initial → 停止
既有專案每次開始 → startup → 等待工作選擇
確認工作 → 執行與驗證
每次工作結束 → shutdown → 本機交接 → manual 確認點／standing_scoped checkpoint
```

ReadyGate 是按風險插入的橫向閘門，不是 Lite 的第四個固定階段。一般唯讀 `startup` 不啟動 ReadyGate；若工作涉及重大返工、批次、公開發布、刪除、搬移、封存、權限或其他不可逆／外部動作，先走 Requirement Gate，完成後再走 Delivery Gate。

## 權威與相依關係

| 層級 | Canonical | 責任 |
|---|---|---|
| Lite 公開發行 | 本 repository | `initial`／`startup`／`shutdown` 的安裝與版本權威 |
| Runtime 安裝 | `~/.agents/skills/<skill>/SKILL.md` | Agent 實際讀取的執行副本，不是發行權威 |
| Full Core | [`cross-device-agent-workflow-core`](https://github.com/sink6985757-web/cross-device-agent-workflow-core) | 首次部署、完整治理、相容性驗證與 Core profile |
| ReadyGate | [`readygate-skill-chatgpt-app`](https://github.com/sink6985757-web/readygate-skill-chatgpt-app) | commit、push、發布、搬移、封存、權限與其他高風險動作的工作單／閘門 |
| 專案狀態 | 各專案 repository | 專案自己的四檔與 Git 歷史才是該專案權威 |

Core profile 使用四個技能：Lite 三技能加 `readygate`。Lite profile 本身不強制安裝 ReadyGate；專案 checkpoint 預設為 `manual`。只有專案已經用受治理 `.agents/project-lifecycle.json` 設為 `standing_scoped`，單獨口令「收工」才涵蓋該 manifest 事先授權的窄範圍 commit／push／readback。

Notion、Obsidian、Knowledge Master 與其他外部知識庫皆為 `ON_DEMAND_ONLY`，不屬於 initial／startup／shutdown 流程。

## 專案四檔契約

| 檔案 | 唯一責任 | 更新時機 |
|---|---|---|
| `AGENTS.md` | 穩定規則、權威來源、邊界與相依路徑 | 規則或架構真的改變時 |
| `README.md` | GitHub 人類安裝、Agent／Tool 安裝、使用、公開版本與最新變更文案 | 每次授權 GitHub delivery 前 |
| `CHANGELOG.md` | 近期修改、驗證結果、版本與 delivery 狀態 | 每次收工 |
| `handoff.md` | 現況、未完成事項、風險與唯一續跑點 | 每次收工，以目前狀態更新 |

`CHANGELOG.md` 是專案內獨立、可版本控制的 Markdown 變更紀錄；不需要 Obsidian 或專門的 RCD 資料夾。

## Part、Project 與 GitHub checkpoint

權威系統採三層模型：

1. **Authority Kernel**：Full Core、Lite、ReadyGate 的共同 schema、版本與規則。
2. **Part routing → Project instance**：Part 只是分類值；每個實際 repository 是獨立 Project，自己的 Git top-level、remote、branch 與 `.agents/project-lifecycle.json` 才是 Git 邊界。
3. **Device binding**：裝置絕對路徑、名稱與登入狀態只存在 runtime／ignored `policy.local.yaml`，不得寫入 canonical manifest。

三個流程在 GitHub 的對照意義不同：

| 流程 | GitHub 對照 |
|---|---|
| Initial | 對初始化變更建立 bootstrap checkpoint；若無既有 remote 或 push 失敗，標 `PARTIAL`，不自動建立 repository |
| Startup | fetch 後記錄最後 remote SHA，分類 clean／dirty／ahead／behind／diverged／wrong remote；不建立空 commit |
| Shutdown | 對本次 allowlist 內成果建立 checkpoint commit，push 目前工作 branch 並回讀 remote SHA |

manifest 有兩種模式：

- `manual`：預設；每次 commit／push 仍需要當次確認。
- `standing_scoped`：專案事先授權例行 Initial／Shutdown checkpoint，但僅限既有且 identity-matching 的 remote、實際 Git root、目前工作 branch、manifest allowlist、非 force push，且不能有 secret、unknown untracked、divergence 或驗證失敗。

`standing_scoped` 永遠不包含建立 repository、force push、auto merge／rebase、tag／release、PR merge、刪除／封存或權限變更。變更 standing policy 本身也要先走確認工作單／ReadyGate。

## 人類安裝

### Windows PowerShell

```powershell
git clone https://github.com/sink6985757-web/cross-device-agent-skills.git
$repo = Resolve-Path .\cross-device-agent-skills
$skillRoot = Join-Path $HOME '.agents\skills'

New-Item -ItemType Directory -Force -Path $skillRoot | Out-Null
foreach ($name in 'initial', 'startup', 'shutdown') {
    New-Item -ItemType Directory -Force -Path (Join-Path $skillRoot $name) | Out-Null
    Copy-Item -Force (Join-Path $repo "$name\SKILL.md") (Join-Path $skillRoot "$name\SKILL.md")
}
```

### Linux／macOS

```bash
git clone https://github.com/sink6985757-web/cross-device-agent-skills.git
mkdir -p "$HOME/.agents/skills"/{initial,startup,shutdown}
for name in initial startup shutdown; do
  cp "cross-device-agent-skills/$name/SKILL.md" "$HOME/.agents/skills/$name/SKILL.md"
done
```

重新啟動或重新載入 Agent 後，再確認三個目錄都只有 `SKILL.md`。

## Agent／Tool 安裝

自動化工具應執行下列規則：

1. clone 或 `git pull --ff-only` 本 repository，不抓取 fork 當作權威。
2. 比較來源與 `~/.agents/skills` 的版本或 SHA-256；不同時先回報，不靜默覆寫未知修改。
3. 只複製三個 `SKILL.md`，移除舊版 `TEMPLATE.md` 前必須確認它屬於本套件。
4. 回讀安裝結果，確認沒有 `.env`、token、credential、cache 或裝置絕對路徑。
5. Full Core 安裝另依 Core README 檢查 `readygate`，不要把 ReadyGate 複製進本公開 Lite repository。

## 使用

對 Agent 說：

```text
初始化專案
開工
收工
```

- `初始化專案`：第一次建立治理結構與 manifest；依 checkpoint mode 停在確認點或留下 bootstrap SHA，完成後停止。
- `開工`：每次工作開始使用；唯讀 fetch／對照最後遠端 SHA，完成後等待下一個工作選擇。
- `收工`：每次工作結束使用；更新交接並依 checkpoint mode 停在確認點或留下遠端 SHA。`manual` 下單獨說「同步」或「收工」不等於授權 push。

## 更新與驗證

```powershell
git -C .\cross-device-agent-skills pull --ff-only
git -C .\cross-device-agent-skills status --short
git -C .\cross-device-agent-skills diff --check
```

更新 runtime 後，應以 SHA-256 比較三個來源檔與三個安裝檔。若使用 chezmoi，`~/.agents/skills` 是本機執行來源，chezmoi source 是可重建副本；兩者必須同步但責任不可互換。

## GitHub 維護與版本規則

GitHub delivery 的明確 allowlist：

```text
AGENTS.md
README.md
CHANGELOG.md
handoff.md
.gitattributes
.gitignore
initial/SKILL.md
startup/SKILL.md
shutdown/SKILL.md
```

checkpoint 前必須更新 CHANGELOG 與 handoff；只有公開安裝／使用／版本文案改變才更新 README。`manual` 經工作單確認後才可 commit／push；`standing_scoped` 只依 manifest allowlist 執行日常 checkpoint。tag／release 永遠另走 ReadyGate。不得 stage 未知 untracked 檔。

- `v1.x`：歷史 Lite 發行線。
- `v2.0.0`：單檔技能與專案四檔契約；source 已在 GitHub `main`，尚未建立 tag／Release。
- 回滾使用可回讀的 Git commit 或 tag；不以 `git reset --hard` 清除未知工作。
- 已發布錯誤用 `git revert`；查看舊 SHA 用 restore branch。乾淨且只有 behind 時才使用 `pull --ff-only`，diverged 時保存 local／remote refs 並停止；clone 只進空目錄。

歷史變更請見 [`CHANGELOG.md`](CHANGELOG.md)。
