# BATCH-001(Predictor) 批记录

GOAL: 构建专业预测系统(深色科技感管理后台)并容器化部署至 localhost-root:8787

## 依赖链
TASK-A(后端引擎) / TASK-B(前端UI) —— 并行
  ↓ (两者完成)
TASK-C 容器化部署+端到端验证 —— 串行, 总dir亲做(写 Dockerfile/compose/部署脚本)

## 并行判定
- TASK-A 只写 app/ + requirements 说明, TASK-B 只写 web/; API 契约已由总监统一定义
  (tasks/api_contract.md)作为唯一对接依据 → 无文件冲突 / 目标独立 / 并行省时 => 通过

## 批次
- TASK-A 后端引擎工程师 → app/server.py 等
- TASK-B 前端 UI 工程师 → web/index.html 等

## 上游事实(来自 macaujc-analysis, 勿再实测)
- 数据源/字段/坑: macaujc-analysis/context/api_analysis.md
- 筛选规则: macaujc-analysis/context/picker_rules.md (15 组)
- 术语与属性表: macaujc-analysis/context/rules_glossary.md
- 机器可读表: macaujc-analysis/raw/{wuxing_table,lunar_table_1900_2100}.json
