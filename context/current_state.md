# 当前状态(Predictor 项目)

## 2026-08-28 Akile 澳门部署完成: ✅ http://45.202.246.39 (端口80)
- systemd: macaujc.service, enable --now, Restart=always, /opt/macaujc
- 部署方式: tar-over-ssh(本机无 rsync); 1Panel 防火墙白名单模式, 80 在白名单
- 三地实测: 本机 200/7ms + 法兰克福 OPEN + 本机 API ok; 2291 期完整
- GitHub 已同步(bdf593c): deploy/akile-macau.service 入库
- 旧容器版继续跑 http://10.5.0.2:8787
