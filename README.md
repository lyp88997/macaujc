# macaujc-predictor 后端引擎

澳门六合彩号码统计分析服务。Python 标准库实现(http.server + sqlite3 + urllib),零第三方依赖。

## 启动

```bash
python3 app/server.py                # 监听 0.0.0.0:8000, 库默认 /app/data/macaujc.db (本地回退 ./data/)
python3 app/server.py --port 8000 --db /app/data/macaujc.db
```

启动后:
1. 后台线程批量采集历史(2020..2026 共 7 个分片,按 expect 全局去重,~2291 期);
2. 每 300s 增量同步最新一期(macaumarksix.com/api/macaujc2.com);
3. HTTP 服务立即可用(采集在后台进行)。

## 结构

```
app/
  server.py          入口: 参数解析 + 装配
  config.py          路径/常量/波色官方固定表
  db.py              SQLite: draws(expect PK, open_time, n1..n6 原始顺序, special, synced_at) + meta
  fetcher.py         后台采集线程: 历史批量 + 300s 增量; 判空 code==200 且 data 非空
  zodiac_wuxing.py   属性派生: 波色/生肖(槽位公式+阴历年查表)/五行(公历年±30 折返)/单双大小头尾合数
  stats_engine.py    /api/stats + /api/omit 计算 (key 全域, count 降序)
  predictors.py      /api/predict composite 打分 + /api/pick 组号
  picker_engine.py   /api/filter 交集引擎 (生肖/家野/五行随年, 波色单双大小头尾合数固定)
  http_api.py        路由 + CORS + 静态文件(web/index.html, SPA 回退)
tests/               单元 + 端到端测试 (python3 tests/test_*.py)
data/                本地开发默认 DB 目录
app/data/            lunar_table_1900_2100.json + wuxing_table.json (由 analysis 阶段复制)
```

## API 速览(权威定义见 tasks/api_contract.md)

| 端点 | 说明 |
|---|---|
| GET /api/status | 服务/库/采集器状态 + 最新一期 + next_draw_at(今日 21:32:32, 已过则明日, UTC+8) |
| GET /api/draws?limit=50&offset=0 | 历史(newest first), 每条含 codes[6]/special + 全 7 位属性数组 |
| GET /api/stats?window=100&dim=special_number | 窗口统计; key 全域返回(count=0 也在), count 降序 |
| GET /api/omit?scope=special | 各维度遗漏: number/wave/zodiac/tail/head/wuxing |
| GET /api/predict?mode=composite&count=10&window=100&scope=special | composite/hot/cold/omission, 40+30+15+15 打分, reasons 逐条对应真实计算值 |
| POST /api/filter | body={"groups":{...}} → union/remaining/count; 单选组多值按覆盖 |
| POST /api/pick | body={"count":7,"pool":"composite","filters":{...}} → 前6平码+第7特码 |

composite 打分 = 40×recency加权频率(decay^age, decay=0.985) + 30×遗漏压力 min(om/avg,2)/2
             + 15×维度回补(波色/生肖窗口占比缺口) + 15×日种子随机(当天固定)。

## 已知上游数据坑(已处理)

- 历史按年接口判空必须 `code==200 && data 非空`(HTTP 200 不代表命中);
- 年份间混装/滚动窗 → 落库前按 expect 全局去重 + 排序;
- 排序方向不稳定 → 库内查询统一按 expect 排序;
- expect=2022132 openCode 为 `15,44,27,33,33,18,19`(含重复对) → 校验仅查 7 位 + 1-49, 不查重复;
- lunar 表 branch 字段以 馬=0 起序 → 换算标准地支序(鼠=0)需 `(branch+6)%12`;
- 五行按公历年取表(简化声明, 春节前后数日可能差一档)。

## 契约备注(实现取舍)

- stats/omit 的 he_sum 域为 1-13: 官方合数表中 01-09 合数=面值(合单含 01), 与"合数=十位+个位"定义自洽;
- pick 在 filters 收窄后池不足 count 时, 返回池内全部不重复号码(顺序 = 分数降序, 末位为特码推荐);
- GET / 无 web/index.html 时返回内置占位页(列出全部 API), 不算错误。
