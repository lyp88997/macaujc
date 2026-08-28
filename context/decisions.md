# 决策记录(Predictor)

## 2026-08-28
1. API 契约 v1.0 由总监统一定义(tasks/api_contract.md), Worker 不得自创端点。
2. 后端 stdlib-only(http.server + sqlite3 + urllib), 容器无 pip。
3. 波色/生肖/五行一律从号码自派生, 禁用上游 API 的 wave/zodiac 字段。
4. Worker 返回与自述不符时以总监实测为准(AON 步骤8): TASK-A 自报全绿但服务起不来,
   总监修复后才算 DONE; 前端 Worker 零产出改总监直做(重试上限规则)。
5. 六冲组在阶段一规则底稿有据(picker_rules.md L101), 引擎必须实现, 马鼠冲等 6 对。
6. 镜像不装 tzdata: 后端时间逻辑硬编码 UTC+8, 避免非必要依赖。
7. 数据库路径优先级 $MACAUJC_DB > /app/data > <base>/data, 三种布局兼容。
