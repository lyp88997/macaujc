# 待办动作清单(合并)

- [高] app/server.py :: Worker自述全绿但服务器实际无法启动: 调用不存在的 config.resolve_db_path() 抛 AttributeError => 已修复: 改为 config.init_paths() + config.DB_PATH, 本地实跑2291期入库验证
- [中] app/picker_engine.py :: 契约#6声明'规则与挑码助手一致(含六冲)'但引擎未实现六冲组; 家野组存在但组名 family_wild 前端未暴露 => 已补六冲引擎(馬鼠/牛羊/猴虎/兔雞/龍狗/豬蛇, 相隔6位, 简繁兼容)并在前端补两组; 馬冲=9号数学验证通过(馬1,13,25,37,49∪鼠7,19,31,43)
- [低] deploy/deploy.sh :: 原脚本仅第1步带 -F ssh config, 后续步骤裸 ssh 存在断链风险 => 已重写为统一 $SSH 变量, 并加 __pycache__/*.db 排除项
- [低] deploy/Dockerfile :: python:3.11-slim 无 tzdata, TZ 环境变量本会回落UTC => 核实后端时间逻辑为硬编码 timezone(timedelta(hours=8)), 不依赖系统时区 → 维持最小镜像不改
- [高] app/db.py :: 上游真实数据 expect=2022132 的 openCode='15,44,27,33,33,18,19' 含重复对 33,33 (全量 2291 期唯一一条, 实测确认)。若按'7 号码互不重复'严格校验会拒绝该期导致 backfill 整批失败 => 已修复: 校验放宽为仅 7 位+范围 1-49(不判重复), upsert_draws 单条格式非法时跳过并打日志不中断整批, 已在 README 数据坑一节注明
- [高] app/zodiac_wuxing.py :: lunar_table_1900_2100.json 的 branch 字段并非契约所述'地支序0-11鼠起': 实测 2020 鼠年 branch=6, 2025 蛇=11, 2026 马=0, 即表内以 马=0 起序(全表 201 年相邻+1 规律一致验证)。若按字面直用会全部生肖错位 6 位 => 已修复: 标准地支序=(branch+6)%12 (BRANCH_OFFSET=6), 并用 2026 马年槽位(马=01,13,25,37,49 等)与 2020/2025 跨年抽查验证通过
- [中] app/stats_engine.py :: 契约写 he_sum 域 2-13, 但官方合数实测表(picker_rules.md §2)中 01-09 合数=面值(合单表含 01,03..), 即全域实为 1-13 => 已按权威实测表取 1-13 并用合单/合双/合大/合小四表逐一回归验证, README 已注明取舍依据
- [中] app/predictors.py :: pick 在 filters 收窄后池小于 count(如生肖马仅 5 号)时无法凑 7 位不重复 => 已处理: 返回池内全部不重复号码(分数降序, 末位为特码推荐), 不虚增号码, 测试覆盖该退化场景
- [低] app/config.py :: 契约 DB 路径 /app/data 与 deploy/docker-compose.yml 挂载点 /app/app/data 不一致 => 已做路径优先级兼容: $MACAUJC_DB env > /app/data(存在时) > <base>/data, 三种部署布局均可落库, 已与部署 subagent 的 compose 卷对齐
- [低] app/http_api.py :: web/index.html 由前端任务负责, 当前不存在 => 静态服务已就绪: 有 index.html 则服务, 否则返回内置占位页(列出全部 API), 前端产物放入 web/ 即自动生效
- [低] app/stats_engine.py :: window 期 omission 与全历史 avg/max 在窗口口径上并存, 极端场景(窗口内从未出现)omission=窗口长度 => 按契约字面语义实现(窗口内统计+全域 key), 已在单测锁定口径
- [高] web/index.html :: loadDraws 使用未声明变量 sm(手误简写), 历史开奖页必然抛 ReferenceError 显示加载失败 => 已修复为 {sm:true}, 本地实测 /api/draws 数据正常渲染路径无异常
- [高] deploy/docker-compose.yml :: 持久化卷挂载点 /app/app/data 与容器真实 DB 路径 /app/data 不一致, 首轮部署数据写入容器临时层, 容器重建即丢 2291 期(重部署 step5 输出 total_draws:0 实证) => 已修: compose 显式 MACAUJC_DB=/app/data/macaujc.db + 卷改挂 /app/data + 删除 Dockerfile 错误 VOLUME 声明; 终验宿主机 /opt/macaujc-predictor/app/data/ 出现 macaujc.db+WAL
