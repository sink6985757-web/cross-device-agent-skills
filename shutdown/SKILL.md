---
name: shutdown
description: Source pipeline 的收工相容入口。當使用者說收工、結束、下班、同步、換電腦或保存進度時使用；把交接、GitHub、技能部署、chezmoi 與外部 connector checkpoint 交給 source。
---

# Shutdown

1. 讀取 `../source/SKILL.md`。
2. 檢查 authority gate、變更與 commit 訊息後，以目前 OS 的 Source adapter 執行 `finish`；子專案會保存 session log、送回 append-only 主幹事件，未知技能只成為待審提案。
3. 若輸出 `PENDING_AGENT`，只讀 `../source/references/connectors.md` 並完成指定 connector。
4. 每完成一個 connector 就用 Source `complete` 回填；不得假裝成功。
5. 主幹管理者最後執行 `hub-status` 與 `hub-sync`；子專案不得直接提交主幹 Git index。
