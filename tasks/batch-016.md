# BATCH-016 依赖链(Predictor)

BATCH-016 依赖链: TASK-AD(挑码页单击复制全部+清空放大+删智能组号卡 / 预测页文案去英文+单击复制全部 / 导航统计调末位) → TASK-AE(双实例部署+验证, 串行)
并行判定: AD/AE 同文件(web/index.html)/部署依赖 => 总监直做
需求(用户原话): 挑码页: 单击任何一位号码改为复制全部, 放大清空按钮, 删除智能组号按钮; 预测页: 打分文字改为权重40+遗漏压力30+维度回补15+日种子15, 模式英文名去掉(热号hot→热号), 单击复制改为复制全部号码; 顺序: 统计分析页调整至最后
总监补充分析(查盘结论): ①单击复制=ball() 的 copy:true→data-copy 单号复制, 全局click代理; 改法=ball() 加 copyAll 选项(data-copyall 属性), 全局代理优先拦截→按页取 PK_LAST/PD_LAST 全集复制 ②智能组号是整卡(推荐池+生成6+1+复制组号)非单按钮→整卡删+死代码清理(genPick/PK_SET/pk-gen/pk-set/pk-note/pk-copy-set/mockApi /api/pick, 防 $() 空引用运行时报错) ③清空按钮内联 4px10px/12px 迷你号→9px18px/13.5px+加粗 ④模式select只改显示文字, value(composite/hot/cold/omission)不动=不影响后端 ⑤导航 data-page 共6处唯一, stats 行挪至末位; LOADERS 映射与顺序无关 ⑥预测页 pred-card 大球原本不可点, 一并接 copyAll(统一"单击球=复制全部")
