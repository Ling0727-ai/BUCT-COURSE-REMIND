# -*- coding: utf-8 -*-
"""
待办事项API模块

提供用户待办事项的CRUD操作接口
"""

from datetime import datetime, timedelta, timezone

from bson import ObjectId
from flask import Blueprint, jsonify, request, session, current_app

from . import mongo
from .auth import login_required
from .model import Todo

# 定义北京时区
BEIJING_TZ = timezone(timedelta(hours=8))


def get_beijing_time():
    """获取北京时间（naive datetime，用于MongoDB存储）"""
    # 获取UTC时间（带时区信息）
    utc_now = datetime.now(timezone.utc)
    # 转换为北京时间（UTC+8）
    beijing_now = utc_now.astimezone(timezone(timedelta(hours=8)))
    # 返回naive datetime（去掉时区信息）
    return beijing_now.replace(tzinfo=None)


todos_bp = Blueprint('todos', __name__, url_prefix='/api/todos')


@todos_bp.route('/', methods=['GET'])
@login_required
def get_todos():
    """获取用户的待办事项列表"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': '用户未登录', 'success': False}), 401

        # 获取查询参数
        include_completed = request.args.get('include_completed', 'false').lower() == 'true'

        # 创建待办模型实例
        todo_model = Todo(mongo.db)

        # 获取待办列表
        todos = todo_model.get_user_todos(user_id, include_completed)

        # 转换ObjectId为字符串
        for todo in todos:
            todo['_id'] = str(todo['_id'])
            todo['user_id'] = str(todo['user_id'])
            if todo.get('due_date'):
                todo['due_date'] = todo['due_date'].isoformat()
            if todo.get('completed_at'):
                todo['completed_at'] = todo['completed_at'].isoformat()
            if todo.get('created_at'):
                todo['created_at'] = todo['created_at'].isoformat()
            if todo.get('updated_at'):
                todo['updated_at'] = todo['updated_at'].isoformat()
            # 确保 estimated_hours 字段存在
            if 'estimated_hours' not in todo:
                todo['estimated_hours'] = None

        return jsonify({
            'success': True,
            'todos': todos,
            'count': len(todos)
        })

    except Exception as e:
        current_app.logger.error(f"获取待办列表失败: {str(e)}")
        return jsonify({'error': '获取待办列表失败', 'details': str(e), 'success': False}), 500


@todos_bp.route('/', methods=['POST'])
@login_required
def create_todo():
    """创建新的待办事项"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': '用户未登录', 'success': False}), 401

        data = request.get_json()
        if not data or not data.get('title'):
            return jsonify({'error': '待办标题不能为空', 'success': False}), 400

        title = data.get('title').strip()
        # 更健壮的描述字段处理
        description_raw = data.get('description')
        if description_raw is None or description_raw == '':
            description = None
        else:
            description = description_raw.strip() if description_raw.strip() else None
        priority = data.get('priority', 'medium')

        # 验证优先级
        if priority not in ['low', 'medium', 'high']:
            priority = 'medium'

        # 处理截止日期 - 支持两种格式：小时数或ISO日期字符串
        due_date = None
        estimated_hours = None
        hours = data.get('hours')
        due_date_str = data.get('due_date')

        if hours is not None and hours != '':
            # 前端发送小时数，计算截止时间并保存原始小时数
            try:
                hours_float = float(hours)
                if hours_float <= 0:
                    return jsonify({'error': '小时数必须大于0', 'success': False}), 400
                due_date = get_beijing_time() + timedelta(hours=hours_float)
                estimated_hours = hours_float  # 保存用户输入的原始小时数
                current_app.logger.info(f"根据小时数 {hours_float} 计算截止时间: {due_date}")
            except (ValueError, TypeError):
                return jsonify({'error': '小时数格式错误', 'success': False}), 400
        elif due_date_str:
            # 兼容旧格式：ISO日期字符串
            try:
                due_date = datetime.fromisoformat(due_date_str.replace('Z', '+00:00'))
            except ValueError:
                return jsonify({'error': '截止日期格式错误', 'success': False}), 400
        else:
            # 未提供时间，默认24小时后
            hours_float = 24.0
            due_date = get_beijing_time() + timedelta(hours=hours_float)
            estimated_hours = hours_float
            current_app.logger.info(f"未提供时间，使用默认值24小时，截止时间: {due_date}")

        # 创建待办模型实例
        todo_model = Todo(mongo.db)

        # 创建待办事项
        todo_id = todo_model.create_todo(
            user_id=user_id,
            title=title,
            description=description,
            priority=priority,
            due_date=due_date,
            estimated_hours=estimated_hours
        )

        current_app.logger.info(f"用户 {user_id} 创建待办事项: {title}")

        return jsonify({
            'success': True,
            'message': '待办事项创建成功',
            'todo_id': str(todo_id)
        })

    except Exception as e:
        current_app.logger.error(f"创建待办事项失败: {str(e)}")
        return jsonify({'error': '创建待办事项失败', 'details': str(e), 'success': False}), 500


@todos_bp.route('/<todo_id>', methods=['PUT'])
@login_required
def update_todo(todo_id):
    """更新待办事项"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': '用户未登录', 'success': False}), 401

        data = request.get_json()
        if not data:
            return jsonify({'error': '请提供更新数据', 'success': False}), 400

        # 创建待办模型实例
        todo_model = Todo(mongo.db)

        # 检查待办是否存在
        existing_todo = todo_model.get_todo_by_id(todo_id, user_id)
        if not existing_todo:
            return jsonify({'error': '待办事项不存在', 'success': False}), 404

        # 准备更新数据
        update_data = {}

        if 'title' in data:
            title = data['title'].strip()
            if not title:
                return jsonify({'error': '待办标题不能为空', 'success': False}), 400
            update_data['title'] = title

        if 'description' in data:
            update_data['description'] = data['description'].strip() or None

        if 'priority' in data:
            priority = data['priority']
            if priority in ['low', 'medium', 'high']:
                update_data['priority'] = priority

        # 处理截止日期更新 - 支持小时数或ISO日期字符串
        if 'hours' in data:
            # 前端发送小时数，计算截止时间
            hours = data['hours']
            if hours is not None:
                try:
                    hours_float = float(hours)
                    if hours_float <= 0:
                        return jsonify({'error': '小时数必须大于0', 'success': False}), 400
                    update_data['due_date'] = get_beijing_time() + timedelta(hours=hours_float)
                    current_app.logger.info(f"根据小时数 {hours_float} 更新截止时间: {update_data['due_date']}")
                except (ValueError, TypeError):
                    return jsonify({'error': '小时数格式错误', 'success': False}), 400
            else:
                update_data['due_date'] = None
        elif 'due_date' in data:
            # 兼容旧格式：ISO日期字符串
            due_date_str = data['due_date']
            if due_date_str:
                try:
                    update_data['due_date'] = datetime.fromisoformat(due_date_str.replace('Z', '+00:00'))
                except ValueError:
                    return jsonify({'error': '截止日期格式错误', 'success': False}), 400
            else:
                update_data['due_date'] = None

        # 更新待办事项
        result = todo_model.update_todo(todo_id, user_id, update_data)

        if result.matched_count > 0:
            current_app.logger.info(f"用户 {user_id} 更新待办事项 {todo_id}")
            return jsonify({
                'success': True,
                'message': '待办事项更新成功'
            })
        else:
            return jsonify({'error': '待办事项不存在', 'success': False}), 404

    except Exception as e:
        current_app.logger.error(f"更新待办事项失败: {str(e)}")
        return jsonify({'error': '更新待办事项失败', 'details': str(e), 'success': False}), 500


@todos_bp.route('/<todo_id>/complete', methods=['POST'])
@login_required
def complete_todo(todo_id):
    """标记待办事项为已完成，12小时后自动删除"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': '用户未登录', 'success': False}), 401

        # 创建待办模型实例
        todo_model = Todo(mongo.db)

        # 检查待办是否存在
        existing_todo = todo_model.get_todo_by_id(todo_id, user_id)
        if not existing_todo:
            return jsonify({'error': '待办事项不存在', 'success': False}), 404

        # 标记为已完成，设置12小时后过期
        result = todo_model.mark_completed(todo_id, user_id)

        if result.matched_count > 0:
            current_app.logger.info(f"用户 {user_id} 完成待办事项: {existing_todo.get('title')}，12小时后自动删除")
            return jsonify({
                'success': True,
                'message': '待办事项已完成，12小时后自动删除'
            })
        else:
            return jsonify({'error': '更新失败', 'success': False}), 500

    except Exception as e:
        current_app.logger.error(f"完成待办事项失败: {str(e)}")
        return jsonify({'error': '完成待办事项失败', 'details': str(e), 'success': False}), 500


@todos_bp.route('/<todo_id>/uncomplete', methods=['POST'])
@login_required
def uncomplete_todo(todo_id):
    """撤销待办事项完成状态"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': '用户未登录', 'success': False}), 401

        # 创建待办模型实例
        todo_model = Todo(mongo.db)

        # 检查待办是否存在
        existing_todo = todo_model.get_todo_by_id(todo_id, user_id)
        if not existing_todo:
            return jsonify({'error': '待办事项不存在', 'success': False}), 404

        # 撤销完成状态，清除过期时间
        result = todo_model.mark_uncompleted(todo_id, user_id)

        if result.matched_count > 0:
            current_app.logger.info(f"用户 {user_id} 撤销完成待办事项: {existing_todo.get('title')}")
            return jsonify({
                'success': True,
                'message': '待办事项完成状态已撤销'
            })
        else:
            return jsonify({'error': '更新失败', 'success': False}), 500

    except Exception as e:
        current_app.logger.error(f"撤销待办完成状态失败: {str(e)}")
        return jsonify({'error': '撤销完成状态失败', 'details': str(e), 'success': False}), 500


@todos_bp.route('/<todo_id>/remind', methods=['POST'])
@login_required
def remind_todo(todo_id):
    """提醒待办事项 - 支持自定义提醒时间"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': '用户未登录', 'success': False}), 401

        # 创建待办模型实例
        todo_model = Todo(mongo.db)

        # 检查待办是否存在
        existing_todo = todo_model.get_todo_by_id(todo_id, user_id)
        if not existing_todo:
            return jsonify({'error': '待办事项不存在', 'success': False}), 404

        # 检查待办是否已完成
        if existing_todo.get('completed'):
            current_app.logger.warning(f"待办 {todo_id} 已完成，不发送提醒")
            return jsonify({
                'error': '该待办事项已完成，无需提醒',
                'success': False
            }), 400

        # 检查待办是否已删除（软删除）
        if existing_todo.get('deleted'):
            current_app.logger.warning(f"待办 {todo_id} 已删除，不发送提醒")
            return jsonify({
                'error': '该待办事项已删除，无法提醒',
                'success': False
            }), 400

        # 从前端请求中获取提醒配置
        data = request.get_json() or {}
        reminder_config = data.get('reminderConfig', {})

        title = existing_todo.get('title', '待办事项')
        description = existing_todo.get('description', '')
        priority = existing_todo.get('priority', 'medium')
        due_date = existing_todo.get('due_date')

        # 格式化截止时间显示
        due_date_display = ''
        if due_date:
            try:
                from datetime import datetime
                if isinstance(due_date, str):
                    dt = datetime.fromisoformat(due_date.replace('Z', '+00:00'))
                else:
                    dt = due_date
                due_date_display = dt.strftime('%Y年%m月%d日 %H:%M:%S')
            except (ValueError, AttributeError):
                due_date_display = str(due_date)

        # 处理提醒配置
        reminder_time_text = ""
        if reminder_config:
            reminder_type = reminder_config.get('type', 'instant')
            timing = reminder_config.get('timing', 'before')

            if reminder_type == 'instant':
                reminder_time_text = "立即"
            elif reminder_type in ['1h', '3h', '6h', '12h'] or 'hours' in reminder_config:
                hours = reminder_config.get('hours', 0)

                if timing == 'after':
                    # 从现在起N小时后
                    if hours >= 24:
                        days = hours // 24
                        remaining_hours = hours % 24
                        if remaining_hours > 0:
                            reminder_time_text = f"{days}天{remaining_hours}小时后"
                        else:
                            reminder_time_text = f"{days}天后"
                    else:
                        reminder_time_text = f"{hours}小时后"
                else:
                    # 截止时间前N小时
                    if hours >= 24:
                        days = hours // 24
                        remaining_hours = hours % 24
                        if remaining_hours > 0:
                            reminder_time_text = f"提前{days}天{remaining_hours}小时"
                        else:
                            reminder_time_text = f"提前{days}天"
                    else:
                        reminder_time_text = f"提前{hours}小时"
            elif reminder_type == 'custom-hours-before':
                hours = reminder_config.get('hours', 0)
                if hours >= 24:
                    days = hours // 24
                    remaining_hours = hours % 24
                    if remaining_hours > 0:
                        reminder_time_text = f"提前{days}天{remaining_hours}小时"
                    else:
                        reminder_time_text = f"提前{days}天"
                else:
                    reminder_time_text = f"提前{hours}小时"
            elif reminder_type == 'custom-hours-after':
                hours = reminder_config.get('hours', 0)
                if hours >= 24:
                    days = hours // 24
                    remaining_hours = hours % 24
                    if remaining_hours > 0:
                        reminder_time_text = f"{days}天{remaining_hours}小时后"
                    else:
                        reminder_time_text = f"{days}天后"
                else:
                    reminder_time_text = f"{hours}小时后"
            elif reminder_type == 'custom-datetime' and 'datetime' in reminder_config:
                custom_time = reminder_config.get('datetime', '')
                reminder_time_text = f"在{custom_time}时"

        # 发送实际提醒（立即发送）
        try:
            # 获取用户邮箱
            user = mongo.db.users.find_one({'_id': ObjectId(user_id)})
            if not user or not user.get('email'):
                return jsonify({'error': '未找到用户邮箱，请在设置中配置邮箱', 'success': False}), 400

            to_email = user['email']

            # 构建提醒消息
            priority_text = {'high': '高', 'medium': '中', 'low': '低'}.get(priority, '中')
            message = f"""📝 待办提醒

标题: {title}
优先级: {priority_text}
{f"描述: {description}" if description else ""}
{f"截止时间: {due_date_display}" if due_date_display else ""}
提醒时间: {reminder_time_text if reminder_time_text else '立即'}"""

            # 发送邮件提醒
            from .notification_services import send_webhook_notification
            email_config = {
                'type': 'email',
                'enabled': True,
                'config': {
                    'to_email': to_email
                }
            }
            success = send_webhook_notification(email_config, message)
            if success:
                current_app.logger.info(f"已发送待办提醒邮件到: {to_email}")
            else:
                current_app.logger.error(f"发送待办提醒邮件失败: {to_email}")
                return jsonify({'error': '邮件发送失败，请检查邮箱配置', 'success': False}), 500
        except Exception as e:
            current_app.logger.error(f"发送提醒邮件失败: {str(e)}")
            import traceback
            traceback.print_exc()
            return jsonify({'error': f'发送提醒失败: {str(e)}', 'success': False}), 500

        current_app.logger.info(f"用户 {user_id} 提醒待办事项: {title}, 提醒方式: {reminder_time_text}")

        return jsonify({
            'success': True,
            'message': f"{reminder_time_text}提醒已发送: {title}",
            'todo': {
                'title': title,
                'description': description,
                'priority': priority,
                'due_date': due_date.isoformat() if due_date else None,
                'reminder_time': reminder_time_text
            }
        })

    except Exception as e:
        current_app.logger.error(f"提醒待办事项失败: {str(e)}")
        return jsonify({'error': '提醒待办事项失败', 'details': str(e), 'success': False}), 500


@todos_bp.route('/<todo_id>/delete', methods=['POST'])
@login_required
def delete_todo(todo_id):
    """软删除待办事项（移至回收站）"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': '用户未登录', 'success': False}), 401

        data = request.get_json() or {}
        title = data.get('title', '未知待办')

        # 创建待办模型实例
        todo_model = Todo(mongo.db)

        # 检查待办是否存在
        existing_todo = todo_model.get_todo_by_id(todo_id, user_id)
        if not existing_todo:
            return jsonify({'error': '待办事项不存在', 'success': False}), 404

        # 软删除待办事项
        result = todo_model.delete_todo(todo_id, user_id)

        if result.matched_count > 0:
            current_app.logger.info(f"用户 {user_id} 删除待办事项: {title}")
            return jsonify({
                'success': True,
                'message': '待办事项已移至回收站'
            })
        else:
            return jsonify({'error': '删除失败', 'success': False}), 500

    except Exception as e:
        current_app.logger.error(f"删除待办事项失败: {str(e)}")
        return jsonify({'error': '删除待办事项失败', 'details': str(e), 'success': False}), 500


@todos_bp.route('/<todo_id>/restore', methods=['POST'])
@login_required
def restore_todo(todo_id):
    """恢复已删除的待办事项"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': '用户未登录', 'success': False}), 401

        data = request.get_json() or {}
        title = data.get('title', '未知待办')

        # 创建待办模型实例
        todo_model = Todo(mongo.db)

        # 恢复待办事项
        result = todo_model.restore_todo(todo_id, user_id)

        if result.matched_count > 0:
            current_app.logger.info(f"用户 {user_id} 恢复待办事项: {title}")
            return jsonify({
                'success': True,
                'message': '待办事项已恢复'
            })
        else:
            return jsonify({'error': '恢复失败，待办事项不存在', 'success': False}), 404

    except Exception as e:
        current_app.logger.error(f"恢复待办事项失败: {str(e)}")
        return jsonify({'error': '恢复待办事项失败', 'details': str(e), 'success': False}), 500


@todos_bp.route('/<todo_id>/permanent-delete', methods=['DELETE'])
@login_required
def permanent_delete_todo(todo_id):
    """永久删除待办事项"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': '用户未登录', 'success': False}), 401

        # 创建待办模型实例
        todo_model = Todo(mongo.db)

        # 永久删除待办事项
        result = todo_model.permanent_delete_todo(todo_id, user_id)

        if result.matched_count > 0:
            current_app.logger.info(f"用户 {user_id} 永久删除待办事项 {todo_id}")
            return jsonify({
                'success': True,
                'message': '待办事项已永久删除'
            })
        else:
            return jsonify({'error': '永久删除失败，待办事项不存在', 'success': False}), 404

    except Exception as e:
        current_app.logger.error(f"永久删除待办事项失败: {str(e)}")
        return jsonify({'error': '永久删除待办事项失败', 'details': str(e), 'success': False}), 500


@todos_bp.route('/deleted', methods=['GET'])
@login_required
def get_deleted_todos():
    """获取已删除的待办事项列表"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': '用户未登录', 'success': False}), 401

        # 创建待办模型实例
        todo_model = Todo(mongo.db)

        # 获取已删除的待办列表
        deleted_todos = todo_model.get_deleted_todos(user_id)

        # 转换ObjectId为字符串
        for todo in deleted_todos:
            todo['_id'] = str(todo['_id'])
            todo['user_id'] = str(todo['user_id'])
            todo['todo_id'] = str(todo['_id'])  # 添加todo_id字段供前端使用
            if todo.get('due_date'):
                todo['due_date'] = todo['due_date'].isoformat()
            if todo.get('completed_at'):
                todo['completed_at'] = todo['completed_at'].isoformat()
            if todo.get('delete_time'):
                todo['delete_time'] = todo['delete_time'].isoformat()
            if todo.get('created_at'):
                todo['created_at'] = todo['created_at'].isoformat()
            if todo.get('updated_at'):
                todo['updated_at'] = todo['updated_at'].isoformat()

        return jsonify({
            'success': True,
            'deleted_todos': deleted_todos,
            'count': len(deleted_todos)
        })

    except Exception as e:
        current_app.logger.error(f"获取已删除待办列表失败: {str(e)}")
        return jsonify({'error': '获取已删除待办列表失败', 'details': str(e), 'success': False}), 500


@todos_bp.route('/clear-deleted', methods=['DELETE'])
@login_required
def clear_deleted_todos():
    """清空已删除的待办事项"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': '用户未登录', 'success': False}), 401

        # 创建待办模型实例
        todo_model = Todo(mongo.db)

        # 清空已删除的待办事项
        result = todo_model.clear_deleted_todos(user_id)

        current_app.logger.info(f"用户 {user_id} 清空已删除待办事项，共删除 {result.modified_count} 条")

        return jsonify({
            'success': True,
            'message': f'已清空 {result.modified_count} 个已删除的待办事项',
            'deleted_count': result.modified_count
        })

    except Exception as e:
        current_app.logger.error(f"清空已删除待办事项失败: {str(e)}")
        return jsonify({'error': '清空已删除待办事项失败', 'details': str(e), 'success': False}), 500


@todos_bp.route('/stats', methods=['GET'])
@login_required
def get_todo_stats():
    """获取待办事项统计信息"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': '用户未登录', 'success': False}), 401

        # 统计信息（排除已删除和永久删除的）
        total_todos = mongo.db.todos.count_documents({
            'user_id': ObjectId(user_id),
            'is_deleted': {'$ne': True},
            'forever': {'$ne': 0}
        })
        completed_todos = mongo.db.todos.count_documents({
            'user_id': ObjectId(user_id),
            'completed': True,
            'is_deleted': {'$ne': True},
            'forever': {'$ne': 0}
        })
        pending_todos = total_todos - completed_todos

        # 按优先级统计
        priority_stats = {}
        for priority in ['low', 'medium', 'high']:
            count = mongo.db.todos.count_documents({
                'user_id': ObjectId(user_id),
                'priority': priority,
                'completed': False,
                'is_deleted': {'$ne': True},
                'forever': {'$ne': 0}
            })
            priority_stats[priority] = count

        # 今日到期的待办
        beijing_now = get_beijing_time()
        today_start = beijing_now.replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = beijing_now.replace(hour=23, minute=59, second=59, microsecond=999999)

        due_today = mongo.db.todos.count_documents({
            'user_id': ObjectId(user_id),
            'completed': False,
            'is_deleted': {'$ne': True},
            'forever': {'$ne': 0},
            'due_date': {'$gte': today_start, '$lte': today_end}
        })

        return jsonify({
            'success': True,
            'stats': {
                'total': total_todos,
                'completed': completed_todos,
                'pending': pending_todos,
                'due_today': due_today,
                'priority_stats': priority_stats
            }
        })

    except Exception as e:
        current_app.logger.error(f"获取待办统计失败: {str(e)}")
        return jsonify({'error': '获取待办统计失败', 'details': str(e), 'success': False}), 500
