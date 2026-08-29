#!/bin/bash
# BATCH-014 线上验证
for H in "45.202.246.39" "10.5.0.2:8787"; do
  curl -s -m 8 "http://$H/" -o /tmp/v.html
  echo "[$H] md5=$(md5sum /tmp/v.html | cut -c1-8)"
  echo "  完整词统计: $(grep -c '出现${it.count}次 · 频率' /tmp/v.html) 处"
  echo "  完整词遗漏: $(grep -c '当前遗漏${r.omission} · 平均遗漏' /tmp/v.html) 处"
  echo "  缩写残留: $(grep -c '· 遗${it.omission}\|均${r.avg_omission}' /tmp/v.html) 处"
  echo "  统计球波色: $(grep -c 'ball sm ${WAVE\[waveClassOf(it.key)\]' /tmp/v.html) 处"
  echo "  两行结构: $(grep -c 'om-main' /tmp/v.html) 处"
done
cmp -s /dev/null /dev/null 2>/dev/null
curl -s -m 8 "http://45.202.246.39/" -o /tmp/m.html; curl -s -m 8 "http://10.5.0.2:8787/" -o /tmp/c.html
echo "双实例一致: $(cmp -s /tmp/m.html /tmp/c.html && echo YES || echo NO)"
curl -s -m 8 "http://45.202.246.39/api/status" | head -c 120; echo