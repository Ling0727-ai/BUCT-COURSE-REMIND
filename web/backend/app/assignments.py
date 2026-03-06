"""
作业管理模块
提供作业的CRUD操作和状态管理
使用统一的状态管理系统
"""

import logging
from datetime import datetime, timedelta

from bson import ObjectId
from flask import Blueprint, request, jsonify, session

from . import mongo
from .auth import login_required

# 创建蓝图
assignments_bp = Blueprint('assignments', __name__, url_prefix='/api/assignments')

# 配置日志
logger = logging.getLogger(__name__)


def get_scraper_instance():
    """获取scraper实例"""
    try:
        # 导入新版scraper
        from .scraper import get_scraper
        return get_scraper()
    except ImportError as e:
        logger.error(f"导入scraper失败: {e}")
        return None
    except Exception as e:
        logger.error(f"获取scraper实例失败: {e}")
        return None


@assignments_bp.route('/standard', methods=['GET'])
@login_required
def get_standard_assignments():
    """获取标准作业列表（从数据库获取）"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'success': False, 'error': '用户未登录'}), 401

        logger.info(f"用户 {user_id} 请求获取作业列表")

        # 从数据库获取数据
        from .course_data import get_course_data_manager
        course_data_mgr = get_course_data_manager()
        tasks = course_data_mgr.get_user_course_data(user_id)

        # 获取作业状态信息
        from .assignment_status import get_assignment_status_manager
        status_manager = get_assignment_status_manager()
        completed_ids = status_manager.get_completed_assignment_ids(user_id)
        deleted_ids = status_manager.get_deleted_assignment_ids(user_id)
        completed_set = set(str(aid) for aid in completed_ids)
        deleted_set = set(str(aid) for aid in deleted_ids)

        # 获取黑名单 courseId set
        from .blacklist import get_user_blacklisted_ids, extract_course_id
        blacklisted_set = set(get_user_blacklisted_ids(user_id))

        # 转换数据格式（过滤掉已删除的任务）
        formatted_tasks = []
        homework_count = 0
        test_count = 0

        for task in tasks:
            task_id = task.get('task_id')
            task_type = task.get('type', 'homework')

            # 跳过已删除的任务
            if task_id in deleted_set:
                continue

            # 跳过黑名单科目（通过 URL 提取 courseId 判断）
            task_url = task.get('url', '')
            course_id = extract_course_id(task_url)
            if course_id and course_id in blacklisted_set:
                continue

            formatted_task = {
                'id': task_id,
                'subject': task.get('subject', ''),
                'type': task_type,
                'details': {
                    'task': task.get('title', ''),
                    'deadline': task.get('deadline', ''),
                    'url': task.get('url', ''),
                    'can_submit': True,
                    'is_group': False,
                    'details_content': task.get('details', '')
                },
                'completed': task_id in completed_set,
                'has_tasks': True,
                'tasks_count': 1
            }
            formatted_tasks.append(formatted_task)

            if task_type == 'homework':
                homework_count += 1
            else:
                test_count += 1

        stats = {
            'homework_count': homework_count,
            'tests_count': test_count,
            'total_count': len(formatted_tasks)
        }

        logger.info(f"从数据库为用户 {user_id} 返回 {len(formatted_tasks)} 个作业/测试项目")

        return jsonify({
            'success': True,
            'tasks': formatted_tasks,
            'total': len(formatted_tasks),
            'stats': stats,
            'source': 'database'
        })

    except Exception as e:
        logger.error(f"获取作业列表失败: {str(e)}")
        return jsonify({'success': False, 'error': '获取作业列表失败'}), 500


@assignments_bp.route('/<assignment_id>/complete', methods=['POST'])
@login_required
def mark_assignment_complete(assignment_id):
    """标记作业为已完成"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'success': False, 'error': '用户未登录'}), 401

        logger.info(f"用户 {user_id} 标记作业 {assignment_id} 为已完成")

        # 从前端请求中获取作业信息
        data = request.get_json() or {}
        assignment_title = data.get('title', '未知作业')
        assignment_subject = data.get('subject', '未知科目')

        # 使用统一状态管理标记为已完成
        from .assignment_status import get_assignment_status_manager
        status_manager = get_assignment_status_manager()
        result = status_manager.mark_completed(user_id, assignment_id, assignment_title, assignment_subject)

        if result:
            logger.info(f"作业 {assignment_id} 标记完成成功")
            return jsonify({'success': True, 'message': '作业已标记为完成'})
        else:
            return jsonify({'success': False, 'error': '标记失败，可能已经完成'}), 400

    except Exception as e:
        logger.error(f"标记作业完成失败: {str(e)}")
        return jsonify({'success': False, 'error': '标记完成失败'}), 500


@assignments_bp.route('/<assignment_id>/uncomplete', methods=['POST'])
@login_required
def mark_assignment_uncomplete(assignment_id):
    """撤销作业完成状态"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'success': False, 'error': '用户未登录'}), 401

        logger.info(f"用户 {user_id} 撤销作业 {assignment_id} 的完成状态")

        # 使用统一状态管理撤销完成状态
        from .assignment_status import get_assignment_status_manager
        status_manager = get_assignment_status_manager()
        result = status_manager.restore_assignment(user_id, assignment_id)

        if result:
            logger.info(f"作业 {assignment_id} 撤销完成成功")
            return jsonify({'success': True, 'message': '已撤销完成状态'})
        else:
            return jsonify({'success': False, 'error': '撤销失败，可能未完成'}), 400

    except Exception as e:
        logger.error(f"撤销作业完成失败: {str(e)}")
        return jsonify({'success': False, 'error': '撤销失败'}), 500


@assignments_bp.route('/<assignment_id>/remind', methods=['POST'])
@login_required
def remind_assignment(assignment_id):
    """提醒作业 - 支持多种提醒方式"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'success': False, 'error': '用户未登录'}), 401

        logger.info(f"用户 {user_id} 提醒作业: {assignment_id}")

        # 检查作业是否已完成或已删除
        from .assignment_status import get_assignment_status_manager
        status_manager = get_assignment_status_manager()

        # 检查是否已完成
        completed_ids = status_manager.get_completed_assignment_ids(user_id)
        if assignment_id in [str(aid) for aid in completed_ids]:
            logger.warning(f"作业 {assignment_id} 已完成，不发送提醒")
            return jsonify({
                'success': False,
                'error': '该作业已完成，无需提醒'
            }), 400

        # 检查是否已删除
        deleted_ids = status_manager.get_deleted_assignment_ids(user_id)
        if assignment_id in [str(aid) for aid in deleted_ids]:
            logger.warning(f"作业 {assignment_id} 已删除，不发送提醒")
            return jsonify({
                'success': False,
                'error': '该作业已删除，无法提醒'
            }), 400

        # 从数据库查询作业信息（更准确、更安全）
        assignment_doc = mongo.db.course_data.find_one({
            'user_id': ObjectId(user_id),
            'task_id': assignment_id
        })

        if not assignment_doc:
            logger.warning(f"作业 {assignment_id} 不存在于数据库中")
            return jsonify({
                'success': False,
                'error': '作业不存在'
            }), 404

        # 从数据库文档中提取作业信息
        subject = assignment_doc.get('subject', '未知科目')
        task = assignment_doc.get('title', '未知任务')
        deadline = assignment_doc.get('deadline', '')
        task_type = assignment_doc.get('type', 'homework')
        assignment_type = '作业' if task_type == 'homework' else '测试'

        # 从请求中获取提醒配置
        data = request.get_json() or {}
        reminder_config = data.get('reminderConfig', {})

        # 解析截止时间（字符串 -> datetime），默认使用北京时间
        due_dt = None
        deadline_display = ''
        try:
            if deadline:
                if 'T' in deadline and ('Z' in deadline or '+' in deadline):
                    due_dt = datetime.fromisoformat(deadline.replace('Z', '+00:00'))
                elif 'T' in deadline:
                    # 无时区信息，按北京时间处理
                    due_dt = datetime.fromisoformat(deadline)
                else:
                    # 非ISO（兼容），尝试直接解析
                    due_dt = datetime.fromisoformat(deadline)
                deadline_display = due_dt.strftime('%Y年%m月%d日 %H:%M:%S') if due_dt else ''
        except Exception:
            # 保持原样显示
            deadline_display = deadline

        # 读取用户邮箱
        from .model import get_beijing_time
        user = mongo.db.users.find_one({'_id': ObjectId(user_id)})
        if not user or not user.get('email'):
            return jsonify({'success': False, 'error': '未找到用户邮箱，请在设置中配置邮箱'}), 400
        to_email = user['email']

        # 生成提醒消息
        base_message = f"⚠️ {assignment_type}提醒\n\n科目: {subject}\n标题: {task}\n截止时间: {deadline_display if deadline_display else '未知'}"

        # 计算计划发送时间 scheduled_time（北京时间的naive datetime）
        now = get_beijing_time()
        scheduled_time = now
        schedule_desc = '立即'

        rtype = reminder_config.get('type', 'instant')
        if rtype == 'instant':
            scheduled_time = now
            schedule_desc = '立即'
        elif rtype in ['1h', '3h', '6h', '12h'] or ('hours' in reminder_config):
            # 获取时间参数
            hours = reminder_config.get('hours')
            timing = reminder_config.get('timing', 'before')  # 默认为'before'

            if hours is None:
                preset = {'1h': 1, '3h': 3, '6h': 6, '12h': 12}
                hours = preset.get(rtype, 1)
            try:
                hours = float(hours)
            except Exception:
                hours = 1.0

            # 根据timing判断是"截止前"还是"从现在起"
            if timing == 'after':
                # 从现在起N小时后
                scheduled_time = now + timedelta(hours=hours)
                schedule_desc = f"{int(hours) if hours.is_integer() else hours}小时后"
            else:
                # 截止时间前N小时（默认行为）
                if due_dt:
                    scheduled_time = due_dt - timedelta(hours=hours)
                    schedule_desc = f"截止前{int(hours) if hours.is_integer() else hours}小时"
                else:
                    # 如果没有截止时间，改为从现在起N小时后
                    scheduled_time = now + timedelta(hours=hours)
                    schedule_desc = f"{int(hours) if hours.is_integer() else hours}小时后"
        elif rtype in ['custom-hours-before', 'custom-hours-after']:
            # 处理新的自定义小时前/后选项
            hours = reminder_config.get('hours', 1)
            try:
                hours = float(hours)
            except Exception:
                hours = 1.0

            if rtype == 'custom-hours-after':
                # 从现在起N小时后
                scheduled_time = now + timedelta(hours=hours)
                schedule_desc = f"{int(hours) if hours.is_integer() else hours}小时后"
            else:
                # 截止时间前N小时
                if due_dt:
                    scheduled_time = due_dt - timedelta(hours=hours)
                    schedule_desc = f"截止前{int(hours) if hours.is_integer() else hours}小时"
                else:
                    scheduled_time = now + timedelta(hours=hours)
                    schedule_desc = f"{int(hours) if hours.is_integer() else hours}小时后"
        elif rtype == 'custom-datetime' and reminder_config.get('datetime'):
            custom_str = reminder_config.get('datetime')  # 形如 YYYY-MM-DDTHH:mm
            try:
                # 前端输入为本地时间（视为北京时间）
                scheduled_time = datetime.fromisoformat(custom_str)
                schedule_desc = scheduled_time.strftime('%Y-%m-%d %H:%M')
            except Exception:
                scheduled_time = now
                schedule_desc = '立即'
        else:
            scheduled_time = now
            schedule_desc = '立即'

        # 若计算出的时间早于当前，则改为立即发送
        if scheduled_time <= now:
            from .notification_services import send_webhook_notification
            email_config = {'type': 'email', 'enabled': True, 'config': {'to_email': to_email}}
            message = f"{base_message}\n提醒时间: 立即"
            success = send_webhook_notification(email_config, message)

            # 记录到数据库，标记为已发送或失败，避免scheduler重复处理
            reminder_doc = {
                'user_id': ObjectId(user_id),
                'type': 'assignment',
                'target_id': assignment_id,
                'email': to_email,
                'message': message,
                'scheduled_time': now,
                'status': 'sent' if success else 'failed',
                'created_at': now,
                'updated_at': now,
                'sent_at': now if success else None,
                'error': None if success else 'immediate send failed'
            }
            mongo.db.scheduled_reminders.insert_one(reminder_doc)

            if success:
                logger.info(f"立即发送提醒到: {to_email}")
                return jsonify({
                    'success': True,
                    'message': f"提醒已立即发送：{subject} - {task}",
                    'detail': {'schedule': 'now', 'email': to_email}
                })
            else:
                logger.error(f"发送提醒邮件失败: {to_email}")
                return jsonify({
                    'success': False,
                    'error': '邮件发送失败，请检查邮箱配置'
                }), 500

        # 插入定时提醒（由scheduler处理）
        reminder_doc = {
            'user_id': ObjectId(user_id),
            'type': 'assignment',
            'target_id': assignment_id,
            'email': to_email,
            'message': f"{base_message}\n提醒时间: {schedule_desc}",
            'scheduled_time': scheduled_time,
            'status': 'scheduled',
            'created_at': now,
            'updated_at': now
        }
        mongo.db.scheduled_reminders.insert_one(reminder_doc)
        logger.info(f"已创建定时提醒，计划 {schedule_desc} 发送到: {to_email}")

        return jsonify({
            'success': True,
            'message': f"已设置{assignment_type}提醒（{schedule_desc}）：{subject} - {task}",
            'assignment': {
                'subject': subject,
                'task': task,
                'deadline': deadline_display,
                'type': assignment_type,
                'reminder_time': schedule_desc
            }
        })

    except Exception as e:
        logger.error(f"提醒作业失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': f'提醒失败: {str(e)}'}), 500


@assignments_bp.route('/enhanced', methods=['GET'])
@login_required
def get_enhanced_assignments():
    """获取增强作业列表（从数据库获取）"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'success': False, 'error': '用户未登录'}), 401

        logger.info(f"用户 {user_id} 请求获取增强作业列表")

        # 从数据库获取数据
        from .course_data import get_course_data_manager
        course_data_mgr = get_course_data_manager()
        tasks = course_data_mgr.get_user_course_data(user_id)

        # 获取作业状态信息
        from .assignment_status import get_assignment_status_manager
        status_manager = get_assignment_status_manager()
        completed_ids = status_manager.get_completed_assignment_ids(user_id)
        deleted_ids = status_manager.get_deleted_assignment_ids(user_id)
        completed_set = set(str(aid) for aid in completed_ids)
        deleted_set = set(str(aid) for aid in deleted_ids)

        # 获取黑名单 courseId set
        from .blacklist import get_user_blacklisted_ids, extract_course_id
        blacklisted_set = set(get_user_blacklisted_ids(user_id))

        # 处理增强数据（过滤掉已删除的任务）
        enhanced_assignments = []
        homework_count = 0
        test_count = 0

        for task in tasks:
            task_id = task.get('task_id')
            task_type = task.get('type', 'homework')

            # 跳过已删除的任务
            if task_id in deleted_set:
                continue

            # 跳过黑名单科目
            task_url = task.get('url', '')
            course_id = extract_course_id(task_url)
            if course_id and course_id in blacklisted_set:
                continue

            enhanced_assignment = {
                'id': task_id,
                'subject': task.get('subject', ''),
                'type': task_type,
                'title': task.get('title', ''),
                'deadline': task.get('deadline', ''),
                'url': task.get('url', ''),
                'can_submit': True,
                'is_group': False,
                'details_content': task.get('details', ''),
                'completed': task_id in completed_set,
                'has_detailed_tasks': bool(task.get('details', '').strip()),
                'tasks_count': 1
            }
            enhanced_assignments.append(enhanced_assignment)

            if task_type == 'homework':
                homework_count += 1
            else:
                test_count += 1

        stats = {
            'homework_count': homework_count,
            'tests_count': test_count,
            'total_count': len(enhanced_assignments)
        }

        logger.info(f"从数据库返回 {len(enhanced_assignments)} 个增强作业/测试项目")

        return jsonify({
            'success': True,
            'assignments': enhanced_assignments,
            'total': len(enhanced_assignments),
            'statistics': stats,
            'query_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'source': 'database'
        })

    except Exception as e:
        logger.error(f"获取增强作业列表失败: {str(e)}")
        return jsonify({'success': False, 'error': '获取增强作业列表失败'}), 500


@assignments_bp.route('/completed', methods=['GET'])
@login_required
def get_completed_assignments():
    """获取已完成的作业ID列表"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'success': False, 'error': '用户未登录'}), 401

        # 获取已完成的作业ID列表
        from .assignment_status import get_assignment_status_manager
        status_manager = get_assignment_status_manager()
        completed_ids = status_manager.get_completed_assignment_ids(user_id)

        return jsonify({
            'success': True,
            'completed_assignments': [str(aid) for aid in completed_ids]
        })

    except Exception as e:
        logger.error(f"获取已完成作业列表失败: {str(e)}")
        return jsonify({'success': False, 'error': '获取已完成作业列表失败'}), 500


@assignments_bp.route('/<assignment_id>/delete', methods=['POST'])
@login_required
def delete_assignment(assignment_id):
    """软删除作业（移至回收站）"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'success': False, 'error': '用户未登录'}), 401

        logger.info(f"用户 {user_id} 删除作业 {assignment_id}")

        # 从前端请求中获取作业信息
        data = request.get_json() or {}
        assignment_title = data.get('title', '未知作业')
        assignment_subject = data.get('subject', '未知科目')
        assignment_type = data.get('type', 'homework')  # 获取作业类型

        # 使用统一状态管理标记为已删除
        from .assignment_status import get_assignment_status_manager
        status_manager = get_assignment_status_manager()
        result = status_manager.mark_deleted(user_id, assignment_id, assignment_title, assignment_subject,
                                             assignment_type)

        if result.upserted_id or result.matched_count > 0:
            logger.info(f"作业 {assignment_id} 标记删除成功")
            return jsonify({'success': True, 'message': '作业已移至回收站'})
        else:
            return jsonify({'success': False, 'error': '删除失败'}), 500

    except Exception as e:
        logger.error(f"删除作业失败: {str(e)}")
        return jsonify({'success': False, 'error': '删除作业失败'}), 500


@assignments_bp.route('/<assignment_id>/restore', methods=['POST'])
@login_required
def restore_assignment(assignment_id):
    """恢复已删除的作业"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'success': False, 'error': '用户未登录'}), 401

        logger.info(f"用户 {user_id} 恢复作业 {assignment_id}")

        # 使用统一状态管理恢复作业
        from .assignment_status import get_assignment_status_manager
        status_manager = get_assignment_status_manager()
        result = status_manager.restore_assignment(user_id, assignment_id)

        if result.deleted_count > 0:
            logger.info(f"作业 {assignment_id} 恢复成功")
            return jsonify({'success': True, 'message': '作业已恢复'})
        else:
            return jsonify({'success': False, 'error': '恢复失败，作业不存在'}), 404

    except Exception as e:
        logger.error(f"恢复作业失败: {str(e)}")
        return jsonify({'success': False, 'error': '恢复作业失败'}), 500


@assignments_bp.route('/<assignment_id>/permanent-delete', methods=['DELETE'])
@login_required
def permanent_delete_assignment(assignment_id):
    """永久删除作业"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'success': False, 'error': '用户未登录'}), 401

        logger.info(f"用户 {user_id} 永久删除作业 {assignment_id}")

        # 使用新的永久删除方法
        from .assignment_status import get_assignment_status_manager
        status_manager = get_assignment_status_manager()
        result = status_manager.permanent_delete_assignment(user_id, assignment_id, '作业', '未知科目')

        if result.upserted_id or result.matched_count > 0:
            logger.info(f"作业 {assignment_id} 永久删除成功")
            return jsonify({'success': True, 'message': '作业已永久删除'})
        else:
            return jsonify({'success': False, 'error': '永久删除失败'}), 500

    except Exception as e:
        logger.error(f"永久删除作业失败: {str(e)}")
        return jsonify({'success': False, 'error': '永久删除作业失败'}), 500


@assignments_bp.route('/deleted', methods=['GET'])
@login_required
def get_deleted_assignments():
    """获取已删除的作业列表"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'success': False, 'error': '用户未登录'}), 401

        # 获取已删除的作业ID列表
        from .assignment_status import get_assignment_status_manager
        status_manager = get_assignment_status_manager()
        deleted_status_records = status_manager.get_user_assignment_status(user_id, 'deleted')
        deleted_ids = set(record['assignment_id'] for record in deleted_status_records)

        if not deleted_ids:
            return jsonify({
                'success': True,
                'deleted_assignments': [],
                'count': 0
            })

        # 从课程数据中获取完整的任务信息
        from .course_data import get_course_data_manager
        course_data_mgr = get_course_data_manager()

        # 直接从数据库查询所有用户数据（包括软删除的）
        from bson import ObjectId
        cursor = course_data_mgr.db[course_data_mgr.collection].find(
            {'user_id': ObjectId(user_id)}
        ).sort('updated_at', -1)

        # 筛选出已删除的任务并合并状态信息
        deleted_assignments = []
        status_dict = {record['assignment_id']: record for record in deleted_status_records}

        for doc in cursor:
            task_id = doc.get('task_id')
            if task_id in deleted_ids:
                status_record = status_dict.get(task_id, {})

                assignment = {
                    'task_id': task_id,
                    'subject': doc.get('subject', ''),
                    'title': doc.get('title', ''),
                    'deadline': doc.get('deadline', ''),
                    'details': doc.get('details', ''),
                    'url': doc.get('url', ''),
                    'type': doc.get('type', 'homework'),
                    'updated_at': doc.get('updated_at').isoformat() if doc.get('updated_at') else None,
                    'delete_time': status_record.get('status_time').isoformat() if status_record.get(
                        'status_time') else None,
                    '_id': str(doc.get('_id', '')),
                    'user_id': str(doc.get('user_id', ''))
                }
                deleted_assignments.append(assignment)

        return jsonify({
            'success': True,
            'deleted_assignments': deleted_assignments,
            'count': len(deleted_assignments)
        })

    except Exception as e:
        logger.error(f"获取已删除作业列表失败: {str(e)}")
        return jsonify({'success': False, 'error': '获取已删除作业列表失败'}), 500


@assignments_bp.route('/clear-deleted', methods=['DELETE'])
@login_required
def clear_deleted_assignments():
    """清空已删除的作业"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'success': False, 'error': '用户未登录'}), 401

        # 清空已删除的作业
        from .assignment_status import get_assignment_status_manager
        status_manager = get_assignment_status_manager()
        deleted_count = status_manager.clear_user_status(user_id, 'deleted')

        logger.info(f"用户 {user_id} 清空已删除作业，共删除 {deleted_count} 条")

        return jsonify({
            'success': True,
            'message': f'已清空 {deleted_count} 个已删除的作业',
            'deleted_count': deleted_count
        })

    except Exception as e:
        logger.error(f"清空已删除作业失败: {str(e)}")
        return jsonify({'success': False, 'error': '清空已删除作业失败'}), 500


@assignments_bp.route('/stats', methods=['GET'])
@login_required
def get_assignments_stats():
    """获取作业统计信息（从数据库获取）"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'success': False, 'error': '用户未登录'}), 401

        # 从数据库获取数据
        from .course_data import get_course_data_manager
        course_data_mgr = get_course_data_manager()
        tasks = course_data_mgr.get_user_course_data(user_id)

        # 获取作业状态信息
        from .assignment_status import get_assignment_status_manager
        status_manager = get_assignment_status_manager()
        completed_ids = status_manager.get_completed_assignment_ids(user_id)
        deleted_ids = status_manager.get_deleted_assignment_ids(user_id)
        completed_set = set(str(aid) for aid in completed_ids)
        deleted_set = set(str(aid) for aid in deleted_ids)

        # 统计各种状态（排除已删除的任务）
        now = datetime.now()
        active_tasks = [task for task in tasks if task.get('task_id') not in deleted_set]
        total = len(active_tasks)
        completed = 0
        urgent = 0
        soon = 0

        # 统计所有活跃任务
        for task in active_tasks:
            task_id = task.get('task_id')
            deadline = task.get('deadline', '')

            if task_id in completed_set:
                completed += 1
                continue

            # 检查截止日期
            if deadline:
                try:
                    # 尝试解析多种时间格式
                    if 'T' in deadline:
                        # ISO格式
                        due_date = datetime.fromisoformat(deadline.replace('Z', '+00:00'))
                    elif '年' in deadline and '月' in deadline and '日' in deadline:
                        # 中文格式：2025年9月23日 23:59:00
                        due_date = datetime.strptime(deadline, '%Y年%m月%d日 %H:%M:%S')
                    else:
                        # 其他格式，跳过
                        continue

                    days_until_due = (due_date - now).days

                    if days_until_due <= 2:
                        urgent += 1
                    elif days_until_due <= 7:
                        soon += 1
                except (ValueError, TypeError):
                    pass

        return jsonify({
            'success': True,
            'stats': {
                'total': total,
                'completed': completed,
                'urgent': urgent,
                'soon': soon,
                'remaining': total - completed
            },
            'source': 'database'
        })

    except Exception as e:
        logger.error(f"获取作业统计失败: {str(e)}")
        return jsonify({'success': False, 'error': '获取统计信息失败'}), 500
