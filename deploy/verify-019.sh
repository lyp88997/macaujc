#!/bin/bash
# BATCH-019 线上验证
for H in "45.202.246.39" "10.5.0.2:8787"; do
  curl -s -m 8 "http://$H/" -o /tmp/v.html
  echo "[$H] md5=$(md5sum /tmp/v.html | cut -c1-8)"
  echo "  桌面flex-start: $(grep -c 'his-row{display:flex;flex-wrap:wrap;justify-content:flex-start' /tmp/v.html)"
  echo "  手机center: $(grep -c 'his-row{flex-wrap:nowrap;gap:1.2vw;justify-content:center' /tmp/v.html)"
  echo "  桌面特码=平码(33,2.7,42)出现2次: $(grep -oc 'clamp(33px,2.7vw,42px)' /tmp/v.html)"
  echo "  手机特码=平码(24,6.8,29)出现2次: $(grep -oc 'clamp(24px,6.8vw,29px)' /tmp/v.html)"
  echo "  旧48px特码残留: $(grep -c 'clamp(36px,3vw,48px)' /tmp/v.html)"
done