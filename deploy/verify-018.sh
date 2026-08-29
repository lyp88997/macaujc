#!/bin/bash
# BATCH-018 线上验证
for H in "45.202.246.39" "10.5.0.2:8787"; do
  curl -s -m 8 "http://$H/" -o /tmp/v.html
  echo "[$H] md5=$(md5sum /tmp/v.html | cut -c1-8)"
  echo "  wx-chip: $(grep -c 'wx-chip' /tmp/v.html)"
  echo "  桌面48px: $(grep -c 'clamp(36px,3vw,48px)' /tmp/v.html)"
  echo "  手机加大: $(grep -c 'clamp(26px,7.3vw,32px)' /tmp/v.html)"
  echo "  两列表头: $(grep -c '右侧为特码五行' /tmp/v.html)"
  echo "  手机居中: $(grep -c '#dr-body td{text-align:center' /tmp/v.html)"
  echo "  旧三列残留: $(grep -c '<th>特码五行</th>' /tmp/v.html)"
done