# -*- coding: utf-8 -*-
"""
待办事项API模块

提供用户待办事项的CRUD操作接口
"""

from flask import Blueprint, jsonify, request, session, current_app
from datetime import datetime, timedelta
from .auth import login_required
from .model import Todo
from . import mongo
from bson import ObjectId

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
        description = data.get('description', '').strip() or None
        priority = data.get('priority', 'medium')
        
        # 验证优先级
        if priority not in ['low', 'medium', 'high']:
            priority = 'medium'
        
        # 处理截止日期 - 支持两种格式：小时数或ISO日期字符串
        due_date = None
        estimated_hours = None
        hours = data.get('hours')
        due_date_str = data.get('due_date')
        
        if hours is not None:
            # 前端发送小时数，计算截止时间并保存原始小时数
            try:
                hours_float = float(hours)
                if hours_float <= 0:
                    return jsonify({'error': '小时数必须大于0', 'success': False}), 400
                due_date = datetime.now() + timedelta(hours=hours_float)
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
                    update_data['due_date'] = datetime.now() + timedelta(hours=hours_float)
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
    """提醒待办事项"""
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
        
        # 这里可以添加提醒逻辑，比如发送通知、邮件等
        # 目前只是记录日志和返回提醒信息
        current_app.logger.info(f"用户 {user_id} 提醒待办事项: {existing_todo.get('title')}")
        
        return jsonify({
            'success': True,
            'message': f"已提醒待办事项: {existing_todo.get('title')}",
            'todo': {
                'title': existing_todo.get('title'),
                'description': existing_todo.get('description'),
                'priority': existing_todo.get('priority'),
                'due_date': existing_todo.get('due_date').isoformat() if existing_todo.get('due_date') else None
            }
        })
        
    except Exception as e:
        current_app.logger.error(f"提醒待办事项失败: {str(e)}")
        return jsonify({'error': '提醒待办事项失败', 'details': str(e), 'success': False}), 500

@todos_bp.route('/<todo_id>', methods=['DELETE'])
@login_required
def delete_todo(todo_id):
    """删除待办事项"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': '用户未登录', 'success': False}), 401
        
        # 创建待办模型实例
        todo_model = Todo(mongo.db)
        
        # 删除待办事项
        result = todo_model.delete_todo(todo_id, user_id)
        
        if result.deleted_count > 0:
            current_app.logger.info(f"用户 {user_id} 删除待办事项 {todo_id}")
            return jsonify({
                'success': True,
                'message': '待办事项已删除'
            })
        else:
            return jsonify({'error': '待办事项不存在', 'success': False}), 404
        
    except Exception as e:
        current_app.logger.error(f"删除待办事项失败: {str(e)}")
        return jsonify({'error': '删除待办事项失败', 'details': str(e), 'success': False}), 500

@todos_bp.route('/stats', methods=['GET'])
@login_required
def get_todo_stats():
    """获取待办事项统计信息"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': '用户未登录', 'success': False}), 401
        
        # 统计信息
        total_todos = mongo.db.todos.count_documents({'user_id': ObjectId(user_id)})
        completed_todos = mongo.db.todos.count_documents({
            'user_id': ObjectId(user_id),
            'completed': True
        })
        pending_todos = total_todos - completed_todos
        
        # 按优先级统计
        priority_stats = {}
        for priority in ['low', 'medium', 'high']:
            count = mongo.db.todos.count_documents({
                'user_id': ObjectId(user_id),
                'priority': priority,
                'completed': False
            })
            priority_stats[priority] = count
        
        # 今日到期的待办
        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = datetime.now().replace(hour=23, minute=59, second=59, microsecond=999999)
        
        due_today = mongo.db.todos.count_documents({
            'user_id': ObjectId(user_id),
            'completed': False,
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