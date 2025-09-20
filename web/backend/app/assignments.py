from flask import Blueprint, jsonify, current_app, session, request
import subprocess
import sys
import os
from datetime import datetime
from .auth import login_required
from . import mongo

# 添加项目根目录到Python路径
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(backend_dir)

# 导入增强版爬虫功能
get_enhanced_details = None
get_standard_format_details = None

def init_scraper_module():
    """初始化爬虫模块"""
    global get_enhanced_details, get_standard_format_details
    
    try:
        from scraper import get_enhanced_details, get_standard_format_details
        print("成功导入增强版爬虫模块")  # 使用print避免current_app问题
        return True
    except ImportError as e:
        print(f"导入爬虫模块失败: {e}")
        
        # 如果直接导入失败，尝试相对路径
        import importlib.util
        scraper_path = os.path.join(backend_dir, 'scraper.py')
        if os.path.exists(scraper_path):
            try:
                spec = importlib.util.spec_from_file_location("scraper", scraper_path)
                if spec and spec.loader:
                    scraper_module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(scraper_module)
                    get_enhanced_details = scraper_module.get_enhanced_details
                    get_standard_format_details = scraper_module.get_standard_format_details
                    print("通过相对路径成功导入增强版爬虫模块")
                    return True
            except Exception as ex:
                print(f"通过相对路径导入失败: {ex}")
        else:
            print(f"爬虫文件不存在: {scraper_path}")
        
        return False

# 尝试初始化爬虫模块
init_scraper_module()

ASSIGNMENTS_COLLECTION = 'assignments'
TESTS_COLLECTION = 'tests'

assignments_bp = Blueprint('assignments', __name__, url_prefix='/api/assignments')

@assignments_bp.route('/', methods=['GET'])
@login_required
def get_assignments():
    """获取所有作业和测试 - 使用增强版爬虫实时查询"""
    try:
        # 获取当前用户ID
        user_id = session.get('user_id')
        
        # 检查爬虫模块是否可用
        if not get_enhanced_details:
            current_app.logger.error("增强版爬虫模块不可用")
            return jsonify({'error': '爬虫模块不可用', 'details': '请检查scraper.py文件'}), 500
        
        # 调用增强版爬虫获取实时数据
        current_app.logger.info("开始使用增强版爬虫实时查询作业和测试数据")
        scraper_data = get_enhanced_details(user_id)
        
        if not scraper_data:
            current_app.logger.warning("增强版爬虫返回空数据，可能是登录失败或网络问题")
            return jsonify({'error': '无法获取课程数据，请检查学号密码设置', 'details': '爬虫返回空数据'}), 500
        
        result = []
        
        # 处理作业数据
        assignments = scraper_data.get('assignments', []) if scraper_data else []
        for assignment in assignments:
            result.append({
                'id': f"assignment_{hash(str(assignment.get('assignment_id', '')) + assignment.get('course_name', ''))}", 
                'subject': assignment.get('course_name', ''), 
                'title': assignment.get('title', ''),
                'content': assignment.get('description', ''), 
                'dueDate': assignment.get('due_date', ''),
                'publisher': assignment.get('teacher', ''), 
                'type': '作业', 
                'completed': assignment.get('submit_status', '') == 'submitted',
                'queryTime': scraper_data.get('query_time', ''),
                'url': assignment.get('course_url', ''),
                'assignment_id': assignment.get('assignment_id', '')
            })
        
        # 处理测试数据
        tests = scraper_data.get('tests', []) if scraper_data else []
        for test in tests:
            result.append({
                'id': f"test_{hash(str(test.get('test_id', '')) + test.get('title', ''))}", 
                'subject': test.get('course_name', '在线测试'), 
                'title': test.get('title', ''),
                'content': f"测试类型: {test.get('test_type', '')}, 创建时间: {test.get('create_time', '')}",
                'dueDate': test.get('end_time', ''), 
                'publisher': '系统', 
                'type': '测试', 
                'completed': test.get('status', '') == 'completed',
                'queryTime': scraper_data.get('query_time', ''),
                'url': test.get('test_url', ''),
                'test_id': test.get('test_id', '')
            })
        
        # 添加统计信息
        stats = scraper_data.get('statistics', {})
        current_app.logger.info(f"增强版爬虫查询成功，获取到 {len(result)} 条数据")
        current_app.logger.info(f"统计: {stats.get('total_courses', 0)}门课程, {stats.get('pending_assignments', 0)}个作业, {stats.get('pending_tests', 0)}个测试")
        
        return jsonify({
            'assignments': result,
            'statistics': stats,
            'query_time': scraper_data.get('query_time', ''),
            'total_count': len(result)
        })
        
    except Exception as e:
        current_app.logger.error(f"增强版爬虫获取作业数据失败: {str(e)}")
        return jsonify({'error': '获取作业数据失败', 'details': str(e)}), 500

@assignments_bp.route('/refresh', methods=['POST'])
@login_required
def refresh_assignments():
    """刷新作业数据 - 使用增强版爬虫实时查询"""
    try:
        # 获取当前用户ID
        user_id = session.get('user_id')
        
        # 检查爬虫模块是否可用
        if not get_enhanced_details:
            return jsonify({'error': '爬虫模块不可用', 'details': '请检查scraper.py文件'}), 500
        
        # 直接调用增强版爬虫获取最新数据
        current_app.logger.info("开始使用增强版爬虫实时刷新作业数据")
        scraper_data = get_enhanced_details(user_id)
        
        if scraper_data:
            stats = scraper_data.get('statistics', {})
            assignments_count = stats.get('pending_assignments', 0)
            tests_count = stats.get('pending_tests', 0)
            available_tests = stats.get('available_tests', 0)
            total_courses = stats.get('total_courses', 0)
            query_time = scraper_data.get('query_time', '')
            
            current_app.logger.info(f"增强版数据刷新成功: {assignments_count}个作业, {tests_count}个测试, {available_tests}个可进行测试")
            return jsonify({
                'message': '数据刷新成功', 
                'assignments_count': assignments_count,
                'tests_count': tests_count,
                'available_tests': available_tests,
                'total_courses': total_courses,
                'query_time': query_time,
                'statistics': stats
            })
        else:
            current_app.logger.error("增强版数据刷新失败: 爬虫返回空数据")
            return jsonify({'error': '数据刷新失败', 'details': '无法获取课程数据'}), 500
            
    except Exception as e:
        current_app.logger.error(f"增强版数据刷新异常: {str(e)}")
        return jsonify({'error': '数据刷新失败', 'details': str(e)}), 500

@assignments_bp.route('/standard', methods=['GET'])
@login_required
def get_assignments_standard():
    """获取标准JSON格式的作业和测试数据"""
    try:
        # 获取当前用户ID
        user_id = session.get('user_id')
        
        # 检查爬虫模块是否可用
        if not get_standard_format_details:
            return jsonify({
                'success': False,
                'error': '标准格式爬虫模块不可用', 
                'details': '请检查scraper.py文件',
                'data': []
            }), 500
        
        # 调用标准格式爬虫获取数据
        current_app.logger.info("开始获取标准JSON格式的作业和测试数据")
        standard_data = get_standard_format_details(user_id)
        
        if not standard_data:
            current_app.logger.warning("标准格式爬虫返回空数据")
            return jsonify({
                'success': False,
                'error': '无法获取课程数据', 
                'details': '爬虫返回空数据',
                'data': []
            }), 500
        
        current_app.logger.info(f"标准格式数据获取成功，共 {len(standard_data)} 个任务")
        return jsonify({
            'success': True,
            'data': standard_data,
            'total_count': len(standard_data),
            'query_time': datetime.now().isoformat()
        })
        
    except Exception as e:
        current_app.logger.error(f"获取标准格式数据失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': '获取标准格式数据失败', 
            'details': str(e),
            'data': []
        }), 500

@assignments_bp.route('/detailed', methods=['GET'])
@login_required
def get_assignments_detailed():
    """获取详细的课程信息（包含统计和分类信息）"""
    try:
        # 获取当前用户ID
        user_id = session.get('user_id')
        
        # 检查爬虫模块是否可用
        if not get_enhanced_details:
            return jsonify({'error': '增强版爬虫模块不可用', 'details': '请检查scraper.py文件'}), 500
        
        # 调用增强版爬虫获取详细数据
        current_app.logger.info("开始获取详细的课程信息")
        detailed_data = get_enhanced_details(user_id)
        
        if not detailed_data:
            current_app.logger.warning("详细数据获取失败")
            return jsonify({'error': '无法获取详细课程数据', 'details': '爬虫返回空数据'}), 500
        
        current_app.logger.info("详细课程信息获取成功")
        return jsonify(detailed_data)
        
    except Exception as e:
        current_app.logger.error(f"获取详细课程信息失败: {str(e)}")
        return jsonify({'error': '获取详细课程信息失败', 'details': str(e)}), 500

@assignments_bp.route('/<assignment_id>/complete', methods=['POST'])
@login_required
def mark_assignment_completed(assignment_id):
    """标记作业为已完成"""
    try:
        from .model import CompletedAssignment
        from flask import request
        
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': '用户未登录', 'success': False}), 401
        
        # 获取请求数据
        data = request.get_json() or {}
        assignment_title = data.get('title', '未知作业')
        assignment_subject = data.get('subject', '未知科目')
        
        # 创建完成记录模型实例
        completed_model = CompletedAssignment(mongo.db)
        
        # 标记为已完成
        result = completed_model.mark_completed(
            user_id=user_id,
            assignment_id=assignment_id,
            assignment_title=assignment_title,
            assignment_subject=assignment_subject
        )
        
        current_app.logger.info(f"用户 {user_id} 标记作业 {assignment_id} 为已完成")
        return jsonify({
            'message': '作业已标记为完成',
            'success': True,
            'assignment_id': assignment_id,
            'expires_in_hours': 12
        })
            
    except Exception as e:
        current_app.logger.error(f"标记作业完成失败: {str(e)}")
        return jsonify({'error': '标记完成失败', 'details': str(e), 'success': False}), 500

@assignments_bp.route('/<assignment_id>/uncomplete', methods=['POST'])
@login_required
def unmark_assignment_completed(assignment_id):
    """取消作业完成标记"""
    try:
        from .model import CompletedAssignment
        
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': '用户未登录', 'success': False}), 401
        
        # 创建完成记录模型实例
        completed_model = CompletedAssignment(mongo.db)
        
        # 取消完成标记
        result = completed_model.unmark_completed(user_id, assignment_id)
        
        if result.deleted_count > 0:
            current_app.logger.info(f"用户 {user_id} 取消作业 {assignment_id} 的完成标记")
            return jsonify({
                'message': '已取消完成标记',
                'success': True,
                'assignment_id': assignment_id
            })
        else:
            return jsonify({
                'message': '该作业未标记为完成',
                'success': False,
                'assignment_id': assignment_id
            }), 404
            
    except Exception as e:
        current_app.logger.error(f"取消完成标记失败: {str(e)}")
        return jsonify({'error': '取消完成标记失败', 'details': str(e), 'success': False}), 500

@assignments_bp.route('/completed', methods=['GET'])
@login_required
def get_completed_assignments():
    """获取用户的已完成作业列表"""
    try:
        from .model import CompletedAssignment
        
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': '用户未登录', 'success': False}), 401
        
        # 创建完成记录模型实例
        completed_model = CompletedAssignment(mongo.db)
        
        # 获取已完成作业列表
        completed_ids = completed_model.get_user_completed(user_id)
        
        return jsonify({
            'success': True,
            'completed_assignments': completed_ids,
            'count': len(completed_ids)
        })
            
    except Exception as e:
        current_app.logger.error(f"获取已完成作业列表失败: {str(e)}")
        return jsonify({'error': '获取已完成作业列表失败', 'details': str(e), 'success': False}), 500

def scrape_assignments_job():
    """定时任务：使用增强版爬虫抓取作业数据"""
    try:
        current_app.logger.info("开始执行增强版定时抓取任务")
        
        # 检查爬虫模块是否可用
        if not get_enhanced_details:
            current_app.logger.error("增强版爬虫模块不可用，跳过定时任务")
            return
        
        # 获取所有用户的数据（这里需要根据实际需求调整）
        # 暂时使用默认用户ID，实际应该遍历所有用户
        scraper_data = get_enhanced_details()
        
        if scraper_data:
            stats = scraper_data.get('statistics', {})
            current_app.logger.info(f"增强版定时抓取任务成功: {stats.get('pending_assignments', 0)}个作业, {stats.get('pending_tests', 0)}个测试")
            
            # TODO: 添加通知功能
            # TODO: 可以在这里添加数据缓存或通知逻辑
            
        else:
            current_app.logger.warning("增强版定时抓取任务返回空数据")
            
    except Exception as e:
        current_app.logger.error(f"增强版定时抓取任务异常: {str(e)}")