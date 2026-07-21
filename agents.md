# 跨電腦專案管理三技能（專案藍圖）

> 本檔為跨 Agent 通用的專案藍圖（AGENTS.md 開放標準）。任何 Agent 的每個 session 都應先讀本檔＋`handoff.md`。

## 專案簡介

本專案提供 `project-init`、`startup`、`shutdown` 三個技能，目標是讓同一個專案能在不同電腦與 AI Agent 之間透過精簡藍圖、交接檔、GitHub 備份及 Obsidian 詳細筆記無縫接續。

## 關鍵時程

## 目標與路線圖

- [x] 建立初始化、開工與收工三個技能及必要範本
- [x] 建立本地專案藍圖與交接機制
- [x] 建立 Obsidian 專案工作流程筆記
- [x] 完成 GitHub 私有 repository 與初始推送
- [ ] 在不同電腦與 Agent 上進行實際接續驗證

## 資料夾結構

```text
cross-device-agent-skills-master/
├─ README.md                     # 專案說明與安裝方式
├─ agents.md                     # 跨 Agent 專案藍圖
├─ handoff.md                    # 每次開工／收工使用的交接檔
├─ .gitignore                    # GDrive 與敏感檔案排除規則
├─ project-init/
│  ├─ SKILL.md                   # 專案初始化技能
│  └─ templates/                 # agents.md、handoff.md 範本
├─ startup/
│  └─ SKILL.md                   # 開工技能
└─ shutdown/
   └─ SKILL.md                   # 收工技能
```

## 同步層級（本專案初始化至第 3 層級）

| 層級 | 平台 | 位置 | 讀取時機 |
|------|------|------|---------|
| L1 | 本地（GDrive） | `agents.md`＋`handoff.md` | 每個 session |
| L2 | GitHub | `sink6985757-web/cross-device-agent-skills`（private） | 指定時 |
| L3 | Obsidian | `cross-device-agent-skills-master/專案工作流程.md` | 有需要時 |

## 工作約定

- 任何 Agent、任何電腦：**開工先讀 `handoff.md`，收工必更新 `handoff.md`**
- 修改共用檔案前先讀最新內容，避免覆蓋其他 Agent 的變更
- 所有回應與文件使用繁體中文
- 修改前先確認計畫，優先保留原有資料結構
