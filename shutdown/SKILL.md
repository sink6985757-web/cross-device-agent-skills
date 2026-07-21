---
name: shutdown
description: 專案收工、交接與同步。當使用者說收工、shutdown、結束、同步、下班或換電腦時使用；依固定模板更新 handoff.md、必要的 AGENTS.md、private GitHub 與 Obsidian。
---

# Shutdown

固定使用同目錄 `TEMPLATE.md`；「收工／同步」即授權執行可回復的專案內保存與既有 private remote push。

## 流程

1. 讀取 `AGENTS.md`、`handoff.md` 與本次對話，盤點實際完成、未完成、測試、風險與下一步；不得補造結果。
2. 只有路線圖或穩定規則改變時才更新 `AGENTS.md`；使用 `TEMPLATE.md` 重寫精簡 `handoff.md`。
3. 若有 Git：
   - 先看 `git status --short` 與 diff。
   - 只 stage 本次已知檔案；未知 untracked、secret 或 credential 一律停止。
   - 使用具體繁體中文 commit 訊息，推送既有 private remote。
   - 沒有 remote 或認證時標示 `PARTIAL`，保留本地 commit 或精確續跑點。
4. 若 `AGENTS.md` 登記 Obsidian，更新既有專案筆記的「上次做到哪、決策／踩坑、最近更動」並回讀；找不到不得猜路徑。
5. Git push 後再把實際結果回填 `handoff.md`；若因此產生第二個 commit，必須一併 push。
6. 最後依 `TEMPLATE.md` 回報每一層狀態與唯一續跑點。

## 不做

- 不建立 public repository。
- 不提交未知檔案或敏感資訊。
- 不把長篇歷史塞進 `handoff.md`。
- 不假報 GitHub、Obsidian 或同步成功。
