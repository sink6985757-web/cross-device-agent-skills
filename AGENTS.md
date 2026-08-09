# Repository guidance

本 repository 只維護三個 Skill：`initial`、`startup`、`shutdown`。

1. 每個 Skill 目錄只能包含一個自足的 `SKILL.md`；規則、相依與固定輸出不得拆成第二份模板。
2. 初始化產生或保留的專案共用檔固定為 `AGENTS.md`、`README.md`、`CHANGELOG.md` 與 `handoff.md`。
3. `README.md` 是 GitHub 人類／Agent 安裝與公開版本文案；`CHANGELOG.md` 是每次收工版本紀錄；`handoff.md` 只保存目前交接。
4. 不加入狀態機、runtime engine、session database、Notion／Obsidian connector 或裝置絕對路徑。
5. GitHub repository 為公開安裝來源；不得提交 secret、credential、cache、個人路徑或未知 untracked 檔。
6. 架構、安裝、使用、GitHub 維護與版本規則以 `README.md` 為準；歷史變更以 `CHANGELOG.md` 為準。
7. 初始化、開工與收工回報都要記錄 Agent 名稱與 runtime 取得的本機電腦名稱；不得拿電腦名稱代替 Git／同步驗證。
8. GitHub delivery、搬移、封存、發布與權限變更必須由確認工作單或 ReadyGate 放行；單獨口令「收工」不構成外部授權。
