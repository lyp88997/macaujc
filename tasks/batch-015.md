# BATCH-015 依赖链(Predictor)

BATCH-015 依赖链: TASK-AB(双主题CSS变量重构+玻璃效果+主题切换默认浅色) → TASK-AC(双实例部署+验证, 串行)
并行判定: AB/AC 同文件(web/index.html)/部署依赖 => 总监直做
需求(用户原话): 主题调整, 增加玻璃效果, 深色浅色可切换, 默认浅色
总监补充分析(用户描述补全): 现状=深色科技感蓝紫霓虹+色值硬编码→重构 CSS 变量(:root 浅色默认 + html[data-theme=dark] 深色覆盖); 玻璃=卡片/导航半透明+backdrop-filter blur+高光边框; 切换=头部🌙/☀️按钮+localStorage 记忆+首屏内联脚本防闪色; 球色 w-red/blue/green 与🔥语义色双主题通用保持固定; 硬红线: 标注完整词规格+波色映射链不许回归; 手机 16 Pro Max 核心验收
