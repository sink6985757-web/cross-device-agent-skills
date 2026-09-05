# Handoff

## 已完成

- `WO-DRIVE-GITHUB-ALIGN-20260905-v2` 已確認；v2 source 契約、manual manifest 與同次授權延續規則已交付既有 GitHub default branch。
- 三個 authority source SHA 已以 Git／GitHub API 回讀，固定於 `.agents/project-lifecycle.json`；本文件所在 commit 是後續文件 checkpoint，不建立 tag／Release。
- Core validator 25 files 與 9/9 tests、Lite 三份 Skill validator、ReadyGate Skill／Plugin validator 與 9/9 tests 已通過；manifest 新增後提交前再檢查。
- newday pilot 已通過 Initial 原四檔不變、Startup 五檔 hash／HEAD 不變、manual scoped commit／push／readback。Drive 原 .archive 保留。
- dotfiles active source、Drive mirror、runtime 與 canonical 四技能 hash 已一致；kernel PASS（13 skills），4 個 Claude adapter warning 保留為既有獨立缺件。

## 唯一續跑點

後續專案直接依自己的 manifest 使用 Startup；只有缺件才 Initial，每次 Shutdown 更新 CHANGELOG／handoff。更新 authority revision 時先檢查來源 commit、相容性與授權範圍，不把來源分支名稱當不可變版本。

## 維護邊界

Part 只做路由，各 repository 獨立。manual 不等於常設授權；本次已确认工作單範圍繼續有效。未啟用 standing_scoped，不新建 repository、tag／Release，不變更權限、不搬移／封存。Notion／Obsidian／Knowledge Master 不參與日常生命週期。

更新：2026-09-05，Codex。最新 GitHub SHA 以本次 default branch readback 與 Git 歷史核對；Drive 雲端同步須另回讀。
