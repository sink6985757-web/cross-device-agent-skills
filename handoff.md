# Handoff

## 目前做到哪

Lite `v2.0.0` GitHub `main` 候選版已將 `initial`、`startup`、`shutdown` 收斂為各一個自足 `SKILL.md`，移除三份 `TEMPLATE.md`，並改用專案四檔契約。Notion、Obsidian、Knowledge Master 與其他外部知識庫已從三流程拆出。

## 狀態

- 可執行：`YES`
- Skill validator：三份皆 `VALID`；繁中 Windows 需以 Python UTF-8 模式執行官方 validator。
- 來源同步：公開 checkout、runtime、active chezmoi source、Google Drive dotfiles mirror 的三組 SHA-256 已一致。
- GitHub：`VERIFIED`；治理 commit `924d64310959796c0520521945b8f7a4c2717684` 已推送 `main` 並回讀一致。
- tag／Release：未執行；已發布 tag 基準仍是 `v1.1.1`。

## 下一步

1. 若要正式發布 `v2.0.0`，另走 tag／Release Gate。
2. 新裝置安裝前確認是否採 GitHub `main` 候選或既有 `v1.1.1` tag。
3. 持續維持 runtime、chezmoi source 與 mirror 的 SHA-256 對齊。

## 風險

- GitHub 尚未包含 v2；在 delivery 完成前，不可把 `v2.0.0` 宣稱為已發布。
- chezmoi status 另有與本工單無關的 runtime 差異；不得一起 stage。

## 最近更新

- 時間：2026-08-09 Asia/Taipei
- Agent：Codex
- 成果 revision：未提交工作樹
