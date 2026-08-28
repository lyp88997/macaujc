# BATCH-011 依赖链(Predictor)

BATCH-011 依赖链: TASK-T(akile-macau 服务器勘察+部署+服务化) → TASK-U(外网可达性验证, 串行)
并行判定: T/U 串行依赖 => 总监直做
需求(用户原话): 把项目部署到 Akile-澳门-🇲🇴 服务器
要点: SSH 走 localhost aliases akile-macau; 后端 stdlib-only 任意 py3 可跑; 端口沿用 8787; 服务化(systemd 优先, 无则 nohup); 防火墙/安全组是外部变量须实测
