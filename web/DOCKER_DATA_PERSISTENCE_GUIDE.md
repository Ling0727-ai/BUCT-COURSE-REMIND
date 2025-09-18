# Docker 数据持久化指南

## 🚨 重要：防止数据丢失

### ✅ 正确的操作命令

```bash
# 启动服务
docker-compose up -d

# 停止服务（保留数据）
docker-compose down

# 重启服务
docker-compose restart

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f backend
```

### ❌ 危险的命令（会删除数据）

```bash
# 这些命令会删除所有数据卷，导致数据丢失！
docker-compose down -v
docker-compose down --volumes
docker system prune -a --volumes
```

## 📊 数据卷管理

### 查看数据卷
```bash
# 查看所有卷
docker volume ls

# 查看 MongoDB 数据卷详情
docker volume inspect web_mongodb_data
```

### 备份数据
```bash
# 备份 MongoDB 数据
docker exec -it <mongodb_container_id> mongodump --out /backup
docker cp <mongodb_container_id>:/backup ./mongodb_backup
```

### 恢复数据
```bash
# 恢复 MongoDB 数据
docker cp ./mongodb_backup <mongodb_container_id>:/backup
docker exec -it <mongodb_container_id> mongorestore /backup
```

## 🔧 数据持久化配置

当前配置已经正确设置了数据持久化：

```yaml
services:
  mongodb:
    volumes:
      - mongodb_data:/data/db  # 数据持久化
      
volumes:
  mongodb_data:  # 命名卷，数据会保留
```

## 🛠️ 故障排除

### 如果数据仍然丢失：

1. **检查卷是否存在**
   ```bash
   docker volume ls | grep mongodb_data
   ```

2. **检查容器挂载**
   ```bash
   docker inspect <mongodb_container_id> | grep -A 10 "Mounts"
   ```

3. **检查数据目录**
   ```bash
   docker exec -it <mongodb_container_id> ls -la /data/db
   ```

## 📋 最佳实践

1. **永远不要使用 `-v` 或 `--volumes` 参数**
2. **定期备份重要数据**
3. **使用命名卷而不是匿名卷**
4. **监控卷的使用情况**

## 🔄 安全重启流程

```bash
# 1. 停止服务（保留数据）
docker-compose down

# 2. 确认数据卷存在
docker volume ls | grep mongodb_data

# 3. 重新启动
docker-compose up -d

# 4. 检查服务状态
docker-compose ps

# 5. 检查日志
docker-compose logs -f backend