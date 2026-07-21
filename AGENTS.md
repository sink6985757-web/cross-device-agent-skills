# Agent entry

本專案的唯一入口是 `SOURCE.md`。

1. 先執行 `./source.ps1 -Action next` 取得狀態與唯一下一步。
2. 修改前讀最新檔案，只處理任務範圍。
3. 不手工修改 `.source/state.json`，不提交 secret 或 credentials。
4. 結束時執行 `./source.ps1 -Action finish`；外部 connector 依 checkpoint 完成。
