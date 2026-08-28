# TASK-TASK-A Worker 报告
- TASK_ID: TASK-A
- STATUS: DONE
- SUMMARY: 已按 tasks/api_contract.md v1.0 用 Python 3.11+ 纯标准库(http.server+sqlite3+urllib)实现完整后端, 位于 /opt/data/workspace/macaujc-predictor/app/ (9 模块 ~1770 行) + tests/ (5 个测试脚本 ~460 行) + README.md。含: SQLite 存储(draws 表, expect TEXT PK, n1..n6 原始顺序+special, WAL); 后台采集线程(首次批量抓 y2020..y2026 共 2291 期按 expect 全局去重入库, 每 300s 增量同步 latest, 间隔≥0.5s/超时≤10s); 属性派生(波色官方固定表/生肖槽位公式+阴历年查表/五行公历年±30 折返查表/单双/大小/头/尾/合数); 7 个 API 端点全部实现并实跑验证(/api/status,/api/draws,/api/stats,/api/omit,/api/predict,/api/filter,/api/pick)+CORS:*+静态文件服务(web/index.html, SPA 回退); composite 打分严格按总监公式 40×recency(decay^age,0.985)+30×遗漏压力 min(om/avg,2)/2+15×维度回补+15×日种子随机(当天固定), reasons 逐条对应真实计算值。真实验收: 服务器实跑加载 2291 期真实历史(2020130..2026239 期号连续零缺口), /api/status 返回与契约示例一致(last_draw 2026239, codes 47,43,34,17,22,07, special 05, next_draw_at 21:32:32), 全部端点用 curl 实测结构/语义/参数校验/CORS 正确, 5 个测试套件全绿。
- CHANGES: 新建 app/server.py(入口, --port/--db 参数+MACAUJC_DB env), app/config.py(路径解析+波色表), app/db.py(SQLite 层: upsert 按条容错/查询/meta), app/fetcher.py(批量+增量采集线程), app/zodiac_wuxing.py(属性派生), app/stats_engine.py(stats+omit, key 全域 count 降序, omission/max/avg 全历史), app/predictors.py(composite/hot/cold/omission 打分+pick 组号), app/picker_engine.py(filter 交集引擎, 生肖/家野/五行随年+固定组, 单选组覆盖语义, 简繁生肖兼容), app/http_api.py(路由+CORS+静态+SPA 回退), README.md(结构/API 速览/数据坑/实现取舍); 复制 lunar_table_1900_2100.json 与 wuxing_table.json 进 app/data/; 新增 tests/test_{picker,stats,fetcher,predictors,e2e}.py。
- FINDINGS:
- severity: 高
  file: app/db.py
  issue: 上游真实数据 expect=2022132 的 openCode='15,44,27,33,33,18,19' 含重复对 33,33 (全量 2291 期唯一一条, 实测确认)。若按'7 号码互不重复'严格校验会拒绝该期导致 backfill 整批失败
  suggestion: 已修复: 校验放宽为仅 7 位+范围 1-49(不判重复), upsert_draws 单条格式非法时跳过并打日志不中断整批, 已在 README 数据坑一节注明
  needs_change: False
- severity: 高
  file: app/zodiac_wuxing.py
  issue: lunar_table_1900_2100.json 的 branch 字段并非契约所述'地支序0-11鼠起': 实测 2020 鼠年 branch=6, 2025 蛇=11, 2026 马=0, 即表内以 马=0 起序(全表 201 年相邻+1 规律一致验证)。若按字面直用会全部生肖错位 6 位
  suggestion: 已修复: 标准地支序=(branch+6)%12 (BRANCH_OFFSET=6), 并用 2026 马年槽位(马=01,13,25,37,49 等)与 2020/2025 跨年抽查验证通过
  needs_change: False
- severity: 中
  file: app/stats_engine.py
  issue: 契约写 he_sum 域 2-13, 但官方合数实测表(picker_rules.md §2)中 01-09 合数=面值(合单表含 01,03..), 即全域实为 1-13
  suggestion: 已按权威实测表取 1-13 并用合单/合双/合大/合小四表逐一回归验证, README 已注明取舍依据
  needs_change: False
- severity: 中
  file: app/predictors.py
  issue: pick 在 filters 收窄后池小于 count(如生肖马仅 5 号)时无法凑 7 位不重复
  suggestion: 已处理: 返回池内全部不重复号码(分数降序, 末位为特码推荐), 不虚增号码, 测试覆盖该退化场景
  needs_change: False
- severity: 低
  file: app/config.py
  issue: 契约 DB 路径 /app/data 与 deploy/docker-compose.yml 挂载点 /app/app/data 不一致
  suggestion: 已做路径优先级兼容: $MACAUJC_DB env > /app/data(存在时) > <base>/data, 三种部署布局均可落库, 已与部署 subagent 的 compose 卷对齐
  needs_change: False
- severity: 低
  file: app/http_api.py
  issue: web/index.html 由前端任务负责, 当前不存在
  suggestion: 静态服务已就绪: 有 index.html 则服务, 否则返回内置占位页(列出全部 API), 前端产物放入 web/ 即自动生效
  needs_change: False
- severity: 低
  file: app/stats_engine.py
  issue: window 期 omission 与全历史 avg/max 在窗口口径上并存, 极端场景(窗口内从未出现)omission=窗口长度
  suggestion: 按契约字面语义实现(窗口内统计+全域 key), 已在单测锁定口径
  needs_change: False
- TEST_RESULT: 全部通过: (1) 属性派生单元验证——波色 49 号对照契约固定表, 生肖 2026 马年槽位(马=01,13,25,37,49/蛇=02,14,26,38/春节前归蛇年)对照 picker_rules.md 实测表, 五行 2026(→1996 表)49 号金木水火土全表对照, 合数四表(合单/合双/合大/合小)逐一回归, 单双大小头尾边界(24/25, 01, 49); (2) 统计引擎合成数据——count/rate/last_expect/omission/max/avg 与手算一致, key 全域(49/3/12/10/5/5/13)与 count 降序锁定, 空库边界; (3) 采集解析——用 analysis 阶段保存的真实响应验证 code==200判空/顶层去重/排序方向防护/期号连续性(2291 期 2020130..2026239 零缺口, 期界跨年正确); (4) 预测引擎——composite 分解 40+30+15+15 全 49 号逐分校验, 日种子当天稳定, hot/cold/omission 排序语义正确, pick 前6+特码不重复; (5) 真实服务器集成(实跑): /api/status 与契约示例字段一致(2291 期, last_draw 2026239), /api/draws 属性数组 7 位逐项对照上游 zodiac(虎/雞等一致), /api/stats 4 个维度手验(sum=window, normal 波色 sum=180), /api/omit 六维度全域, /api/predict 4 模式+双 scope, /api/filter 交集语义(马蛇∩红={01,02,13} 手验)与单选组覆盖语义, /api/pick composite/all+filters, 404/400 错误路径, CORS:*, OPTIONS 预检, 分页 offset; (6) 5 个测试脚本(picker/stats/fetcher/predictors/e2e)最终回归全绿, 增量同步 300s 周期实跑确认(last_fetch 更新, last_error=null)。
- RISKS: 1) 上游接口无 SLA: macaumarksix.com 若变更结构或限流, 增量同步会失败(last_error 可见), 但已入库的 2291 期不受影响; 2) 上游数据质量: 2022132 已出现重复对, 未来若再出现脏数据仅告警跳过该期; 3) 五行按公历年取表为契约认可的简化, 春节前后数日可能差一档; 4) fetcher 增量周期 300s, 开奖瞬间(21:32:32)后最长 5 分钟才见新期, 前端如需即时可用 /api/draws 轮询或缩短 SYNC_INTERVAL; 5) 首次部署需网络可达 history.macaumarksix.com 拉全量(约 10s+), 此前 /api/stats 返回空 items 结构(不报错)。
- NEXT_ACTION: 前端任务(TASK-B?)可直接对接 http://<host>:8000 的 7 个端点, web/index.html 放入项目 web/ 目录即被静态服务; 建议部署任务用 deploy/docker-compose.yml 起容器(已与后端路径约定对齐); 若总监要求调整打分权重或 filter 组语义, 改 predictors.py/picker_engine.py 常量即可, tests/ 可回归。
