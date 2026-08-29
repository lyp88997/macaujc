# TASK-V/W 报告(BATCH-012, 总监直做)

## TASK-V: 倒计时归零自动刷新 DONE
- startCountdown 归零→ autoPollNewDraw(): 20s/次轮询 /api/status, 最长12分钟
- 检测新期: toast "🎉 新一期 XXXX 已出" + loadStatus() 全量刷新 + 历史页联动
- 超时兜底: 12分钟无新期→按 next_draw_at 重挂下一期倒计时
- 实现波折: 刀1插重已修复(删残留+补收尾), 终版 node --check OK
- 沙盒实测: mock api 第二轮返回新期→ results=[loadStatus], toast "🎉 新一期 2026241 已出" ✅

## TASK-W: 双实例部署 DONE
- 容器 Recreate 完成端到端 ok:true 2292期/2026240; 澳门 systemd restart active
- 线上: macau/容器 autoPollNewDraw 2处+等待开奖 2处, 双实例 HTML cmp 一致
- GitHub 284fee0 推送
