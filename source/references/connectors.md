# Connector checkpoint

只在 `.source/state.json` 顯示 `PENDING_AGENT` 時讀取本檔。

## Notion

1. 重新讀取 config 登記的 Knowledge Master 與正式主題 Prompt；Prompt 只讀。
2. 依 Asia/Taipei 週次搜尋同主題唯一頁；有就最小更新，沒有才建立。
3. 不寫入 secret、token、裝置絕對路徑或未公開內容。
4. 回讀頁面與父頁，確認 Page ID、父頁與唯一性，再將 connector 標為 `VERIFIED`／`PARTIAL`／`BLOCKED`。

## Obsidian

使用 config 的 vault-relative note；先讀後做最小更新。工具或 vault 不可用時標示 `BLOCKED`，不要猜路徑。

## CDN

只有 config 的 `cdn.enabled=true` 且 provider、target、驗證方式齊全時才部署。缺一項就是 `NOT_CONFIGURED`，不影響本地、GitHub、Notion 或技能同步。部署後必須回讀正式 URL／版本並記錄 rollback 識別。

## 完成 checkpoint

```powershell
./source.ps1 -Action complete -Connector notion -ConnectorStatus VERIFIED -ExternalId "page-id"
./source.ps1 -Action complete -Connector obsidian -ConnectorStatus VERIFIED
./source.ps1 -Action complete -Connector cdn -ConnectorStatus BLOCKED -Note "缺少部署 target"
```
