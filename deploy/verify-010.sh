#!/usr/bin/env bash
L=$(curl -s -m 8 http://10.5.0.2:8787/)
echo "seq徽标数: $(echo "$L" | grep -o 'class="seq"' | wc -l)"
echo "按钮特征: $(echo "$L" | grep -c 'pd-copy-btn\|#pd-combo-card h3\|flex:1;justify-content:center;padding:12px 0')"
echo "seq顺序: $(echo "$L" | grep -o '<i class="seq">[0-9]</i>' | grep -o '[0-9]' | tr -d '\n')"
curl -s -m 8 http://10.5.0.2:8787/api/status | grep -o '"total_draws":[0-9]*'
