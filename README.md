# 跨裝置 Agent 三技能

> 架構版本：**Three-Skill Lite v1.1.0**（2026-07-22）

這個 repository 只做三件事：初始化、開工、收工。每個技能只有 `SKILL.md` 與一份固定 `TEMPLATE.md`；每個專案只產生 `AGENTS.md` 與 `handoff.md` 兩個共用檔案。

## 架構

```text
cross-device-agent-skills/
├─ initial/
│  ├─ SKILL.md
│  └─ TEMPLATE.md
├─ startup/
│  ├─ SKILL.md
│  └─ TEMPLATE.md
├─ shutdown/
│  ├─ SKILL.md
│  └─ TEMPLATE.md
├─ AGENTS.md
├─ README.md
├─ .gitattributes
└─ .gitignore
```

| 口令 | 技能 | 作用 |
|---|---|---|
| 初始化專案 | `initial` | 偵測本機工具、部署三技能、建立 `AGENTS.md` 與 `handoff.md` |
| 開工 | `startup` | 只讀兩個專案檔與 Git 狀態，用固定模板回報 |
| 收工 | `shutdown` | 更新交接、GitHub 與 Obsidian，用固定模板回報 |

`AGENTS.md` 是所有 Agent 的共同專案說明；`handoff.md` 只保存最近一次交接，以及執行該次交接的 Agent 與本機電腦名稱。詳細決策與踩坑放 Obsidian，不塞進交接檔。

## 安裝

Repository 預設為 private，先登入 GitHub：

```powershell
gh auth login
gh repo clone sink6985757-web/cross-device-agent-skills
```

### Windows PowerShell

```powershell
$repo = Resolve-Path .\cross-device-agent-skills
$skills = Join-Path $HOME '.agents\skills'
New-Item -ItemType Directory -Force -Path $skills | Out-Null
Copy-Item -Recurse -Force "$repo\initial"  $skills
Copy-Item -Recurse -Force "$repo\startup"  $skills
Copy-Item -Recurse -Force "$repo\shutdown" $skills
```

### Linux／macOS

```bash
gh auth login
gh repo clone sink6985757-web/cross-device-agent-skills
mkdir -p "$HOME/.agents/skills"
cp -R cross-device-agent-skills/{initial,startup,shutdown} "$HOME/.agents/skills/"
```

`~/.agents/skills` 是唯一正式 Skill 來源。Codex、Gemini、Claude、Hermes 或其他 Agent 若不能原生讀取這個位置，只建立 symlink／junction 或設定外部技能目錄，不再複製第二份內容。

## 使用

### 1. 初始化專案

在專案資料夾對 Agent 說：

```text
初始化專案
```

`initial` 會依 `initial/TEMPLATE.md` 檢查：

- 這台機器的 OS、Git、GitHub CLI 與登入狀態。
- 本次執行的 Agent 名稱與本機電腦名稱。
- 三技能是否已部署到共用技能目錄。
- 專案是否已有 Git、remote、`AGENTS.md`、`handoff.md`。
- 是否能定位 Obsidian vault。
- 哪些可自動完成、哪些需要使用者登入或確認。

初始化不覆寫既有檔案；GitHub repository 預設 private。

### 2. 開工

```text
開工
```

`startup` 只讀 `AGENTS.md`、`handoff.md` 與 Git 狀態，不修改檔案、不自動 pull；回報同時顯示本次與上次使用的 Agent、電腦名稱。輸出固定使用 `startup/TEMPLATE.md`。

### 3. 收工

```text
收工
```

`shutdown` 把本次 Agent 與本機電腦名稱寫入 `handoff.md`，必要時更新 `AGENTS.md` 路線圖；確認變更安全後 commit／push，並更新 `AGENTS.md` 登記的 Obsidian 筆記。輸出固定使用 `shutdown/TEMPLATE.md`。

## 每個專案只需要的兩個檔案

### `AGENTS.md`

保存穩定資訊：專案目標、目錄、工作規則、GitHub、Obsidian 相對路徑與路線圖。所有 Agent 每次先讀本檔。

### `handoff.md`

保存變動資訊：目前做到哪、狀態、下一步、注意事項、最近一次 Git push，以及最後更新的 Agent 與電腦名稱。開工只讀，收工重寫，不累積長篇日誌。

## GitHub 維護

維護本技能 repository 時只提交以下 allowlist：

```text
AGENTS.md
README.md
.gitattributes
.gitignore
initial/
startup/
shutdown/
```

標準流程：

```bash
git status --short
git diff --check
git add AGENTS.md README.md .gitattributes .gitignore initial startup shutdown
git commit -m "更新三技能架構：<摘要>"
git push origin main
gh repo view sink6985757-web/cross-device-agent-skills
```

不要提交 `.env`、token、key、credential、Agent cache 或未知 untracked 檔。發布新架構版本時更新本 README 的版本號，再建立 annotated tag：

```bash
git tag -a v1.1.0 -m "Three-Skill Lite v1.1.0"
git push origin v1.1.0
```

## 版本與回滾

- `v1.x`：三技能 Lite 架構內的相容更新。
- `v2.0.0`：輸出檔名或模板契約有破壞性變更。
- 舊 Source 平台完整保留在 Git commit `52b9857`，未重寫歷史。
- 若要回復舊版，建立一般 revert／restore commit；不要使用 `git reset --hard`。

概念參考：[mathruffian-dot/cross-device-agent-skills](https://github.com/mathruffian-dot/cross-device-agent-skills)。本版本依個人跨 Agent 工作方式重新編寫。
