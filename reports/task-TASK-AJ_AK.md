# TASK-AJ/AK 报告(BATCH-019, 总监直做)

## TASK-AJ: 特码生肖中心线+电脑端左靠 DONE
- 根因1: 特码球 clamp(36,3vw,48) 大于平码 (33,2.7vw,42), 球列顶对齐→特码生肖字被顶低
- 修法: 桌面/手机特码球 clamp 全部对齐平码(33/2.7/42 + 24/6.8/29), 金圈高亮保留→生肖行齐平
- 根因2: .his-row 桌面 justify-content:center→球行在格内居中, 离期号列远
- 修法: 桌面改 flex-start 左靠期号; 手机520档补 justify-content:center(018居中需求不回退)
- CHANGES: web/index.html 4刀(CSS only); 部署 edit-019.py/verify-019.sh

## TASK-AK: 部署+验证 DONE
- 双实例 md5 一致 734dc40d; 特征5项全命中; 旧48px残留0
- JS两块语法OK; CSS配平176:176; 数据2292期/2026240
- GitHub c8daa13
