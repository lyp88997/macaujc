# TASK-H/I 报告(BATCH-005, 总监直做)

## TASK-H: 前端优化 DONE
- 总览最新一期: 数据源切到 /api/draws?limit=1(期号一致才覆盖), 球按波色着色,
  每球下标注生肖(ball-col/zlabel), 单击任一球复制全部 7 个号码; loadMeta(波色分布)保留
- ball() 增加 label 参数(带标签时包 ball-col 纵排列)
- 新增 zodiacOf(it,n)(与 waveOf 同构, 特码取 index 6, 简繁由后端数据保证)
- 历史页: 表头 6→4 列(期号/时间 合并, 移除特码生肖列), 行模板期号+时间(去年份)两行,
  平码/特码球全部带生肖标注, colspan 6→4
- 验证: node --check OK, 52 id 零缺失, 9 特征在位, 无旧列残留, loadMeta 保留

## TASK-I: 重部署+线上验证 DONE
- 容器 Recreate 后 2291 期即时在库(持久化稳定)
- 线上新特征 12 处命中; /api/draws limit=1 抽查: wave=[蓝,绿,红,绿,绿,红,绿],
  zodiac=[猴,鼠,雞,虎,雞,鼠,虎], 47→蓝/猴 ✓ (着色与标注输入正确)
