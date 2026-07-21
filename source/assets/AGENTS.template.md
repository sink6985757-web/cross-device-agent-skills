# Agent entry

1. 先讀 `SOURCE.md`。
2. 執行 `./source.ps1 -Action next`，依唯一下一步續接。
3. 修改前讀最新檔案；只處理任務範圍。
4. 結束時執行 `./source.ps1 -Action finish`。
5. 不手工修改 `.source/state.json`，不提交 secret 或 credentials。
