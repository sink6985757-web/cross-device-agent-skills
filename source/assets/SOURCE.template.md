# SOURCE — PROTECTED

本檔是專案唯一入口，不能直接修改；正式變更必須使用 Source authority gate。

```text
Windows       ./source.ps1
Linux/macOS   ./source.sh
```

- `next`：目前狀態與唯一下一步。
- `doctor`：工具、權限、相對路徑、signature、hash、唯讀檢查。
- `finish`：保存 checkpoint、Git 與 connector 狀態。
- `hub-init`／`child-create`：建立主幹與隔離子專案；主幹事件只新增不覆寫。
- `authority-unlock --yes` → 核准修改 → `authority-seal --yes`：唯一權威修改流程。

不可手改 `.source/state.json` 或 `handoff.md`。canonical JSON 只保存 root-relative 路徑；OS 絕對路徑只允許 runtime 解析。同一子專案一次只允許一個 active session。
