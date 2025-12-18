# 构建阶段
FROM golang:1.21-alpine AS builder

WORKDIR /app

# 安装必要的构建工具
RUN apk add --no-cache git ca-certificates tzdata

# 设置Go代理
ENV GOPROXY=https://goproxy.cn,direct

# 复制go.mod (go.sum可能不存在)
COPY go.mod ./
RUN go mod download || true

# 复制源代码
COPY . .

# 下载依赖并构建应用
RUN go mod tidy && CGO_ENABLED=0 GOOS=linux go build -a -installsuffix cgo -o main .

# 运行阶段
FROM alpine:latest

WORKDIR /app

# 安装必要的运行时依赖
RUN apk --no-cache add ca-certificates tzdata wget

# 设置时区
ENV TZ=Asia/Shanghai

# 从构建阶段复制二进制文件
COPY --from=builder /app/main .
COPY --from=builder /app/docker-entrypoint.sh .

# 创建日志目录
RUN mkdir -p /app/logs && chmod +x /app/docker-entrypoint.sh

# 暴露端口
EXPOSE 5000

# 运行应用
ENTRYPOINT ["./docker-entrypoint.sh"]
