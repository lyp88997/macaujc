# BATCH-012 依赖链(Predictor)

BATCH-012 依赖链: TASK-V(倒计时归零自动刷新功能) → TASK-W(双实例部署+验证, 串行)
并行判定: V/W 同文件/部署依赖 => 总监直做
需求(用户原话): 开奖时间每天都是21:32:32，增加倒计时归零后自动刷新数据
方案: startCountdown 归零→ stopCountdown → autoPollNewDraw(): 20s间隔轮询 /api/status 比对 expect, 最长12分钟; 检测到新期→ loadStatus()+loadDraws(当前页联动)+toast "🎉 新一期已出"; 未检测到→按 next_draw_at 重挂下一期倒计时
背景: 后端采集实测开奖后 1m44s~5m 入库; 官网开奖时间固定 21:32:32
