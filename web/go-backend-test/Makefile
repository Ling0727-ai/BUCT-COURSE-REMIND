.PHONY: help build run clean test fmt lint dep

# 变量定义
BINARY_NAME=go-backend
OUTPUT_DIR=dist
MAIN_FILE=main.go

# 帮助信息
help:
	@echo "BUCT Course Remind - Go Backend"
	@echo ""
	@echo "可用命令:"
	@echo "  make build       - 构建二进制文件"
	@echo "  make run         - 运行应用"
	@echo "  make clean       - 清理生成的文件"
	@echo "  make test        - 运行测试"
	@echo "  make fmt         - 格式化代码"
	@echo "  make lint        - 代码质量检查"
	@echo "  make dep         - 管理依赖"
	@echo "  make dev         - 开发模式（热重载）"
	@echo ""

# 安装依赖
dep:
	go mod download
	go mod tidy
	@echo "✓ 依赖安装完成"

# 构建二进制文件
build: clean
	@echo "开始构建..."
	@mkdir -p $(OUTPUT_DIR)
	go build -o $(OUTPUT_DIR)/$(BINARY_NAME).exe $(MAIN_FILE)
	@echo "✓ 构建完成: $(OUTPUT_DIR)/$(BINARY_NAME).exe"

# 运行应用
run:
	@echo "启动应用..."
	go run $(MAIN_FILE)

# 开发模式（需要安装 air: go install github.com/cosmtrek/air@latest）
dev:
	@command -v air >/dev/null 2>&1 || (echo "请先安装 air: go install github.com/cosmtrek/air@latest" && exit 1)
	air

# 清理生成的文件
clean:
	@echo "清理文件..."
	@if exist $(OUTPUT_DIR) rmdir /s /q $(OUTPUT_DIR)
	go clean
	@echo "✓ 清理完成"

# 运行测试
test:
	@echo "运行测试..."
	go test -v -coverprofile=coverage.out ./...
	go tool cover -html=coverage.out -o coverage.html
	@echo "✓ 测试完成，覆盖率报告: coverage.html"

# 代码格式化
fmt:
	@echo "格式化代码..."
	go fmt ./...
	@echo "✓ 格式化完成"

# 代码质量检查（需要 golangci-lint）
lint:
	@command -v golangci-lint >/dev/null 2>&1 || (echo "请先安装: go install github.com/golangci/golangci-lint/cmd/golangci-lint@latest" && exit 1)
	@echo "执行代码检查..."
	golangci-lint run ./...
	@echo "✓ 检查完成"

# 生成文档
docs:
	@echo "生成API文档..."
	@echo "TODO: 集成 swag 生成 Swagger 文档"

# 完整的开发流程
all: dep fmt test build
	@echo "✓ 所有任务完成"

# 显示当前配置
version:
	@echo "Go版本:"
	@go version
	@echo ""
	@echo "项目配置:"
	@cat go.mod | grep "go "

