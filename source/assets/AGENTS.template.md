# Agent entry — PROTECTED

1. 先執行 Source `next`：Windows 使用 `./source.ps1`，Linux／macOS 使用 `./source.sh`。
2. 不直接修改本檔、`SOURCE.md` 或 `.source/config.json`；正式變更走 authority gate。
3. `.source/state.json` 與 `handoff.md` 是 GENERATED，只能由 engine 寫入。
4. 不保存 secret、credential 或裝置絕對路徑；結束時執行 Source `finish`。
