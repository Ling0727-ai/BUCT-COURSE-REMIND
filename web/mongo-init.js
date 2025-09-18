// MongoDB 初始化脚本
// 这个脚本会在 MongoDB 容器首次启动时执行

// 切换到 admin 数据库
db = db.getSiblingDB('admin');

// 创建 root 用户（如果不存在）
try {
    db.createUser({
        user: 'REDACTED_MONGO_USER',
        pwd: 'REDACTED_MONGO_PASSWORD',
        roles: [
            { role: 'root', db: 'admin' }
        ]
    });
    print('Root user created successfully');
} catch (e) {
    print('Root user already exists or error occurred: ' + e);
}

// 切换到应用数据库
db = db.getSiblingDB('buct-course');

// 创建应用数据库用户
try {
    db.createUser({
        user: 'REDACTED_MONGO_USER',
        pwd: 'REDACTED_MONGO_PASSWORD',
        roles: [
            { role: 'readWrite', db: 'buct-course' },
            { role: 'dbAdmin', db: 'buct-course' }
        ]
    });
    print('Application user created successfully');
} catch (e) {
    print('Application user already exists or error occurred: ' + e);
}

// 创建基本集合和索引
try {
    // 用户集合
    db.createCollection('users');
    db.users.createIndex({ "username": 1 }, { unique: true });
    db.users.createIndex({ "email": 1 }, { unique: true });
    
    // 作业集合
    db.createCollection('assignments');
    db.assignments.createIndex({ "due_date": 1 });
    db.assignments.createIndex({ "subject": 1 });
    
    // 测试集合
    db.createCollection('tests');
    db.tests.createIndex({ "start_time": 1 });
    db.tests.createIndex({ "end_time": 1 });
    
    // 设置集合
    db.createCollection('settings');
    db.settings.createIndex({ "key": 1 }, { unique: true });
    
    // 验证码集合（带TTL索引）
    db.createCollection('verification_codes');
    db.verification_codes.createIndex({ "expires_at": 1 }, { expireAfterSeconds: 0 });
    
    // Webhook日志集合
    db.createCollection('webhook_logs');
    db.webhook_logs.createIndex({ "created_at": 1 });
    
    print('Collections and indexes created successfully');
} catch (e) {
    print('Error creating collections or indexes: ' + e);
}

// 插入默认设置
try {
    db.settings.insertMany([
        { key: 'scrape_interval', value: '60', updated_at: new Date() },
        { key: 'serverUrl', value: 'http://localhost:5000', updated_at: new Date() },
        { key: 'webhooks', value: '[]', updated_at: new Date() }
    ]);
    print('Default settings inserted successfully');
} catch (e) {
    print('Error inserting default settings (may already exist): ' + e);
}

print('MongoDB initialization completed');