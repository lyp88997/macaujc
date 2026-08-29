# 🎰 新澳六合 分析预测

> 新澳六合号码统计分析与预测服务 · 版本 v1.1.9
> 开发者 @平歌歌 · 项目地址：https://github.com/lyp88997/macaujc · TG 联系：https://t.me/mzlpin

[![tests](https://img.shields.io/badge/tests-5%2F5%20pass-brightgreen)]() [![version](https://img.shields.io/badge/version-1.1.9-blue)]() [![stdlib](https://img.shields.io/badge/deps-Python%20stdlib%20only-orange)]()

---

## 项目介绍

**新澳六合 分析预测**（仓库名 macaujc）是一套自托管（self-hosted）的号码统计分析与预测服务：
后端 Python 标准库实现（http.server + sqlite3 + urllib），**零第三方依赖**；前端单文件
`web/index.html`（原生 HTML/CSS/JS，深浅双主题、玻璃效果、移动端自适应）。

- **自动采集**：启动即后台采集 2020→2026 全部历史（约 2292 期），此后每 300s 增量同步
- **开奖追新**：每日 21:32:32 开奖后，页面每 1 秒轮询直至新数据到达，自动刷新展示
- **统计分析**：多维度窗口统计（号码/波色/生肖/五行/单双/大小/头尾/合数），遗漏榜 + 🔥 冷热徽标
- **预测推荐**：综合打分模型（权重 40 + 遗漏压力 30 + 维度回补 15 + 日种子 15），四种模式（综合/热号/冷号/遗漏）
- **挑码筛选**：多条件交集引擎（波色/生肖/五行/家野/单双/大小/头尾/合数），单击球复制全部结果
- **双实例部署**：Docker 容器 + systemd 服务，同源 API + 单页应用

## 功能一览

| 页面 | 功能 |
|---|---|
| 数据总览 | 最新开奖大球 + 波色/生肖/五行章、七大模块统计卡、开奖倒计时、开奖后秒级追新 |
| 历史开奖 | 期号/时间/号码/特码五行一行式（响应式缩放，手机居中、电脑左对齐），复制全部 |
| 遗漏统计 | 多维度遗漏榜，遗漏 ≥ 平均×1.5 打 🔥 徽标 |
| 预测推荐 | 四模式打分推荐 + 评分构成说明，单击号码复制全部 |
| 挑码筛选 | 多条件交集筛选，单击号码复制全部 |
| 统计分析 | 窗口 50/100/200(/500)期 多维度频次统计 + 图表 |
| 主题 | 深浅双主题（默认浅色）玻璃效果，头部 🌙/☀️ 一键切换，localStorage 记忆 + 防闪色 |

## 快速开始

### 方式一：Docker

```bash
docker compose up -d          # 监听 8787
curl http://localhost:8787/api/status
```

### 方式二：直接运行

```bash
python3 app/server.py --port 8000 --db ./data/macaujc.db
curl http://localhost:8000/api/status
```

### 部署脚本

```bash
bash deploy/deploy.sh         # 本地容器重建 + 端到端验证
```

### 运行测试

```bash
python3 tests/test_*.py       # 单元 + 端到端(起真实服务)
```

## API 一览

| 端点 | 方法 | 说明 |
|---|---|---|
| `/api/status` | GET | 服务/库/采集器状态 + 最新一期 + 下一期开奖时间(next_draw_at) |
| `/api/draws` | GET | 历史开奖（newest first，含 7 位属性数组） |
| `/api/stats` | GET | 窗口统计（key 全域返回，count 降序） |
| `/api/omit` | GET | 遗漏统计（key 全域返回） |
| `/api/predict` | GET | 预测推荐（composite/hot/cold/omission 四模式） |
| `/api/pick` | GET | 组号（6+1） |
| `/api/filter` | POST | 挑码筛选（多条件交集） |
| `/` | GET | 单页应用（web/index.html，SPA 回退） |

## 项目结构

```
app/
  server.py          入口: 参数解析 + 装配
  config.py          路径/常量/波色官方固定表
  app/db.py          SQLite: draws + meta
  fetcher.py         后台采集: 历史批量 + 300s 增量
  zodiac_wuxing.py   属性派生: 波色/生肖/五行/单双大小头尾合数
  stats_engine.py    /api/stats + /api/omit
  predictors.py      /api/predict + /api/pick
  picker_engine.py   /api/filter 交集引擎
  http_api.py        路由 + CORS + 静态文件
web/index.html       前端单文件(双主题/玻璃/响应式)
tests/               单元 + 端到端测试
deploy/              Dockerfile/docker-compose/部署脚本/编辑脚本/验证脚本
tasks/ reports/ context/   AON 批次记录/任务报告/状态外置
```

## 版本历史（节选）

| 版本 | 内容 |
|---|---|
| v1.1.9 | 品牌升级「新澳六合 分析预测」(渐变)、开奖后 1s 追新、总览去序号、筛选页放大、底部署名 |
| v1.1.8 | 历史页五行并入球行、球体极限缩放、全列居中 |
| v1.1.7 | 特码生肖中心线对齐、电脑端左靠期号 |
| v1.1.6 | 预测页摘要中文化、窗口带「期」、历史页响应式缩放 |
| v1.1.5 | 挑码/预测单击复制全部、删智能组号、导航重排 |
| v1.1.0 | 深浅双主题 + 玻璃效果 + 防闪色（b516177） |
| v1.0.x | 基础统计/预测/筛选引擎、完整词标注、🔥 徽标、球色映射链 |
| — | 更早版本见 git log |

## 许可 | License

本项目以学习与研究目的发布，不构成任何投注建议。

## 节点与链接

- 🌐 澳门公网：http://45.202.246.39
- 🐳 容器节点：`http://10.5.0.2:8787`（内网）
- 📦 仓库：https://github.com/lyp88997/macaujc
- 📱 TG：https://t.me/mzlpin
- 📊 Komari 服务器状态：https://tz.mzlp.eu.org/
