#!/bin/sh
# Go 后端容器启动脚本
# 对应 Python 版本的 docker-entrypoint.sh

set -e

echo "======================================"
echo "北化课程提醒系统 (Go) 启动中..."
echo "======================================"

# 创建日志目录（以防挂载卷未自动创建）
mkdir -p /app/logs

# ── 等待 MongoDB 就绪 ──
# 对应 Python 版本的数据库连接等待逻辑
MONGO_HOST=$(echo "${MONGODB_URI:-mongodb://mongodb:27017}" | sed 's|.*@\([^:/]*\).*|\1|' | sed 's|.*://\([^:/]*\).*|\1|')
MONGO_PORT=27017

echo "等待 MongoDB ($MONGO_HOST:$MONGO_PORT) 就绪..."
MAX_TRIES=30
i=0
while [ $i -lt $MAX_TRIES ]; do
    if nc -z "$MONGO_HOST" "$MONGO_PORT" 2>/dev/null; then
        echo "✅ MongoDB 已就绪!"
        break
    fi
    i=$((i + 1))
    echo "  等待中... ($i/$MAX_TRIES)"
    sleep 2
done

if [ $i -eq $MAX_TRIES ]; then
    echo "❌ 错误: MongoDB 未能在规定时间内启动"
    exit 1
fi

# ── 打印运行时配置（不打印敏感信息）──
echo "--------------------------------------"
echo "运行环境:    ${ENV:-production}"
echo "监听端口:    ${PORT:-:8080}"
echo "MongoDB:     ${MONGO_HOST}:${MONGO_PORT}"
echo "邮件服务:    ${MAIL_SENDER:-未配置}"
echo "邮件可用:    $([ -n "$MAIL_PASSWORD" ] && echo '是' || echo '否（未设置 MAIL_PASSWORD）')"
echo "--------------------------------------"

echo "======================================"
echo "✅ 系统启动完成!"
echo "   应用端口: ${PORT:-:5000}"
echo "======================================"

# 以 root 启动 haveged 补充熵（后台运行）
# Go 的 crypto/rand 在低熵容器环境下会阻塞，RSA 密钥生成尤其明显
if command -v haveged >/dev/null 2>&1; then
    haveged -w 1024 -v 0
    echo "✅ haveged 已启动（熵池补充中）"
fi

# 切换到非 root 用户运行 server（su-exec 是 alpine 的 gosu 等价物）
# 若第一个参数已经是完整命令（如 /app/server），直接 su-exec 执行
exec su-exec appuser "$@"

