@echo off
chcp 65001 >nul
echo 💾 开始备份 MongoDB 数据库...

REM 创建备份目录
if not exist "mongodb_backup" mkdir mongodb_backup

REM 获取当前日期时间
for /f "tokens=2 delims==" %%a in ('wmic OS Get localdatetime /value') do set "dt=%%a"
set "YY=%dt:~2,2%" & set "YYYY=%dt:~0,4%" & set "MM=%dt:~4,2%" & set "DD=%dt:~6,2%"
set "HH=%dt:~8,2%" & set "Min=%dt:~10,2%" & set "Sec=%dt:~12,2%"
set "datestamp=%YYYY%-%MM%-%DD%_%HH%-%Min%-%Sec%"

echo 📅 备份时间: %datestamp%

REM 执行备份
docker exec buct-mongodb mongodump --host localhost --port 27017 --username REDACTED_MONGO_USER --password REDACTED_MONGO_PASSWORD --authenticationDatabase admin --db buct-course --out /backup/backup_%datestamp%

if %ERRORLEVEL% EQU 0 (
    echo ✅ 数据库备份成功！
    echo 📁 备份位置: mongodb_backup/backup_%datestamp%
) else (
    echo ❌ 数据库备份失败！
    echo 请检查 MongoDB 容器是否正在运行
)

echo.
echo 💡 提示：定期备份数据库可以防止数据丢失
pause