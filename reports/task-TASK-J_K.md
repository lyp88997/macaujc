# TASK-J/K 报告(BATCH-006, 总监直做)

## TASK-J: 布局协调优化 DONE
- 总览最新一期: 头部两行制(期号 #2026239 大字 27px 在上, 开奖时间 12.5px 在下,
  ov-head/ov-exp/ov-time); 号码阵 2 列 grid(draw-grid, 平码 2x3 + 加号/特码末行);
  球升 lg 档(44px/字17px), 生肖字 9.5px→11.5px(每球下方 ball-col 纵排)
- 历史开奖: 生肖独立成行(draw-z 独立 grid), 与球行(draw-six)列宽锁 27px 严格对齐
  (3球行→3生肖行交错); 特码球+下方生肖; 时间去年份保留
- 交互不变: 总览单击任一球仍复制全部 7 号

## TASK-K: 部署 DONE
- deploy.sh 重建容器(Recreate), 服务第2次探测就绪
- 线上: 新特征 16 处命中, 旧痕迹(last-big/ov-lasttime)0, 2291 期在库
- 数据源抽查: expect 2026239, zodiac[猴,鼠,雞,虎,雞,鼠,虎], wave[蓝,绿,红,绿,绿,红,绿]
