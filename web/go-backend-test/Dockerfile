# ──────────────────────────────────────────────
# 阶段一：构建
# ──────────────────────────────────────────────
FROM golang:1.25-alpine AS builder

# 安装构建依赖（gcc 用于 cgo，git 用于拉取依赖）
RUN apk add --no-cache gcc musl-dev git

WORKDIR /build

# 先只复制依赖文件，利用 Docker 缓存层
# 只要 go.mod/go.sum 不变，下次构建直接用缓存，不重新下载依赖
COPY go.mod go.sum ./

# 配置 GOPROXY 使用国内镜像，加速依赖下载
RUN go env -w GOPROXY=https://goproxy.cn,direct && \
    go mod download

# 复制全部源码
COPY . .

# 编译：
#   CGO_ENABLED=0  禁用 cgo，产出纯静态二进制
#   -ldflags="-w -s"  去掉调试信息和符号表，减小体积
#   -o /app/server  输出到 /app/server
RUN CGO_ENABLED=0 GOOS=linux go build \
    -ldflags="-w -s" \
    -o /app/server \
    .

# ──────────────────────────────────────────────
# 阶段二：运行
# 用 alpine 而不是 scratch，方便 curl 健康检查和 shell 调试
# ──────────────────────────────────────────────
FROM alpine:3.20 AS runner

# 安装运行时依赖
#   ca-certificates  HTTPS 请求（发邮件、调外部 API）必需
#   curl             健康检查
#   tzdata           时区支持（北京时间）
#   haveged          熵守护进程：防止 alpine 容器内 crypto/rand 因熵不足而阻塞
#                    （RSA 2048 密钥生成需要大量随机熵）
RUN apk add --no-cache ca-certificates curl tzdata haveged su-exec && \
    cp /usr/share/zoneinfo/Asia/Shanghai /etc/localtime && \
    echo "Asia/Shanghai" > /etc/timezone

# 创建非 root 用户
RUN addgroup -S appgroup && adduser -S appuser -G appgroup

WORKDIR /app

COPY --from=builder /app/server .
RUN mkdir -p /app/logs && chown -R appuser:appgroup /app

COPY docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

# 不在此处切换用户，由 entrypoint 在启动 haveged(root) 后 su-exec 到 appuser
# USER appuser

# 对应 Python 版本的 MONGO_URI 默认值格式
ENV PORT=:5000
ENV ENV=production
ENV MONGODB_URI=mongodb://REDACTED_MONGO_USER:REDACTED_MONGO_PASSWORD@mongodb:27017/REDACTED_MONGO_USER?authSource=admin

EXPOSE 5000

# 健康检查，对应 Python 版本的 /api/health
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:5000/api/health || exit 1

ENTRYPOINT ["docker-entrypoint.sh"]
CMD ["/app/server"]

