# TASK-AF/AG 报告(BATCH-017, 总监直做)

## TASK-AF: 预测页中文化+窗口带期+历史页响应式 DONE
- 摘要: `composite · 特码 · window 100 · ...` → `综合模式 · 特码 · 窗口 100期 · ...`(MODE_TXT 四模式映射, 用户示例逐字)
- 连带治: 复制文案 `模式:${p.mode}` → MODE_TXT; 统计页 `(window 100)` → `窗口 100期`
- 窗口选项: 50/100/200(/500) → `50期/100期/200期/500期` 显示, value 保数字(API 参数不受影响)
- 历史页响应式(仅 .his-row 作用域): 桌面球体 clamp(34px,2.6vw,44px)/sm(31~40)/生肖(12.5~16px)/间距(7~14px)/加号(22~30px);
  手机(≤520px) 球体 clamp(22px,6.4vw,28px)/sm(20~26)/生肖(8.5~10.5px)/间距 1.2vw
- 编辑脚本 deploy/edit-017.py 10 刀全中(含 223 行 .plus 后置定义的原位覆盖规避)

## TASK-AG: 部署验证 DONE
- 本地: 两块 script 语法 OK/CSS 配平 172:172/option value 核对/沙盒四模式摘要仿真逐字命中
- 线上: 双实例 md5 一致 e1120796/MODE_TXT 3 处/窗口期摘要 1 处/option带期 2 处/桌面缩放 2 处/手机缩小 1 处/英文 window 残留 0
- 数据: 2292 期/2026240/last_sync 15:06(验证脚本字段名猜错示 ?, 实际 API db.total_draws 正常)
- GitHub: 6d3d737 推送
