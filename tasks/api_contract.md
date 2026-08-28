# API 契约 v1.0(总监定义, 后端/前端唯一对接依据)

> 后端: Python 3.11 stdlib-only(http.server + sqlite3 + urllib), 容器内监听 0.0.0.0:8000
> 静态: GET / → web/index.html; GET /api/* → JSON; 全部响应带 CORS: *
> 数据库: SQLite /app/data/macaujc.db, 主表 draws(expect TEXT PK, open_time TEXT,
>         n1..n6 INT, special INT, synced_at TEXT) —— n1..n6 保留开奖原始顺序(平一~平六)

## 1. GET /api/status
```json
{"ok":true,"service":"macaujc-predictor","version":"1.0.0",
 "last_draw":{"expect":"2026239","open_time":"2026-08-27 21:32:32",
   "codes":["47","43","34","17","22","07"],"special":"05"},
 "db":{"total_draws":2200,"first_expect":"2020355","last_expect":"2026239","last_sync":"..."},
 "fetcher":{"running":true,"last_fetch":"...","last_error":null},
 "next_draw_at":"2026-08-28 21:32:32","server_time":"..."}
```

## 2. GET /api/draws?limit=50&offset=0 (newest first)
items 每条: expect/open_time/codes[6]/special + 全 7 位属性数组(平1-6+特):
wave(红/蓝/绿) / zodiac / wuxing(金木水火土) / odd_even(单/双) / big_small(大/小)
/ head(0-4) / tail(0-9) / he_sum(2-13)

## 3. GET /api/stats?window=100&dim=<key>
dim ∈ special_number|special_wave|special_zodiac|special_tail|special_head|special_wuxing|special_odd_even|special_big_small|normal_number|normal_wave|...
→ {"window":100,"from_expect":"...","to_expect":"...","items":[{"key":"05","count":12,"rate":0.12,"last_expect":"2026230","omission":9}]}
⚠️ key 全域返回(49 号/3 波/12 生肖/10 尾/5 头/5 行), count=0 也要出现, items 按 count 降序。

## 4. GET /api/omit?scope=special
→ 各维度遗漏: {"number":[{"key","omission","max_omission","avg_omission"},...], "wave":[...], "zodiac":[...], "tail":[...], "head":[...], "wuxing":[...]}
(omission=距上次出现的期数; max/avg 基于全部历史)

## 5. GET /api/predict?mode=composite|hot|cold|omission&count=10&window=100&scope=special|normal
→ {"mode","scope","window","generated_at","items":[{"rank":1,"number":"05","score":87.3,
    "attrs":{"wave":"红","zodiac":"虎","wuxing":"金","head":0,"tail":5,"he":5},
    "reasons":["近100期出现8次(热)","遗漏9期≈平均12.5的回补区","红波近30期偏冷"]}],
   "disclaimer":"统计分析仅供参考,不构成任何中奖承诺"}
composite 打分(总监规定, 透明可解释):
  score = 40×recency加权频率(decay^age, decay=0.985, window 内) 归一
        + 30×遗漏压力 min(omission/avg,2)/2
        + 15×维度回补(所属波色/生肖在 window 内占比低于均值程度) 归一
        + 15×日种子平滑随机(当天固定, 避免"每次刷新全变")
reasons 必须逐条对应真实计算值, 禁止编造文案。

## 6. POST /api/filter  body={"groups":{"zodiac":["馬","蛇"],"wave":["红"],"big_small":["大"],"tail":["5"],"odd_even":["单"],...}}
→ {"union":{"zodiac":[...号码],...},"remaining":[升序号码],"count":n}
单选组 big_small/odd_even 服务端强制(传多值取交集为空的语义按覆盖处理);
规则与 macaujc 挑码助手一致(picker_rules.md): 生肖/家野/五行/六合六冲随年, 其余固定表。

## 7. POST /api/pick  body={"count":7,"pool":"composite|hot|cold|all","filters":{...同 filter.groups}}
→ {"sets":[["05","12","23","31","38","44","07"]],"strategy_note":"前6=推荐池按分取,第7=特码推荐"}
count=7: 前 6 个为平码推荐 + 最后 1 个为特码推荐(号码不重复)。

## 属性派生规则(后端必须实现, 禁用 API wave/zodiac 字段)
- 波色=官方固定表: 红 01,02,07,08,12,13,18,19,23,24,29,30,34,35,40,45,46 |
  蓝 03,04,09,10,14,15,20,25,26,31,36,37,41,42,47,48 | 绿 05,06,11,16,17,21,22,27,28,32,33,38,39,43,44,49
- 生肖: 槽位k号码=k+1,k+13,k+25,k+37(k=0含49), 槽位0=当年生肖, 逐年倒退;
  年份按开奖日查 raw/lunar_table_1900_2100.json(start=农历正月初一公历日, branch=地支序0-11鼠起),
  date < start 则归上一年; cycle=鼠牛虎兔龍蛇馬羊猴雞狗豬
- 五行: 按 openTime 公历年 t, while t<1976:t+=30; while t>2025:t-=30 → raw/wuxing_table.json[t]
- 大小: 01-24 小/25-49 大; 单双: 奇/偶; 头=十位; 尾=个位; 合数=十位+个位
- 简化声明: 五行按公历年(非农历年)取表, 春节前后数日可能差一档, 文档注明即可

## 数据采集(后端内置后台线程)
- 首次: GET https://history.macaumarksix.com/history/macaujc2/y/{year}, year=2020..2026
  响应 {code:200,data:[...]} 才算成功(code=0/data=null 判空); 按 expect 全局去重
  (年份间有混装), openCode="47,43,34,..." 两位零填充逗号分隔 7 个
- 增量: 每 300s GET https://macaumarksix.com/api/macaujc2.com (顶层 JSON 数组, 无包装)
  抓 expect/openCode/openTime, 新期号才入库; 请求间隔≥0.5s, 超时≤10s
- next_draw_at = 今天 21:32:32(已过则明天), 北京时间
