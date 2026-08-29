#!/bin/bash
# BATCH-015 线上验证
for H in "45.202.246.39" "10.5.0.2:8787"; do
  curl -s -m 8 "http://$H/" -o /tmp/v.html
  echo "[$H] md5=$(md5sum /tmp/v.html | cut -c1-8)"
  echo "  data-theme覆盖块: $(grep -c 'html\[data-theme=dark\]' /tmp/v.html) | 主题按钮: $(grep -c 'theme-toggle' /tmp/v.html) | 防闪色: $(grep -c 'mcjc-theme' /tmp/v.html) | applyTheme: $(grep -c 'applyTheme' /tmp/v.html)"
  echo "  玻璃blur: $(grep -c 'backdrop-filter' /tmp/v.html) 处 | var()引用: $(grep -o 'var(--' /tmp/v.html | wc -l) 处"
done
echo "双实例一致: $(cmp -s /tmp/v.html /tmp/v.html && echo SAME)"