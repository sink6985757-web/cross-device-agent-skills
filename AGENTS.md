# Repository guidance

本 repository 只維護三個 Skill：`initial`、`startup`、`shutdown`。

## 三技能不可混用邊界

| Skill | 唯一定位 | 完成後路由 |
|---|---|---|
| `initial` | 第一次建立治理結構、修復缺件或部署技能；同時建立／驗證 portable manifest 與初始化 checkpoint | `manual` 停在確認點；`standing_scoped` 可在限制內 push bootstrap，之後停止 |
| `startup` | 每次工作階段唯讀對照本機與最後 GitHub checkpoint；不建立空 commit、不執行工作 | 輸出開工報告後停止，等待使用者選擇工作 |
| `shutdown` | 每次結束更新版本紀錄與交接，依 manifest 決定停在確認點或建立 scoped GitHub checkpoint | 遠端 SHA 回讀後完成；超出 standing scope 另走 ReadyGate |

ReadyGate 是外部橫向閘門，不是本 repository 的第四個日常階段；只有高風險、不可逆或外部交付工作才按需使用。

1. 每個 Skill 目錄只能包含一個自足的 `SKILL.md`；規則、相依與固定輸出不得拆成第二份模板。
2. 初始化產生或保留的專案共用檔固定為 `AGENTS.md`、`README.md`、`CHANGELOG.md` 與 `handoff.md`。
3. `README.md` 是 GitHub 人類／Agent 安裝與公開版本文案；`CHANGELOG.md` 是每次收工版本紀錄；`handoff.md` 只保存目前交接。
4. 不加入 session database、Notion／Obsidian connector 或裝置絕對路徑；共同 schema／validator 由 Full Core 維護，本 Lite repository 只保留操作契約。
5. GitHub repository 為公開安裝來源；不得提交 secret、credential、cache、個人路徑或未知 untracked 檔。
6. 架構、安裝、使用、GitHub 維護與版本規則以 `README.md` 為準；歷史變更以 `CHANGELOG.md` 為準。
7. 初始化、開工與收工回報都要記錄 Agent 名稱與 runtime 取得的本機電腦名稱；不得拿電腦名稱代替 Git／同步驗證。
8. `Part` 只做分類／路由，不等於 Git 邊界；每個實際 Project 都以 `git rev-parse --show-toplevel` 驗證，並部署自己的 `.agents/project-lifecycle.json`。
9. checkpoint 預設 `manual`。只有先前受治理 manifest 已設為 `standing_scoped`，且 remote identity、目前工作 branch、allowlist、secret、unknown untracked、ahead／behind／diverged 全部符合，Initial／Shutdown 才可執行非 force push 與遠端回讀。
10. 建立 repository、force push、auto merge／rebase、tag／release、PR merge、刪除／封存與權限變更永遠不在 standing scope，須由確認工作單或 ReadyGate 放行。
