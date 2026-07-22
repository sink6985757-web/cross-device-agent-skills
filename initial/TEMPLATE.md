# Initial 固定模板

## A. 本機部署 checklist

```markdown
# 初始化報告

- 專案：<名稱>
- 狀態：<VERIFIED｜PARTIAL｜BLOCKED>
- Agent：<本次 Agent 名稱>
- 電腦：<本機電腦名稱>

## 本機環境
- [ ] OS 已辨識
- [ ] 本機電腦名稱已辨識
- [ ] Git 可用
- [ ] GitHub CLI 已登入／不使用
- [ ] `~/.agents/skills/initial` 已部署
- [ ] `~/.agents/skills/startup` 已部署
- [ ] `~/.agents/skills/shutdown` 已部署
- [ ] Agent adapter 已連到共用技能目錄／不需要

## 專案檔案
- [ ] `AGENTS.md` 已建立或保留
- [ ] `handoff.md` 已建立或保留
- [ ] Git `main` 已建立／沿用
- [ ] private remote 已建立／沿用／未授權
- [ ] Obsidian 已建立／沿用／NOT_CONFIGURED

## 尚待處理
1. <最多三項；沒有就寫「無」>
```

## B. 產生 `AGENTS.md`

```markdown
# <專案名稱>

## 目標
<一句話；未知就標示待確認>

## 路線圖
- [ ] <階段一>
- [ ] <階段二>

## 專案結構
- `<相對路徑>`：<用途>

## 共用規則
1. 每個 Agent 開工先讀本檔與 `handoff.md`。
2. 保留既有修改；不提交 secret、credential 或未知檔案。
3. 所有 canonical 路徑使用專案相對路徑。
4. 開工只讀；收工才更新交接、GitHub 與 Obsidian。

## 整合
- GitHub：<private remote｜NOT_CONFIGURED>
- Obsidian：<vault-relative path｜NOT_CONFIGURED>
```

## C. 產生 `handoff.md`

```markdown
# Handoff

## 目前做到哪
專案初始化完成。

## 目前狀態
- 可執行：<是／否／待確認>
- Git：<狀態>
- Obsidian：<狀態>

## 下一步
1. <最小可執行步驟>

## 注意事項
- <沒有就寫「無」>

## 最近更新
- 時間：<YYYY-MM-DD HH:mm，含時區>
- 更新者：<Agent 名稱>
- 電腦：<本機電腦名稱>
- Git push：<已推／未推／NOT_CONFIGURED>
```
