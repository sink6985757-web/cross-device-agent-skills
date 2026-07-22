# Shutdown 固定模板

## A. 重寫 `handoff.md`

```markdown
# Handoff

## 目前做到哪
<最後完成的成果，最多三句>

## 目前狀態
- 可執行：<是／否／PARTIAL>
- 已驗證：<測試或回讀>
- 未完成：<沒有就寫「無」>

## 下一步
1. <最小可執行步驟>
2. <可選>
3. <可選>

## 注意事項
- <風險、workaround 或不要碰的範圍；沒有就寫「無」>

## 最近更新
- 時間：<YYYY-MM-DD HH:mm，含時區>
- 更新者：<Agent 名稱>
- 電腦：<本機電腦名稱>
- 成果 commit：<SHA／未提交／NOT_CONFIGURED>
- Git push：<VERIFIED／PARTIAL／BLOCKED／NOT_CONFIGURED>
- Obsidian：<VERIFIED／PARTIAL／BLOCKED／NOT_CONFIGURED>
```

## B. 收工回報

```markdown
# 收工報告

- 整體：<VERIFIED｜PARTIAL｜BLOCKED>
- Agent：<本次 Agent 名稱>
- 電腦：<本機電腦名稱>
- 本地：<完成內容>
- GitHub：<repository、commit、push 狀態>
- Obsidian：<筆記相對路徑與回讀狀態>
- `AGENTS.md`：<未變更｜已更新>
- `handoff.md`：<已更新並回讀>

## 回滾
- <commit／備份／還原方法>

## 唯一續跑點
1. <下一次開工直接執行的第一步>
```
