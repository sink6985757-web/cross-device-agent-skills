# Agent entry — PROTECTED

> 使用者只需說「初始化專案」「開工」「收工」；所有生命週期邏輯都交給 Source。

1. 先執行 Source `next`：Windows 使用 `./source.ps1`，Linux／macOS 使用 `./source.sh`。
2. 不直接修改本檔、`SOURCE.md` 或 `.source/config.json`；正式變更走 authority gate。
3. `.source/state.json` 與 `handoff.md` 是 GENERATED，只能由 engine 寫入。
4. 不保存 secret、credential 或裝置絕對路徑；結束時執行 Source `finish`。
5. 子專案不得操作主幹 Git index；hub event 與 skill proposal 只新增、不覆寫。
6. 簡短續跑資訊留在 checkpoint；決策原因、踩坑與時間線寫入 config 登記的 Obsidian 筆記。
