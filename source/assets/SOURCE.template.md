# SOURCE

這是本專案唯一操作入口。

```powershell
./source.ps1                         # 自動初始化、開工或中斷續接
./source.ps1 -Action next            # 顯示做到哪與唯一下一步
./source.ps1 -Action finish          # 收工與同步
./source.ps1 -Action doctor          # 權限與完整性檢查
```

狀態以 `.source/state.json` 為準；給人看的摘要在 `handoff.md`。不要手工修改 state，讓 `source.ps1` 寫入 checkpoint。
