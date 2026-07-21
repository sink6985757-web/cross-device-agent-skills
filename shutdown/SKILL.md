---
name: shutdown
description: Source pipeline 的收工相容入口。當使用者說收工、結束、下班、同步、換電腦或保存進度時使用；把交接、GitHub、技能部署、chezmoi 與外部 connector checkpoint 交給 source。
---

# Shutdown

1. 讀取 `../source/SKILL.md`。
2. 檢查變更與 commit 訊息後執行 `./source.ps1 -Action finish -CommitMessage <具體成果>`。
3. 若輸出 `PENDING_AGENT`，只讀 `../source/references/connectors.md` 並完成指定 connector。
4. 每完成一個 connector 就用 `source.ps1 -Action complete` 回填；不得假裝成功。
