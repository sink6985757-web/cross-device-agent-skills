# Cross-Device Agent Skills

跨裝置專案生命週期的公開 Lite 套件，只包含三個自足技能：`initial`、`startup`、`shutdown`。適合 Codex、Claude、Gemini、Hermes 或其他能讀取 Markdown 技能的 Agent。

目前 GitHub 發行版：`v1.1.1`
開發中版本：`v2.0.0`（尚未 commit／push／tag）

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

| 技能 | 用途 | 寫入行為 |
|---|---|---|
| `initial` | 初始化新專案或補齊既有專案缺件 | 只建立缺少的四檔，不覆寫既有內容 |
| `startup` | 開工與續跑 | 唯讀規則、handoff 與 Git 狀態 |
| `shutdown` | 收工、版本紀錄與交接 | 更新 `CHANGELOG.md`、`handoff.md`；外部動作另行放行 |

## 權威與相依關係

| 層級 | Canonical | 責任 |
|---|---|---|
| Lite 公開發行 | 本 repository | `initial`／`startup`／`shutdown` 的安裝與版本權威 |
| Runtime 安裝 | `~/.agents/skills/<skill>/SKILL.md` | Agent 實際讀取的執行副本，不是發行權威 |
| Full Core | [`cross-device-agent-workflow-core`](https://github.com/sink6985757-web/cross-device-agent-workflow-core) | 首次部署、完整治理、相容性驗證與 Core profile |
| ReadyGate | [`readygate-skill-chatgpt-app`](https://github.com/sink6985757-web/readygate-skill-chatgpt-app) | commit、push、發布、搬移、封存、權限與其他高風險動作的工作單／閘門 |
| 專案狀態 | 各專案 repository | 專案自己的四檔與 Git 歷史才是該專案權威 |

Core profile 使用四個技能：Lite 三技能加 `readygate`。Lite profile 本身不強制安裝 ReadyGate，但單獨口令「收工」不授權任何外部 Git、發布、搬移或封存動作。

Notion、Obsidian、Knowledge Master 與其他外部知識庫皆為 `ON_DEMAND_ONLY`，不屬於 initial／startup／shutdown 流程。

## 專案四檔契約

| 檔案 | 唯一責任 | 更新時機 |
|---|---|---|
| `AGENTS.md` | 穩定規則、權威來源、邊界與相依路徑 | 規則或架構真的改變時 |
| `README.md` | GitHub 人類安裝、Agent／Tool 安裝、使用、公開版本與最新變更文案 | 每次授權 GitHub delivery 前 |
| `CHANGELOG.md` | 近期修改、驗證結果、版本與 delivery 狀態 | 每次收工 |
| `handoff.md` | 現況、未完成事項、風險與唯一續跑點 | 每次收工，以目前狀態更新 |

`CHANGELOG.md` 是專案內獨立、可版本控制的 Markdown 變更紀錄；不需要 Obsidian 或專門的 RCD 資料夾。

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

- `初始化專案`：偵測環境、確認 Git 根目錄，並只補齊缺少的四檔。
- `開工`：唯讀 `AGENTS.md`、`handoff.md` 與 Git 狀態，回報可續跑點。
- `收工`：更新 `CHANGELOG.md` 與 `handoff.md`；若本次已授權 GitHub delivery，再更新 README 公開文案並通過 Delivery Gate。

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

delivery 前必須更新 README 的安裝／使用／版本／最新變更文案及 CHANGELOG，並經工作單或 ReadyGate 確認後才可 commit、push、tag 或 release。不得 stage 未知 untracked 檔。

- `v1.x`：歷史 Lite 發行線。
- `v2.0.0`：單檔技能與專案四檔契約；目前仍是本機開發狀態。
- 回滾使用可回讀的 Git commit 或 tag；不以 `git reset --hard` 清除未知工作。

歷史變更請見 [`CHANGELOG.md`](CHANGELOG.md)。
