# Hub / Child 模型

## 為什麼不共用一份 state

雲端同步資料夾會在不同電腦上延遲到達；若所有工作者共同覆寫同一個 JSON 或同一個 Git index，最後寫入者可能蓋掉前一台電腦。Source 因此把可變狀態留在各自子專案，主幹只接受不可變、唯一命名的事件。

## 資料流

```text
核准技能 remote ──開工驗證/下載──> 子專案
主幹登錄與既有事件 ──讀取──> 子專案
子專案 session log ──收工摘要──> 主幹 append-only event
子專案 skills/* ──收工提案──> 主幹 review queue
主幹事件 ──hub-sync──> 主幹 Git/GitHub
```

每個事件檔包含 `event_id`、`project_id`、`session_id`、revision、摘要與 Git commit。檔名由 UTC timestamp 加 UUID 組成；engine 不提供覆寫既有事件的動作。

## 競爭規則

1. 一個子專案同時間只有一個 active session。
2. 每個修改命令先取得短期 mutation lock；未過期 lock 存在就停止。
3. active lease 預設 12 小時，崩潰後可在過期時回收；可用 `--lease-hours 1..168` 調整。
4. 主幹不追蹤 `projects/*/`，子專案各自有 `.git/`。
5. 子專案只新增主幹事件，不執行主幹 add/commit/push；由單一 `hub-sync` 收斂。

這是針對同步資料夾的衝突降低機制，不宣稱 Google Drive 提供強一致鎖。若兩台離線電腦同時開啟同一子專案，雲端尚未同步的 lease 無法互相看見；作業規則仍是「先收工、等同步、再換機」。

## 恢復

- `WORKING`：Source 不另開 session，只顯示原 checkpoint。
- mutation lock 過期：下一次修改命令將其移到唯一 stale 名稱後回收。
- active lease 過期但 state 仍 `WORKING`：保留原 session，先檢查 `handoff.md` 與 session log，再由同一專案收工。
- 主幹暫時不可用：不得假裝已發佈；保留子專案 log 並在主幹可用後重試收工/同步。

## 權責

- 子專案擁有自己的程式碼、state、handoff 與 session logs。
- Source engine 擁有 lock、hub descriptors、events 與 proposal metadata。
- 主幹維護者審核技能提案、處理衝突並執行 `hub-sync`。
- 外部帳號、Notion 授權、GitHub remote 建立與 CDN target 屬使用者權限，不寫入 secret。
