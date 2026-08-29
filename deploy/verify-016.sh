#!/bin/bash
# BATCH-016 线上验证
for H in "45.202.246.39" "10.5.0.2:8787"; do
  curl -s -m 8 "http://$H/" -o /tmp/v.html
  echo "[$H] md5=$(md5sum /tmp/v.html | cut -c1-8)"
  echo "  copyall特征: $(grep -c 'data-copyall' /tmp/v.html) | copyAll:true: $(grep -c 'copyAll:true' /tmp/v.html)"
  echo "  智能组号残留: $(grep -c '智能组号' /tmp/v.html) | pk-gen残留: $(grep -c 'pk-gen' /tmp/v.html)"
  echo "  权重40文案: $(grep -c '权重40' /tmp/v.html) | 英文模式残留: $(grep -cE '(综合 composite|热号 hot|冷号 cold|遗漏 omission)' /tmp/v.html)"
  echo "  导航顺序: $(grep -o 'data-page="[a-z]*"' /tmp/v.html | tr '\n' ' ')"
done
echo "双实例一致: $(curl -s -m 8 http://45.202.246.39/ | cmp -s - <(curl -s -m 8 http://10.5.0.2:8787/) && echo YES || echo NO)"