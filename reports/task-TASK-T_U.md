# TASK-T/U 报告(BATCH-011, 总监直做)

## TASK-T: Akile澳门部署 DONE
- 勘察: Debian 13 / Python 3.13 / systemd / 967MB 内存 / 双栈(IPv4 45.202.246.39 + IPv6)
- 上传: tar-over-ssh 全项目 480K → /opt/macaujc(本机无 rsync)
- 服务化: systemd 单元 /etc/systemd/system/macaujc.service, enable --now, Restart=always
- 端口波折: 初始 8787 外网被拦 → 定位 1PANEL_BASIC_AFTER 全局 DROP 兜底(白名单模式) →
  白名单内 80 空闲 → 改监听 80 → 外网即通
- 数据: 采集线程自动跑满 2291 期(2026239), 与容器版完全一致

## TASK-U: 外网验证 DONE
- 本机→公网 IPv4: HTTP 200 / 7ms, 标题 MACAUJC·号码分析台
- 法兰克福独立网络: TCP 80 OPEN
- 服务器本机: 127.0.0.1:80 API ok, 期数/期号正确
- systemd 单元已收编仓库 deploy/akile-macau.service 并推送 GitHub(bdf593c)

## 遗留
- 无。IPv6 外网未单独实测(本机无 v6 路由), 服务器 ip6tables 无 DROP, 理论可达
