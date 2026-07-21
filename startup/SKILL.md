---
name: startup
description: Source pipeline 的開工與續接相容入口。當使用者說開工、開始工作、繼續、下一步、工作到哪或換電腦接續時使用；把狀態判定交給 source，不重複載入完整 SOP。
---

# Startup

1. 讀取 `../source/SKILL.md`。
2. 以目前 OS 的 Source adapter 執行 `start`；中途中斷或只查狀態時執行 `next`。
3. 不主動 pull；依輸出的 checkpoint 與唯一下一步續接。
