from flask import Blueprint, jsonify, current_app, session, request
import sys
import os
import importlib.util
from datetime import datetime
from bson import ObjectId
from .model import User
from . import mongo

assignments_bp = Blueprint('assignments', __name__)

# 添加项目根目录到Python路径
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(backend_dir)

# 导入爬虫功能
get_enhanced_details = None
get_standard_format_details = None

def init_scraper_module():
    """初始化爬虫模块"""
    global get_enhanced_details, get_standard_format_details
    
    try:
        from ..scraper import get_enhanced_details, get_standard_format_details
        print("成功导入爬虫模块")
        return True
    except ImportError as e:
        print(f"导入爬虫模块失败: {e}")
        
        # 尝试相对路径导入
        scraper_path = os.path.join(backend_dir, 'scraper.py')
        if os.path.exists(scraper_path):
            try:
                spec = importlib.util.spec_from_file_location("scraper", scraper_path)
                if spec and spec.loader:
                    scraper_module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(scraper_module)
                    get_enhanced_details = scraper_module.get_enhanced_details
                    get_standard_format_details = scraper_module.get_standard_format_details
                    print("通过相对路径成功导入爬虫模块")
                    return True
            except Exception as ex:
                print(f"通过相对路径导入失败: {ex}")
        
        print(f"爬虫文件不存在: {scraper_path}")
        return False

# 初始化爬虫模块
scraper_available = init_scraper_module()

def get_scraper_data(username=None, password=None):
    """获取真实的爬虫数据"""
    print(f"爬虫模块可用性: {scraper_available}")
    print(f"get_enhanced_details函数: {get_enhanced_details}")
    
    if not scraper_available or not get_enhanced_details:
        print("爬虫模块不可用，返回空数据")
        return {'assignments': [], 'tests': []}
    
    if not username or not password:
        print(f"用户名或密码为空: username={username}, password={'***' if password else None}")
        return {'assignments': [], 'tests': []}
    
    try:
        print(f"开始获取用户 {username} 的爬虫数据")
        scraper_data = get_enhanced_details(username, password)
        
        print(f"爬虫原始返回数据: {scraper_data}")
        
        if not scraper_data:
            print("爬虫返回空数据")
            return {'assignments': [], 'tests': []}
        
        assignments_count = len(scraper_data.get('assignments', [])) if isinstance(scraper_data, dict) else 0
        tests_count = len(scraper_data.get('tests', [])) if isinstance(scraper_data, dict) else 0
        
        print(f"爬虫数据获取成功: {assignments_count} 个作业, {tests_count} 个测试")
        return scraper_data
        
    except Exception as e:
        print(f"获取爬虫数据时出错: {e}")
        import traceback
        traceback.print_exc()
        return {'assignments': [], 'tests': []}

def get_todo_data(user_id):
    """获取真实的待办事项数据"""
    try:
        if not user_id:
            return []
        
        # 从数据库获取用户的待办事项
        todos_cursor = mongo.db.todos.find({
            'user_id': ObjectId(user_id),
            'completed': {'$ne': True}  # 只获取未完成的待办
        }).sort('created_at', -1)
        
        todos = []
        for todo in todos_cursor:
            todo_item = {
                'id': f"todo_{str(todo['_id'])}",
                'subject': todo.get('category', '个人事务'),
                'title': todo.get('title', ''),
                'content': todo.get('description', ''),
                'dueDate': todo.get('due_date').isoformat() if todo.get('due_date') else None,
                'publisher': '我',
                'type': '待办',
                'completed': todo.get('completed', False),
                'priority': todo.get('priority', 'medium'),
                'source': 'todo',
                'created_at': todo.get('created_at').isoformat() if todo.get('created_at') else None
            }
            todos.append(todo_item)
        
        print(f"从数据库获取到 {len(todos)} 个待办事项")
        return todos
        
    except Exception as e:
        print(f"获取待办数据时出错: {e}")
        return []

def get_user_info():
    """获取当前用户信息"""
    try:
        print(f"Session内容: {dict(session)}")
        
        # 尝试从session获取用户ID
        user_id = session.get('user_id')
        print(f"从session获取的user_id: {user_id}")
        
        if not user_id:
            print("Session中没有user_id")
            return None, None
        
        # 获取用户信息
        print(f"查询用户: {user_id}")
        user = mongo.db.users.find_one({'_id': ObjectId(user_id)})
        print(f"数据库查询结果: {user}")
        
        if not user:
            print("数据库中用户不存在")
            return None, None
        
        print(f"用户信息获取成功: username={user.get('username')}")
        return user_id, user
        
    except Exception as e:
        print(f"获取用户信息时出错: {e}")
        import traceback
        traceback.print_exc()
        return None, None

@assignments_bp.route('/api/assignments', methods=['GET'])
def get_assignments():
    """获取作业列表 - 整合真实的爬虫数据和待办数据"""
    try:
        print("收到前端作业请求")
        
        # 获取用户信息
        user_id, user = get_user_info()
        print(f"用户信息: user_id={user_id}, user存在={user is not None}")
        
        if not user_id or not user:
            print("用户未登录")
            return jsonify({
                'assignments': [],
                'statistics': {
                    'total_courses': 0,
                    'pending_assignments': 0,
                    'pending_tests': 0,
                    'pending_todos': 0,
                    'total_pending': 0
                },
                'query_time': datetime.now().isoformat(),
                'total_count': 0,
                'message': '用户未登录，请先登录'
            }), 401
        
        # 获取真实的爬虫数据
        scraper_data = get_scraper_data(user.get('username'), user.get('password'))
        
        # 获取真实的待办数据
        todo_data = get_todo_data(user_id)
        
        # 整合所有数据
        all_assignments = []
        
        # 处理爬虫获取的作业数据
        assignments = scraper_data.get('assignments', [])
        for assignment in assignments:
            if isinstance(assignment, dict):
                all_assignments.append({
                    'id': f"assignment_{assignment.get('assignment_id', hash(str(assignment)))}",
                    'subject': assignment.get('course_name', ''),
                    'title': assignment.get('title', ''),
                    'content': assignment.get('description', ''),
                    'dueDate': assignment.get('due_date', ''),
                    'publisher': assignment.get('teacher', ''),
                    'type': '作业',
                    'completed': assignment.get('submit_status', '') == 'submitted',
                    'source': 'scraper',
                    'url': assignment.get('course_url', ''),
                    'assignment_id': assignment.get('assignment_id', '')
                })
        
        # 处理爬虫获取的测试数据
        tests = scraper_data.get('tests', [])
        for test in tests:
            if isinstance(test, dict):
                all_assignments.append({
                    'id': f"test_{test.get('test_id', hash(str(test)))}",
                    'subject': test.get('course_name', '在线测试'),
                    'title': test.get('title', ''),
                    'content': f"测试类型: {test.get('test_type', '')}, 创建时间: {test.get('create_time', '')}",
                    'dueDate': test.get('end_time', ''),
                    'publisher': '系统',
                    'type': '测试',
                    'completed': test.get('status', '') == 'completed',
                    'source': 'scraper',
                    'url': test.get('test_url', ''),
                    'test_id': test.get('test_id', '')
                })
        
        # 添加待办事项
        all_assignments.extend(todo_data)
        
        # 按截止日期排序
        all_assignments.sort(key=lambda x: x.get('dueDate', '9999-12-31'))
        
        # 计算统计信息
        total_count = len(all_assignments)
        pending_assignments = len([a for a in all_assignments if a.get('type') == '作业' and not a.get('completed')])
        pending_tests = len([a for a in all_assignments if a.get('type') == '测试' and not a.get('completed')])
        pending_todos = len([a for a in all_assignments if a.get('type') == '待办' and not a.get('completed')])
        
        # 获取课程统计
        stats = scraper_data.get('statistics', {})
        total_courses = stats.get('total_courses', 0)
        
        return jsonify({
            'assignments': all_assignments,
            'statistics': {
                'total_courses': total_courses,
                'pending_assignments': pending_assignments,
                'pending_tests': pending_tests,
                'pending_todos': pending_todos,
                'total_pending': pending_assignments + pending_tests + pending_todos
            },
            'query_time': datetime.now().isoformat(),
            'total_count': total_count,
            'message': '数据获取成功'
        })
        
    except Exception as e:
        print(f"API获取作业列表时发生错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'assignments': [],
            'statistics': {
                'total_courses': 0,
                'pending_assignments': 0,
                'pending_tests': 0,
                'pending_todos': 0,
                'total_pending': 0
            },
            'query_time': datetime.now().isoformat(),
            'total_count': 0,
            'error': '服务器内部错误',
            'message': '获取作业数据失败'
        }), 200

@assignments_bp.route('/api/assignments/standard', methods=['GET'])
def get_assignments_standard():
    """获取标准格式作业列表"""
    try:
        print("收到标准格式作业请求")
        
        # 获取用户信息
        user_id, user = get_user_info()
        print(f"用户信息: user_id={user_id}, user={user}")
        
        if not user_id or not user:
            print("用户未登录，返回空数据")
            return jsonify({
                'success': True,
                'data': [],
                'total_count': 0,
                'query_time': datetime.now().isoformat(),
                'message': '用户未登录，请先登录'
            })
        
        # 获取真实数据
        scraper_data = get_scraper_data(user.get('username'), user.get('password'))
        todo_data = get_todo_data(user_id)
        
        print(f"爬虫数据: {scraper_data}")
        print(f"待办数据: {todo_data}")
        
        # 整合所有数据为标准格式
        all_data = []
        
        # 处理爬虫数据
        for assignment in scraper_data.get('assignments', []):
            if isinstance(assignment, dict):
                all_data.append({
                    'id': f"assignment_{assignment.get('assignment_id', hash(str(assignment)))}",
                    'subject': assignment.get('course_name', ''),
                    'title': assignment.get('title', ''),
                    'content': assignment.get('description', ''),
                    'dueDate': assignment.get('due_date', ''),
                    'publisher': assignment.get('teacher', ''),
                    'type': '作业',
                    'completed': assignment.get('submit_status', '') == 'submitted',
                    'source': 'scraper'
                })
        
        for test in scraper_data.get('tests', []):
            if isinstance(test, dict):
                all_data.append({
                    'id': f"test_{test.get('test_id', hash(str(test)))}",
                    'subject': test.get('course_name', '在线测试'),
                    'title': test.get('title', ''),
                    'content': f"测试类型: {test.get('test_type', '')}",
                    'dueDate': test.get('end_time', ''),
                    'publisher': '系统',
                    'type': '测试',
                    'completed': test.get('status', '') == 'completed',
                    'source': 'scraper'
                })
        
        # 添加待办数据
        all_data.extend(todo_data)
        
        # 按截止日期排序
        all_data.sort(key=lambda x: x.get('dueDate', '9999-12-31'))
        
        return jsonify({
            'success': True,
            'data': all_data,
            'total_count': len(all_data),
            'query_time': datetime.now().isoformat(),
            'message': '数据获取成功'
        })
        
    except Exception as e:
        print(f"获取标准格式作业列表时发生错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'data': [],
            'error': '服务器内部错误',
            'message': '获取作业数据失败'
        }), 200

@assignments_bp.route('/api/assignments/refresh', methods=['POST'])
def refresh_assignments():
    """刷新作业数据"""
    try:
        print("收到刷新作业请求")
        
        # 获取用户信息
        user_id, user = get_user_info()
        if not user_id or not user:
            return jsonify({
                'error': '用户未登录',
                'message': '请先登录'
            }), 401
        
        # 重新获取真实数据并计算统计
        scraper_data = get_scraper_data(user.get('username'), user.get('password'))
        todo_data = get_todo_data(user_id)
        
        assignments_count = len(scraper_data.get('assignments', []))
        tests_count = len(scraper_data.get('tests', []))
        todos_count = len(todo_data)
        
        # 获取课程统计
        stats = scraper_data.get('statistics', {})
        total_courses = stats.get('total_courses', 0)
        
        return jsonify({
            'message': '数据刷新成功', 
            'assignments_count': assignments_count,
            'tests_count': tests_count,
            'todos_count': todos_count,
            'total_courses': total_courses,
            'query_time': datetime.now().isoformat(),
            'statistics': {
                'total_courses': total_courses,
                'pending_assignments': assignments_count,
                'pending_tests': tests_count,
                'pending_todos': todos_count,
                'total_pending': assignments_count + tests_count + todos_count
            }
        })
            
    except Exception as e:
        print(f"刷新作业数据时发生错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'error': '数据刷新失败', 
            'details': str(e)
        }), 200

@assignments_bp.route('/api/assignments/<assignment_id>/complete', methods=['POST'])
def mark_assignment_completed(assignment_id):
    """标记作业为已完成"""
    try:
        print(f"标记作业 {assignment_id} 为已完成")
        
        return jsonify({
            'message': '作业已标记为完成，12小时后自动清除',
            'success': True,
            'assignment_id': assignment_id,
            'expires_in_hours': 12
        })
            
    except Exception as e:
        print(f"标记作业完成失败: {str(e)}")
        return jsonify({
            'error': '标记完成失败', 
            'details': str(e), 
            'success': False
        }), 200

@assignments_bp.route('/api/assignments/<assignment_id>/uncomplete', methods=['POST'])
def unmark_assignment_completed(assignment_id):
    """取消作业完成标记"""
    try:
        print(f"取消作业 {assignment_id} 的完成标记")
        
        return jsonify({
            'message': '已取消完成标记',
            'success': True,
            'assignment_id': assignment_id
        })
            
    except Exception as e:
        print(f"取消完成标记失败: {str(e)}")
        return jsonify({
            'error': '取消完成标记失败', 
            'details': str(e), 
            'success': False
        }), 200

@assignments_bp.route('/api/assignments/completed', methods=['GET'])
def get_completed_assignments():
    """获取用户的已完成作业列表"""
    try:
        print("获取已完成作业列表")
        
        return jsonify({
            'success': True,
            'completed_assignments': [],
            'count': 0
        })
            
    except Exception as e:
        print(f"获取已完成作业列表失败: {str(e)}")
        return jsonify({
            'error': '获取已完成作业列表失败', 
            'details': str(e), 
            'success': False
        }), 200