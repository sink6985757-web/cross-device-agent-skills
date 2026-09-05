# Changelog

## [Unreleased] - 2026-09-05

- `WO-DRIVE-GITHUB-ALIGN-20260905-v2`：完成initial／startup／shutdown 的 manifest、remote checkpoint 與授權延續契約；保留既有功能與治理差異。
- 已確認工作單持續授權其列出的動作，manual 不重複索取相同授權。
- 驗證：initial／startup／shutdown 三份 Skill validator PASS。 提交前重跑 validator 與 diff whitespace 檢查。
- Delivery：本輪 source checkpoint；不建立新 tag／Release。

## [Unreleased 2.0.0] - 2026-08-13

### Changed
- 將 `initial`、`startup`、`shutdown` 各收斂為單一自足 `SKILL.md`。
- 專案生命週期改為 `AGENTS.md`、`README.md`、`CHANGELOG.md`、`handoff.md` 四檔契約。
- `shutdown` 每次更新 CHANGELOG 與 handoff；GitHub delivery 前更新 README，外部動作交由工作單／ReadyGate。
- 移除 Notion、Obsidian 與其他外部知識庫的自動讀寫。
- 明確定義三技能的進入條件、允許寫入、完成標準、硬停止點與下一流程：`initial` 只做第一次治理／缺件修復／技能部署，`startup` 永遠唯讀並在報告後停止，`shutdown` 預設只做本機交接。
- 說明 ReadyGate 是按風險插入的橫向閘門，不是 Lite 的第四個日常階段；單獨口令「收工」或「同步」不授權 push。
- v2 工作單將 Part 明定為分類／路由、Project repository 明定為 Git 邊界，並新增 `.agents/project-lifecycle.json`、`manual`／`standing_scoped` checkpoint 契約。
- Initial 現在驗證或建立 bootstrap checkpoint；Startup fetch 並對照遠端 SHA、不建立空 commit；Shutdown 在 standing scope 安全限制通過時才可建立 scoped commit、非 force push 與 remote readback。
- 明列 wrong remote、dirty、ahead、behind、diverged、restore branch、`git revert`、`pull --ff-only` 與 empty-directory clone 的衝突／回滾規則。

### Validation
- 三個 Skill 已通過官方 quick validator；繁中 Windows 需使用 Python UTF-8 模式。
- 公開 checkout、runtime、active chezmoi source 與 Google Drive mirror 的三組 SHA-256 已一致。
- 每個 Skill 目錄都只包含一個 `SKILL.md`。
- 2026-08-13 重新執行三份官方 quick validator，全部 `PASS`；`git diff --check` 通過。
- canonical source 與目前裝置 runtime 的三份 `SKILL.md` 已逐一以 SHA-256 回讀一致；chezmoi source／dotfiles mirror 本輪未修改、未重新驗證。
- v2 重新執行三份 quick validator，全部 `PASS`；source／runtime SHA-256 分別為 initial `C29A4E3B...D5F55`、startup `6547360A...B932A5`、shutdown `AEFE9A67...CC9D6` 且逐一一致。
- Full Core manifest 正反例與六種 Git 狀態情境測試通過；本 Lite repository 的 `git diff --check` 通過。

### Delivery
- 本輪生命週期邊界更新：`LOCAL_ONLY／PENDING_GATE`，未 commit、未 push。
- v2 GitHub checkpoint／Part routing 更新：`LOCAL_ONLY／PENDING_GATE`；權威與 runtime 已更新，尚未部署任何 Project manifest，未 stage、未 commit、未 push。
- 基底 GitHub：本機 `HEAD` 與 `origin/main`／`ls-remote` 均為 `383f50275c68bbb54deeaec7d3ffc13384360528`。
- tag／Release：未執行。

## [1.1.1] - 2026-07-26

### Changed
- 發布 Three-Skill Lite v1.1.1 可攜安裝基準。

### Delivery
- GitHub：tag `v1.1.1`
