#!/bin/bash
# BATCH-017 线上验证
for H in "45.202.246.39" "10.5.0.2:8787"; do
  curl -s -m 8 "http://$H/" -o /tmp/v.html
  echo "[$H] md5=$(md5sum /tmp/v.html | cut -c1-8)"
  echo "  MODE_TXT: $(grep -c 'MODE_TXT' /tmp/v.html) 处"
  echo "  窗口期摘要: $(grep -c '窗口 ${r.window}期' /tmp/v.html) 处"
  echo "  option带期: $(grep -c '>50期<' /tmp/v.html) 处"
  echo "  桌面缩放CSS: $(grep -c 'his-row .ball{width:clamp' /tmp/v.html) 处"
  echo "  手机缩小CSS: $(grep -c 'his-row .ball{width:clamp(22px' /tmp/v.html) 处"
  echo "  残留window英文: $(grep -c 'window ${' /tmp/v.html) 处"
  echo "  数据期数: $(curl -s -m 8 "http://$H/api/status" | python3 -c 'import json,sys; d=json.load(sys.stdin); print(d.get("total_draws","?"), "期 /", d.get("last_expect","?"))' 2>/dev/null)"
done