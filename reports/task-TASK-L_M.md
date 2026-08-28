# TASK-L/M 报告(BATCH-007, 总监直做)

## TASK-L: 官网布局分析与移植 DONE
- 抓取 https://macaujc.com(156KB HTML + /css/app.*.css 165KB)提取官方真实布局:
  .his-items 单行 flex 居中; 每球 hisCode-item-number(46px/30px字)在上,
  hisCode-item-zodiac(14px)在下; 红色 hisCode-item-plus「+」分隔平码与特码
- 移植(macaujc-predictor 深色主题适配):
  * 新 .his-row(flex wrap 居中, gap 8/10)替代 draw-grid/draw-six 两层网格
  * 总览: his-row 单行(lg球44px + 生肖14px粗体), plus-cell plus 红色加号, 特码同行末尾
  * 历史: 每期一行 = 6平码球(各带下标生肖) + 红加号 + 特码球(带生肖), sm球
  * 表头 4列→3列(期号时间/开奖号码(号码下方为生肖)/特码五行), colspan 同步
- 修复: 历史行特码重复渲染残留td(改造时发现并删除); 死CSS(draw-z)清理

## TASK-M: 部署验证 DONE
- deploy.sh: Recreate 后 2291 期即时在库(持久化稳定)
- 线上: 新特征 7 处命中, 旧痕迹(draw-grid/draw-six/draw-z/sp-cell) 0
- 本地: JS 语法 OK, 62 id 无缺失, 历史行结构 6球+加号+特码球 ✓

## RISKS
- 手机窄屏: his-row 带 flex-wrap 会自动折行, 不溢出(官方为 PC 优先布局, 此处已适配)
