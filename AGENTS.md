# Agent entry — PROTECTED

本檔是跨 Agent 權威指標，不能直接修改；正式變更必須走 Source `authority-unlock → authority-seal`。

1. Windows 執行 `./source.ps1 -Action next`；Linux／macOS 執行 `./source.sh next`。
2. 只依 `SOURCE.md`、`.source/config.json`、`.source/state.json` 與 authority gate 判定下一步。
3. `.source/state.json`、`handoff.md` 是 GENERATED，永遠不得手改。
4. 結束時執行 Source `finish`；外部 connector 必須回讀後才能標示 `VERIFIED`。
5. 不提交 secret、credential、裝置絕對路徑或未知 untracked 檔。
