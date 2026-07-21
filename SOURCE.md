# SOURCE — 唯一入口（PROTECTED）

不論新電腦、換作業系統、中途中斷或一般工作，都只從這裡開始：

```text
Windows       ./source.ps1
Linux/macOS   ./source.sh
```

無參數會自動判斷：未初始化就建立、`READY` 就開工、工作中或等待外部服務就顯示唯一下一步。不得手改 `.source/state.json`、`handoff.md` 或權威檔。

## 全新環境

先 clone 私有技能發行庫，再於預定主幹目錄執行：

```powershell
# Windows
./source.ps1 -Action hub-init -ProjectName "我的工作主幹"
./source.ps1 -Action child-create -ChildName "第一個專案"
```

```bash
# Linux / macOS
./source.sh hub-init --project-name "我的工作主幹"
./source.sh child-create --child-name "第一個專案"
```

進入 `projects/第一個專案的-slug/` 後，日常只需要：

```text
Source          自動開工或顯示下一步
Source finish   收工、記錄、Git、技能提案與主幹事件
```

主幹管理者查看及收取全部子專案事件：

```text
Source hub-status
Source hub-sync --yes
```

## 固定架構

```text
主幹/
├─ .source/hub/projects/          子專案登錄；每個 project 一檔
├─ .source/hub/events/            UUID 事件；只新增、不覆寫
├─ .source/hub/skill-proposals/   子專案收工送回；必須人工審核
└─ projects/*/                    各自獨立 Git、state、log、lease
```

- 子專案各自寫 `logs/sessions/<session-id>.json`，收工後再新增一個主幹事件。
- 主幹 Git 不追蹤 `projects/*/`；子專案不能操作主幹 Git index。只有 `hub-sync` 提交主幹事件，因此不會互搶同一個 index。
- `.source/coordination/` 由 engine 管理且不進 Git；active lease 表示專案尚未收工，mutation lock 阻擋同一專案同時改寫。
- Google Drive／Dropbox 類同步服務不是分散式資料庫；同一子專案仍應一次只由一台電腦工作，換機前先收工並等同步完成。需要最強隔離時，各電腦使用獨立 Git clone。

## 技能更新

- 開工只檢查 `.source/config.json` 指定的已核准 private Git remote；authority hash 驗證通過才自動備份並更新 managed skills。
- 未核准、ChatGPT 建議或子專案新技能不會自動安裝；收工只送入 `skill-proposals/`，審核後才可提升為正式技能。
- `skills-check` 只檢查，`skills-update` 執行已核准來源更新。沒有通用且可信的「全網最新技能資料庫」，因此不得靜默安裝任意來源。

## 空白 Connector

- Obsidian：初始化時建立專案內 `knowledge/obsidian/Project Log.md`，全程相對路徑。
- Notion：建立 `NEEDS_SETUP` checkpoint；必須先由使用者授權 connector，再建立或選擇頁面並 `complete`。Prompt 永遠只讀。
- Google Drive：只偵測 runtime mount；Source 不保存 mount 絕對路徑，也不能代替使用者登入或安裝同步客戶端。
- CDN：provider 與 target 未明確設定時維持 `NOT_CONFIGURED`，絕不猜測部署。

## 權威與路徑

| 類別 | 寫入規則 |
|---|---|
| `PROTECTED` | 只能 `authority-unlock --yes` → 核准修改 → `authority-seal --yes` |
| `GENERATED` | 只能由 Source engine 寫入 |
| `PROJECT_WORK` | 專案 Agent 依任務修改 |
| `EXTERNAL_READ_ONLY` | 永不修改，例如 Notion Prompt |

canonical JSON 只保存專案相對路徑、URL 與外部 ID；Windows drive、UNC、`/home/...`、`/Users/...` 只允許 runtime 使用。每次交接前執行 `doctor`，任何 authority、hash、路徑或事件唯一性錯誤都會標示 `BLOCKED`。

詳細平台安裝見 [platforms.md](source/references/platforms.md)，主幹與競爭模型見 [hub.md](source/references/hub.md)，Notion 空白建置見 [notion-bootstrap.md](source/references/notion-bootstrap.md)。
