# TASK-AN/AO 报告(BATCH-021, 总监直做)

## TASK-AN: README 重写 DONE
- 旧版为早期"后端引擎"文档(端口/品牌/署名全过时), 重写为项目级 README:
  品牌(新澳六合 分析预测)/介绍/功能一览表/快速开始(Docker+直跑+deploy.sh+测试)/API 8端点表/项目结构/版本历史表/许可/节点与链接(公网/容器/仓库/TG/Komari)
- 连带修复: tests/test_e2e.py 版本断言 1.0.0(硬编码)→动态跟随 server.__version__(首次修复缩进撞块, patch 现场校正)
- 测试 5/5 全绿(test_e2e/test_fetcher/test_picker/test_predictors/test_stats)

## TASK-AO: v1.1.9 Release DONE
- tag: git tag -a v1.1.9(带 -c 身份参数; 首次漏带致 tag 未创建, 补)→ push origin v1.1.9 → [new tag] 确认
- Release: gh 未安装→GitHub REST API(token 临时读取, 未落日志, 用后 unset); HTTP 201, id 378933377
- 匿名读回验证: name="v1.1.9 · 新澳六合 分析预测", draft=False, author=lyp88997, 正文含品牌/追新/署名/验证小节
- 双实例未动(纯文档+发布批, 服务零变更)

## COMMIT
- 3ba3873 docs: README 重写(新澳六合品牌/功能/API/部署/版本历史)+e2e版本断言动态跟随__version__

## NEXT_ACTION
- 无遗留; 下批如改 UI 记得清 .seq 死CSS(无害)
