# 部署脚本: 本地构建产物同步到目标机(ssh 别名 localhost-root)并以 Docker 运行
# 用法: bash deploy.sh
set -e
TARGET_HOST=localhost-root
TARGET_DIR=/opt/macaujc-predictor
PROJ=/opt/data/workspace/macaujc-predictor
SSH="ssh -F /opt/data/home/.ssh/config $TARGET_HOST"

echo "[1/5] 预检: 部署机 Docker"
$SSH 'docker version --format "Docker {{.Server.Version}} ✓"'

echo "[2/5] 同步项目文件 → $TARGET_HOST:$TARGET_DIR"
$SSH "mkdir -p $TARGET_DIR"
tar -C $PROJ --exclude='context' --exclude='reports' --exclude='tasks' --exclude='.git' \
  --exclude='__pycache__' --exclude='*.db' -cf - app web rules deploy | \
  $SSH "tar -C $TARGET_DIR -xf -"

echo "[3/5] 构建并启动容器(端口 8787→8000)"
$SSH "cd $TARGET_DIR/deploy && docker compose up -d --build 2>&1 | tail -5"

echo "[4/5] 等待服务就绪"
for i in $(seq 1 45); do
  if $SSH "curl -sf http://127.0.0.1:8787/api/status >/dev/null 2>&1"; then echo "服务已就绪 ✓ (第 ${i} 次探测)"; break; fi
  if [ $i -eq 45 ]; then echo "✗ 90s 内未就绪, 查看日志:"; $SSH "docker logs --tail 40 macaujc-predictor"; exit 1; fi
  sleep 2
done

echo "[5/5] 端到端验证"
$SSH "curl -s http://127.0.0.1:8787/api/status | head -c 300; echo"
echo "完成: http://<宿主机IP>:8787"
