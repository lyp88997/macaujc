# BATCH-023 总监汇总报告

## 状态
- Worker TASK-AR/TASK-AS/TASK-AT：均因 API 超时撞迭代上限，未返回可验证的结构化报告；不采信其未完成结论。
- 总监已直接完成源码审查、真实接口数据回测、修复和回归验证。

## 总监实测
- 数据源：`http://10.5.0.2:8787/api/draws?limit=300`
- 导入临时库：300 期，范围 `2025307` 至 `2026241`
- Walk-forward：最近 60 期逐期预测，每次仅使用此前最多 100 期。
- top-7 平均命中：composite 1.133、hot 1.083、cold 1.067、omission 1.150。
- 该样本只作工程基线，不证明存在可持续预测优势。

## 已确认问题与修复
1. `app/predictors.py` 的 `pick_sets` 原先把整个推荐池固定按 `special` 打分，和“前 6=平码、第 7=特码”的接口契约冲突。现改为前 6 使用 `normal` 预测池，第 7 使用 `special` 预测池；筛选条件同时应用，号码仍不重复。
2. 综合分中 `avg=None` 的无历史号码原先遗漏压力为 0。现使用 scope 理论平均间隔作为保守基准，避免该分量被静默关闭。
3. 删除 hot 模式无效的重复排序和未使用的 `tiebreak` 变量。

## 未改动判断
- 频率项按理论上界归一，当前数值偏小不能单独证明公式错误；在缺少更长时间回测和对照实验前不调整权重。
- 未新增命中率承诺、未改数据库结构、未部署生产实例。

## 验证
- `python tests/test_predictors.py`：PASS
- `python tests/test_e2e.py`：PASS
- `python -m compileall -q app tests`：PASS
- `git diff --check`：PASS
- 仓库不存在 `tests/test_stats_engine.py`，未将其作为有效测试目标。
