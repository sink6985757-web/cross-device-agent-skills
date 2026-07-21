# Source project pipeline

Windows、Linux、macOS 共用一套 Python 標準庫狀態機；PowerShell 與 POSIX shell 只是薄 adapter。

```text
Windows       ./source.ps1
Linux/macOS   ./source.sh
```

完整安裝、路徑政策、不可修改檔案與正式變更閘門請讀 [SOURCE.md](SOURCE.md)。

## 核心結構

```text
SOURCE.md                         唯一人類／Agent 入口（PROTECTED）
source.ps1 | source.sh            OS adapter（PROTECTED）
source/scripts/source.py          唯一跨平台 engine
.source/config.json               root-relative canonical config（PROTECTED）
.source/authority.*               signature、hash 與寫入權限契約
.source/state.json | handoff.md   engine-only checkpoint（GENERATED）
source/                           正式 Skill、scripts、references、assets
tests/                            Windows／Linux／macOS 端到端驗證
```

五個 managed skills 共用同一狀態機；GitHub repository 維持 private。Notion Prompt 只讀，CDN 未配置 provider／target 前不部署。
