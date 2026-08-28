# BATCH-002 依赖链(Predictor)

BATCH-002 依赖链: TASK-A ∥ TASK-B(并行) → TASK-C(串行, 总监亲做)
并行判定: A 写 app/ / B 写 web/ 目标独立 / 无依赖 / 不写同一文件 / 并行省时  => 通过
批次: TASK-A(后端引擎, deleg_fd0dc24d/t0) TASK-B(前端 UI, deleg_fd0dc24d/t1)

## 执行结果
- TASK-A: Worker 自报 DONE, 但总监实测发现致命 bug(server.py 引用不存在的
  config.resolve_db_path, 服务无法启动) + 六冲组未实现 → 总监修复后验收通过。
  报告: reports/task-TASK-A.md
- TASK-B: Worker 撞迭代上限 + LLM 超时, 零产出(web/ 不存在) → 按失败规则
  (第2次失败不再重派)改由总监直做, 单文件 web/index.html 交付。报告: reports/task-TASK-B.md
- TASK-C: 总监亲做(Dockerfile/compose/deploy.sh 部署件 + SSH 侧构建 + 8787 端到端验证)。
