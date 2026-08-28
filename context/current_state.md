# 当前状态(Predictor 项目)

## 2026-08-28 波色双重映射 bug 修复: ✅ 双实例+GitHub 已同步(585e0da)
- 根因: waveClassOf 把中文色名→CSS类后又传给 ball() 二次查表→undefined→灰球兜底
- 修复: waveClassOf=n=>NUM_WAVE[+n]||null (直取中文色名, 交 ball() 统一映射)
- 实测: 修复前49/49全灰→修复后 红17/蓝16/绿16 零灰; 前后端波色逐号对照一致
- 双实例 md5 一致(adccdd8b), 2291 期, 旧bug特征0
