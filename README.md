# Source project pipeline

跨電腦、跨 Agent 的單一入口專案生命週期。

```powershell
./source.ps1
```

完整入口、安裝與安全邊界請讀 [SOURCE.md](SOURCE.md)。

## 四個口令，一個狀態機

| 口令 | 功能 |
|---|---|
| `source` | 自動初始化、開工或從 checkpoint 續接 |
| `初始化` | 建立最小專案核心與私有 Git 準備 |
| `開工` | 讀取狀態、遠端差異與唯一下一步 |
| `收工` | 保存交接、push、部署 Skill，等待外部 connector |

三個舊 Skill 已縮成相容轉接；正式邏輯只在 `source/scripts/source.ps1`。

## 結構

```text
SOURCE.md                 單一人類／Agent 入口
source.ps1                單一命令入口
.source/                  可恢復 config 與 state
source/                   正式 Skill、腳本、connector 規則、模板
project-init|startup|shutdown/
                          舊口令的薄轉接
tests/                    拋棄式端到端驗證
```

GitHub repo 維持 private。Notion Prompt 只讀；CDN 未配置 provider／target 前不部署。
