#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据迁移脚本
将旧的 completed_assignments 和 deleted_assignments 数据迁移到新的 assignment_status 集合
"""

import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.assignment_status import get_assignment_status_manager
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def migrate_completed_assignments(app):
    """迁移已完成作业数据"""
    with app.app_context():
        from app import mongo

        logger.info("开始迁移已完成作业数据...")

        # 获取所有已完成作业记录
        completed_collection = mongo.db['completed_assignments']
        completed_records = list(completed_collection.find())

        if not completed_records:
            logger.info("没有找到已完成作业记录")
            return 0

        # 获取状态管理器
        status_manager = get_assignment_status_manager()

        migrated_count = 0
        for record in completed_records:
            try:
                user_id = record['user_id']
                assignment_id = record['assignment_id']
                assignment_title = record.get('assignment_title', '未知作业')
                assignment_subject = record.get('assignment_subject', '未知科目')

                # 检查是否已经迁移
                existing_status = status_manager.get_assignment_status(user_id, assignment_id)
                if existing_status == 'completed':
                    logger.debug(f"作业 {assignment_id} 已经迁移，跳过")
                    continue

                # 迁移到新系统
                result = status_manager.mark_completed(user_id, assignment_id, assignment_title, assignment_subject)
                if result:
                    migrated_count += 1
                    logger.debug(f"迁移已完成作业: {assignment_id}")

            except Exception as e:
                logger.error(f"迁移已完成作业记录失败: {record.get('assignment_id', 'unknown')}, 错误: {e}")

        logger.info(f"已完成作业迁移完成，共迁移 {migrated_count} 条记录")
        return migrated_count


def migrate_deleted_assignments(app):
    """迁移已删除作业数据"""
    with app.app_context():
        from app import mongo

        logger.info("开始迁移已删除作业数据...")

        # 获取所有已删除作业记录
        deleted_collection = mongo.db['deleted_assignments']
        deleted_records = list(deleted_collection.find())

        if not deleted_records:
            logger.info("没有找到已删除作业记录")
            return 0

        # 获取状态管理器
        status_manager = get_assignment_status_manager()

        migrated_count = 0
        for record in deleted_records:
            try:
                user_id = record['user_id']
                assignment_id = record['assignment_id']
                assignment_title = record.get('assignment_title', '未知作业')
                assignment_subject = record.get('assignment_subject', '未知科目')

                # 检查是否已经迁移
                existing_status = status_manager.get_assignment_status(user_id, assignment_id)
                if existing_status == 'deleted':
                    logger.debug(f"作业 {assignment_id} 已经迁移，跳过")
                    continue

                # 迁移到新系统
                result = status_manager.mark_deleted(user_id, assignment_id, assignment_title, assignment_subject)
                if result:
                    migrated_count += 1
                    logger.debug(f"迁移已删除作业: {assignment_id}")

            except Exception as e:
                logger.error(f"迁移已删除作业记录失败: {record.get('assignment_id', 'unknown')}, 错误: {e}")

        logger.info(f"已删除作业迁移完成，共迁移 {migrated_count} 条记录")
        return migrated_count


def cleanup_old_collections(app, confirm=False):
    """清理旧的集合（可选）"""
    if not confirm:
        logger.warning("清理旧集合需要确认，请使用 --cleanup 参数")
        return

    with app.app_context():
        from app import mongo

        logger.info("开始清理旧集合...")

        # 重命名旧集合作为备份
        try:
            mongo.db['completed_assignments'].rename('completed_assignments_backup')
            logger.info("已将 completed_assignments 重命名为 completed_assignments_backup")
        except Exception as e:
            logger.warning(f"重命名 completed_assignments 失败: {e}")

        try:
            mongo.db['deleted_assignments'].rename('deleted_assignments_backup')
            logger.info("已将 deleted_assignments 重命名为 deleted_assignments_backup")
        except Exception as e:
            logger.warning(f"重命名 deleted_assignments 失败: {e}")


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description='数据迁移脚本')
    parser.add_argument('--cleanup', action='store_true', help='清理旧集合（重命名为备份）')
    parser.add_argument('--dry-run', action='store_true', help='试运行，不实际执行迁移')

    args = parser.parse_args()

    if args.dry_run:
        logger.info("试运行模式，不会实际执行迁移")
        return

    # 创建应用实例
    app = create_app()

    try:
        # 执行迁移
        completed_count = migrate_completed_assignments(app)
        deleted_count = migrate_deleted_assignments(app)

        logger.info(f"迁移完成！已完成作业: {completed_count} 条，已删除作业: {deleted_count} 条")

        # 可选清理
        if args.cleanup:
            cleanup_old_collections(app, confirm=True)

        logger.info("数据迁移脚本执行完成")

    except Exception as e:
        logger.error(f"迁移过程中发生错误: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
