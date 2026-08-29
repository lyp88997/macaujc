# TASK-AD/AE 报告(BATCH-016, 总监直做)

## TASK-AD: 挑码/预测交互+导航顺序 DONE
- ball() 加 copyAll 选项(data-copyall 属性); 全局点击代理优先拦截 data-copyall→按 PK_LAST/PD_LAST 复制全集
- 挑码页: 结果球 copyAll+文案"单击号码复制全部"; 清空按钮 4px10px/12px→9px18px/13.5px+加粗
- 智能组号整卡删除(非单按钮, 避免死卡)+死代码清理: genPick/PK_SET/pk-gen/pk-copy-set/pk-set/pk-note/pk-pool/mockApi /api/pick 分支, 19刀全中
- 预测页: 打分文案 recency→权重40; 模式去英文(综合/热号/冷号/遗漏, value 不动不影响后端); 推荐球+pred大球接 copyAll
- 导航: 统计分析 overview,draws,omit,predict,picker,stats 调至末位(LOADERS 映射与顺序无关, 零风险)

## TASK-AE: 双实例部署+验证 DONE
- 沙盒: 单击球→代理拦截→剪贴板收 3 9 17 22 38 45 全集 OK(坑: Node26 navigator 只读 getter, 须 defineProperty 覆写, 连败9次全是测试台问题非代码)
- 线上: 双实例 md5 一致 e6f22d39; copyall 2处/copyAll:true 3处/智能组号 0残留/pk-gen 0/权重40 1处/英文模式 0残留/导航顺序实测正确
- GitHub cb74a00

## 风险
- data-copy 单球复制仍保留(ball copy 选项), 目前仅 HTML 静态用; 若需彻底移除单球复制可后续批处理
