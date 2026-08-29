#!/bin/bash
# BATCH-020 线上验证
for H in "45.202.246.39" "10.5.0.2:8787"; do
  curl -s -m 8 "http://$H/" -o /tmp/v.html
  echo "[$H] md5=$(md5sum /tmp/v.html | cut -c1-8)"
  echo "  品牌渐变: $(grep -c 'brand-name' /tmp/v.html) | 新澳六合: $(grep -c '新澳六合' /tmp/v.html) | 页脚: $(grep -c 'site-foot' /tmp/v.html) | 平歌歌: $(grep -c '平歌歌' /tmp/v.html) | seq: $(grep -c 'class=\"seq\"' /tmp/v.html) | 1s轮询: $(grep -c '},1000);' /tmp/v.html) | 超时块: $(grep -c '12\*60\*1000' /tmp/v.html)"
done
echo "---"
echo "容器API版本: $(curl -s -m 8 http://10.5.0.2:8787/api/status | head -c 120)"
echo "澳门API版本: $(curl -s -m 8 http://45.202.246.39/api/status | head -c 120)"
