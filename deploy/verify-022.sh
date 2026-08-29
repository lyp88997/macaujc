#!/bin/bash
# BATCH-022 线上验证
for H in "45.202.246.39" "10.5.0.2:8787"; do
  curl -s -m 8 "http://$H/" -o /tmp/v.html
  echo "[$H] md5=$(md5sum /tmp/v.html | cut -c1-8)"
  echo "  行1ctl-row: $(grep -c 'ctl-row"><label>模式' /tmp/v.html)"
  echo "  行2ctl-row: $(grep -c '<div class="ctl-row"><label>数量' /tmp/v.html)"
  echo "  手机两行CSS: $(grep -c 'page-predict .controls{flex-direction:column' /tmp/v.html)"
  echo "  按页取数: $(grep -c 'page==="page-predict"?(pd.length?pd:pk)' /tmp/v.html)"
  echo "  旧优先PK残留: $(grep -c 'PK_LAST&&PK_LAST.length?PK_LAST:(PD_LAST' /tmp/v.html)"
  echo "  API: $(curl -s -m 8 http://$H/api/status | head -c 80)"
done