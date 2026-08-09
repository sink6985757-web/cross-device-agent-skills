# Changelog

## [Unreleased 2.0.0] - 2026-08-09

### Changed
- 將 `initial`、`startup`、`shutdown` 各收斂為單一自足 `SKILL.md`。
- 專案生命週期改為 `AGENTS.md`、`README.md`、`CHANGELOG.md`、`handoff.md` 四檔契約。
- `shutdown` 每次更新 CHANGELOG 與 handoff；GitHub delivery 前更新 README，外部動作交由工作單／ReadyGate。
- 移除 Notion、Obsidian 與其他外部知識庫的自動讀寫。

### Validation
- 三個 Skill 已通過官方 quick validator；繁中 Windows 需使用 Python UTF-8 模式。
- 公開 checkout、runtime、active chezmoi source 與 Google Drive mirror 的三組 SHA-256 已一致。
- 每個 Skill 目錄都只包含一個 `SKILL.md`。

### Delivery
- GitHub：`LOCAL_ONLY`

## [1.1.1] - 2026-07-26

### Changed
- 發布 Three-Skill Lite v1.1.1 可攜安裝基準。

### Delivery
- GitHub：tag `v1.1.1`
