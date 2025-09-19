import datetime
import buct_course
import os
import sys
from pymongo import MongoClient
from urllib.parse import quote_plus
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BUCTScraperEnhanced:
    """BUCT课程平台增强爬虫类 - 基于源码分析的完整实现"""
    
    def __init__(self):
        self.mongo_client = None
        self.db = None
        self.client = None  # 使用BUCTClient
        self._connect_to_database()
    
    def _connect_to_database(self):
        """连接到MongoDB数据库"""
        try:
            # 从环境变量获取数据库连接信息
            mongo_uri = os.getenv('MONGO_URI')
            
            if not mongo_uri:
                # 如果没有MONGO_URI，构建连接字符串
                username = os.getenv('MONGO_INITDB_ROOT_USERNAME', 'REDACTED_MONGO_USER')
                password = os.getenv('MONGO_INITDB_ROOT_PASSWORD', 'REDACTED_MONGO_PASSWORD')
                host = os.getenv('MONGO_HOST', 'localhost')
                port = os.getenv('MONGO_PORT', '27017')
                db_name = os.getenv('MONGO_INITDB_DATABASE', 'buct-course')
                
                mongo_uri = f"mongodb://{username}:{password}@{host}:{port}/{db_name}"
            
            self.mongo_client = MongoClient(mongo_uri)
            
            # 提取数据库名称
            if '/' in mongo_uri:
                db_name = mongo_uri.split('/')[-1]
                # 移除可能的查询参数
                if '?' in db_name:
                    db_name = db_name.split('?')[0]
            else:
                db_name = 'buct-course'
            
            self.db = self.mongo_client[db_name]
            
            # 测试连接
            self.db.command('ping')
            logger.info(f"数据库连接成功: {db_name}")
            
        except Exception as e:
            logger.error(f"数据库连接失败: {str(e)}")
            raise
    
    def get_user_credentials(self, user_id=None):
        """
        从数据库获取用户的学号和密码
        
        Args:
            user_id: 用户ID，如果为None则获取第一个有凭证的用户
            
        Returns:
            tuple: (student_id, s_password) 或 (None, None)
        """
        try:
            if user_id:
                # 根据用户ID查找
                from bson import ObjectId
                user = self.db.users.find_one({'_id': ObjectId(user_id)})
            else:
                # 查找第一个有学号和密码的用户
                user = self.db.users.find_one({
                    'student_id': {'$exists': True, '$ne': None, '$ne': ''},
                    's_password': {'$exists': True, '$ne': None, '$ne': ''}
                })
            
            if user and user.get('student_id') and user.get('s_password'):
                logger.info(f"找到用户凭证: 学号 {user['student_id']}")
                return user['student_id'], user['s_password']
            else:
                logger.warning("未找到有效的用户凭证")
                return None, None
                
        except Exception as e:
            logger.error(f"获取用户凭证失败: {str(e)}")
            return None, None
    
    def login(self, user_id=None):
        """
        登录到BUCT课程平台
        
        Args:
            user_id: 用户ID，如果为None则使用第一个有凭证的用户
            
        Returns:
            bool: 登录是否成功
        """
        try:
            # 获取用户凭证
            student_id, s_password = self.get_user_credentials(user_id)
            
            if not student_id or not s_password:
                logger.error("无法获取有效的用户凭证")
                return False
            
            # 创建BUCT客户端实例
            self.client = buct_course.create_client()
            
            # 尝试登录
            logger.info(f"正在尝试登录，学号: {student_id}")
            login_success = self.client.login(student_id, s_password)
            
            if login_success:
                logger.info("登录成功")
                return True
            else:
                logger.error("登录失败，请检查学号和密码")
                return False
                
        except Exception as e:
            logger.error(f"登录过程中发生错误: {str(e)}")
            return False
    
    def get_comprehensive_course_details(self):
        """
        获取全面的课程详情（基于源码中实际可用的方法）
        
        Returns:
            dict: 包含详细课程信息的字典
        """
        if not self.client:
            logger.error("未登录，无法获取课程详情")
            return None
        
        try:
            comprehensive_info = {
                'pending_tasks': {},
                'detailed_tests': {},
                'course_summary': {},
                'statistics': {},
                'raw_data': {}
            }
            
            # 1. 获取待办任务（作业和测试）
            logger.info("正在获取待办任务...")
            try:
                pending_tasks = self.client.get_pending_tasks()
                comprehensive_info['pending_tasks'] = pending_tasks
                comprehensive_info['raw_data']['pending_tasks'] = pending_tasks
                
                if pending_tasks and pending_tasks.get('success'):
                    data = pending_tasks.get('data', {})
                    homework_list = data.get('homework', [])
                    tests_list = data.get('tests', [])
                    
                    logger.info(f"✅ 获取到 {len(homework_list)} 个待提交作业")
                    logger.info(f"✅ 获取到 {len(tests_list)} 个待提交测试")
                    
                    # 记录作业详情
                    for hw in homework_list:
                        logger.info(f"   📝 作业: {hw.get('course_name', 'N/A')} (ID: {hw.get('lid', 'N/A')})")
                    
                    # 记录测试详情
                    for test in tests_list:
                        logger.info(f"   🧪 测试: {test.get('course_name', 'N/A')} (ID: {test.get('lid', 'N/A')})")
                
            except Exception as e:
                logger.warning(f"获取待办任务失败: {str(e)}")
                comprehensive_info['pending_tasks'] = {'success': False, 'error': str(e)}
            
            # 2. 获取测试分类信息
            logger.info("正在获取测试分类...")
            try:
                test_categories = self.client.get_test_categories()
                comprehensive_info['raw_data']['test_categories'] = test_categories
                
                if test_categories and test_categories.get('success'):
                    categories = test_categories.get('data', {}).get('categories', [])
                    logger.info(f"✅ 获取到 {len(categories)} 个测试分类")
                    
                    for category in categories:
                        logger.info(f"   📂 分类: {category.get('name', 'N/A')} (ID: {category.get('id', 'N/A')})")
                
            except Exception as e:
                logger.warning(f"获取测试分类失败: {str(e)}")
                comprehensive_info['raw_data']['test_categories'] = {'success': False, 'error': str(e)}
            
            # 3. 获取每个分类下的详细测试信息
            logger.info("正在获取详细测试信息...")
            detailed_tests = {}
            
            # 预定义的测试分类ID（基于源码分析）
            test_category_ids = ["34060", "34061", "34062", "34063"]
            
            for cate_id in test_category_ids:
                try:
                    logger.info(f"正在获取分类 {cate_id} 的测试...")
                    
                    # 获取该分类下的所有测试
                    category_tests = self.client.get_tests_by_category(cate_id)
                    detailed_tests[cate_id] = category_tests
                    
                    if category_tests and category_tests.get('success'):
                        tests = category_tests.get('data', {}).get('tests', [])
                        stats = category_tests.get('data', {}).get('stats', {})
                        
                        logger.info(f"   ✅ 分类 {cate_id}: {stats.get('total_tests', 0)} 个测试")
                        logger.info(f"      - 可进行: {stats.get('available_tests', 0)} 个")
                        logger.info(f"      - 已完成: {stats.get('completed_tests', 0)} 个")
                        
                        # 记录每个测试的详细信息
                        for test in tests:
                            if test.get('can_take_test'):
                                logger.info(f"      🟢 {test.get('title', 'N/A')}")
                                if test.get('date'):
                                    logger.info(f"         📅 创建: {test.get('date')}")
                                if test.get('deadline'):
                                    logger.info(f"         ⏰ 截止: {test.get('deadline')}")
                                if test.get('test_link'):
                                    logger.info(f"         🔗 链接: {test.get('test_link')}")
                    else:
                        logger.info(f"   ❌ 分类 {cate_id}: 无可用测试或获取失败")
                        
                except Exception as e:
                    logger.debug(f"获取分类 {cate_id} 测试失败: {str(e)}")
                    detailed_tests[cate_id] = {'success': False, 'error': str(e)}
            
            comprehensive_info['detailed_tests'] = detailed_tests
            
            # 4. 生成课程摘要
            logger.info("正在生成课程摘要...")
            course_summary = self._generate_course_summary(comprehensive_info)
            comprehensive_info['course_summary'] = course_summary
            
            # 5. 生成统计信息
            statistics = self._generate_statistics(comprehensive_info)
            comprehensive_info['statistics'] = statistics
            
            logger.info("✅ 全面课程信息获取完成")
            return comprehensive_info
            
        except Exception as e:
            logger.error(f"获取全面课程详情失败: {str(e)}")
            return None
    
    def _generate_course_summary(self, comprehensive_info):
        """生成课程摘要信息"""
        try:
            summary = {
                'courses': [],
                'assignments': [],
                'tests': [],
                'urgent_items': []
            }
            
            # 从待办任务中提取课程信息
            pending_tasks = comprehensive_info.get('pending_tasks', {})
            if pending_tasks.get('success'):
                data = pending_tasks.get('data', {})
                
                # 处理作业
                homework_list = data.get('homework', [])
                for hw in homework_list:
                    course_name = hw.get('course_name', '')
                    if course_name and course_name not in [c['name'] for c in summary['courses']]:
                        summary['courses'].append({
                            'name': course_name,
                            'id': hw.get('lid'),
                            'url': hw.get('url'),
                            'type': 'course_with_homework'
                        })
                    
                    summary['assignments'].append({
                        'course_name': course_name,
                        'id': hw.get('lid'),
                        'url': hw.get('url'),
                        'status': 'pending'
                    })
                
                # 处理测试
                tests_list = data.get('tests', [])
                for test in tests_list:
                    course_name = test.get('course_name', '')
                    if course_name and course_name not in [c['name'] for c in summary['courses']]:
                        summary['courses'].append({
                            'name': course_name,
                            'id': test.get('lid'),
                            'url': test.get('url'),
                            'type': 'course_with_test'
                        })
                    
                    summary['tests'].append({
                        'course_name': course_name,
                        'id': test.get('lid'),
                        'url': test.get('url'),
                        'status': 'pending'
                    })
            
            # 从详细测试信息中提取额外的测试
            detailed_tests = comprehensive_info.get('detailed_tests', {})
            for cate_id, category_data in detailed_tests.items():
                if category_data.get('success'):
                    tests = category_data.get('data', {}).get('tests', [])
                    for test in tests:
                        if test.get('can_take_test'):
                            summary['tests'].append({
                                'title': test.get('title', ''),
                                'category_id': cate_id,
                                'date': test.get('date', ''),
                                'deadline': test.get('deadline', ''),
                                'test_link': test.get('test_link', ''),
                                'status': 'available'
                            })
            
            return summary
            
        except Exception as e:
            logger.error(f"生成课程摘要失败: {str(e)}")
            return {}
    
    def _generate_statistics(self, comprehensive_info):
        """生成统计信息"""
        try:
            stats = {
                'total_courses': 0,
                'total_assignments': 0,
                'total_tests': 0,
                'available_tests': 0,
                'pending_assignments': 0,
                'pending_tests': 0,
                'categories_with_tests': 0
            }
            
            # 统计待办任务
            pending_tasks = comprehensive_info.get('pending_tasks', {})
            if pending_tasks.get('success'):
                data = pending_tasks.get('data', {})
                stats['pending_assignments'] = len(data.get('homework', []))
                stats['pending_tests'] = len(data.get('tests', []))
                
                # 统计涉及的课程数量
                course_names = set()
                for hw in data.get('homework', []):
                    if hw.get('course_name'):
                        course_names.add(hw.get('course_name'))
                for test in data.get('tests', []):
                    if test.get('course_name'):
                        course_names.add(test.get('course_name'))
                stats['total_courses'] = len(course_names)
            
            # 统计详细测试信息
            detailed_tests = comprehensive_info.get('detailed_tests', {})
            for cate_id, category_data in detailed_tests.items():
                if category_data.get('success'):
                    category_stats = category_data.get('data', {}).get('stats', {})
                    stats['total_tests'] += category_stats.get('total_tests', 0)
                    stats['available_tests'] += category_stats.get('available_tests', 0)
                    
                    if category_stats.get('total_tests', 0) > 0:
                        stats['categories_with_tests'] += 1
            
            stats['total_assignments'] = stats['pending_assignments']  # 目前只能获取待办作业
            
            return stats
            
        except Exception as e:
            logger.error(f"生成统计信息失败: {str(e)}")
            return {}
    
    def format_to_standard_json(self, comprehensive_data):
        """
        格式化为统一的标准JSON格式
        
        Args:
            comprehensive_data: 全面的课程数据
            
        Returns:
            list: 统一格式的任务列表，格式为:
            [
                {
                    "type": "homework" | "test",
                    "subject": "科目名称",
                    "details": {
                        "task": "具体任务详情",
                        "deadline": "结束时间",
                        "url": "对应的网页url"
                    }
                }
            ]
        """
        if not comprehensive_data:
            return []
        
        try:
            standard_tasks = []
            course_summary = comprehensive_data.get('course_summary', {})
            
            # 处理作业信息
            for assignment in course_summary.get('assignments', []):
                task_item = {
                    "type": "homework",
                    "subject": assignment.get('course_name', '未知科目'),
                    "details": {
                        "task": f"{assignment.get('course_name', '未知课程')} - 作业待提交",
                        "deadline": "",  # 待办任务中没有截止时间信息
                        "url": assignment.get('url', '')
                    }
                }
                standard_tasks.append(task_item)
            
            # 处理测试信息
            for test in course_summary.get('tests', []):
                # 优先使用 course_name，如果没有则使用 title
                subject = test.get('course_name', '') or test.get('title', '未知科目')
                task_name = test.get('title', '') or test.get('course_name', '未知测试')
                
                task_item = {
                    "type": "test",
                    "subject": subject,
                    "details": {
                        "task": task_name,
                        "deadline": test.get('deadline', ''),
                        "url": test.get('test_link', test.get('url', ''))
                    }
                }
                standard_tasks.append(task_item)
            
            logger.info(f"✅ 格式化完成，共 {len(standard_tasks)} 个任务")
            return standard_tasks
                        
        except Exception as e:
            logger.error(f"格式化为标准JSON失败: {str(e)}")
            return []
    
    def format_enhanced_data(self, comprehensive_data):
        """
        格式化增强的课程数据，保持与原版本的兼容性
        
        Args:
            comprehensive_data: 全面的课程数据
            
        Returns:
            dict: 格式化后的数据（兼容原格式）
        """
        if not comprehensive_data:
            return None
        
        try:
            current_time = datetime.datetime.now(datetime.timezone.utc)
            formatted_data = {
                'query_time': current_time.isoformat(),
                'assignments': [],
                'tests': [],
                'standard_format': self.format_to_standard_json(comprehensive_data),  # 添加标准格式
                'enhanced_info': comprehensive_data  # 添加增强信息
            }
            
            # 从课程摘要中提取格式化的作业和测试信息
            course_summary = comprehensive_data.get('course_summary', {})
            
            # 格式化作业信息
            for assignment in course_summary.get('assignments', []):
                formatted_assignment = {
                    'subject': assignment.get('course_name', ''),
                    'title': assignment.get('course_name', ''),
                    'content': f"课程ID: {assignment.get('id', '')}",
                    'due_date': '',  # 待办任务中没有截止时间信息
                    'publisher': '系统',
                    'type': '作业',
                    'status': assignment.get('status', 'pending'),
                    'course_url': assignment.get('url', ''),
                    'query_time': current_time.isoformat()
                }
                formatted_data['assignments'].append(formatted_assignment)
            
            # 格式化测试信息
            for test in course_summary.get('tests', []):
                formatted_test = {
                    'title': test.get('title', test.get('course_name', '')),
                    'start_time': test.get('date', ''),
                    'end_time': test.get('deadline', ''),
                    'allowed_attempts': 1,  # 默认值
                    'time_limit': 60,  # 默认值
                    'status': 'available' if test.get('status') == 'available' else 'pending',
                    'test_type': test.get('category_id', ''),
                    'can_take_test': test.get('status') == 'available',
                    'test_link': test.get('test_link', test.get('url', '')),
                    'query_time': current_time.isoformat()
                }
                formatted_data['tests'].append(formatted_test)
            
            # 添加统计信息到格式化数据中
            formatted_data['statistics'] = comprehensive_data.get('statistics', {})
            
            return formatted_data
                        
        except Exception as e:
            logger.error(f"格式化增强数据失败: {str(e)}")
            return None
    
    def run_enhanced_scraper(self, user_id=None):
        """
        运行增强版爬虫流程，返回详细的实时数据
        
        Args:
            user_id: 用户ID，如果为None则使用第一个有凭证的用户
            
        Returns:
            dict: 详细的格式化课程数据，如果失败返回None
        """
        try:
            logger.info("🚀 开始运行BUCT增强课程爬虫")
            
            # 步骤1: 登录
            if not self.login(user_id):
                return None
            
            # 步骤2: 获取全面的课程详情
            comprehensive_data = self.get_comprehensive_course_details()
            if not comprehensive_data:
                return None
            
            # 步骤3: 格式化数据并返回
            formatted_data = self.format_enhanced_data(comprehensive_data)
            
            # 输出摘要信息
            if formatted_data:
                stats = formatted_data.get('statistics', {})
                logger.info("📊 爬虫运行完成，数据摘要:")
                logger.info(f"   📚 涉及课程: {stats.get('total_courses', 0)} 门")
                logger.info(f"   📝 待提交作业: {stats.get('pending_assignments', 0)} 个")
                logger.info(f"   🧪 待提交测试: {stats.get('pending_tests', 0)} 个")
                logger.info(f"   ✅ 可进行测试: {stats.get('available_tests', 0)} 个")
                logger.info(f"   📂 有测试的分类: {stats.get('categories_with_tests', 0)} 个")
            
            logger.info("✅ 增强爬虫运行完成，返回详细数据")
            return formatted_data
            
        except Exception as e:
            logger.error(f"增强爬虫运行失败: {str(e)}")
            return None
        finally:
            # 清理资源
            if self.client:
                try:
                    self.client.logout()
                    logger.info("已成功登出BUCT课程平台")
                except Exception as e:
                    logger.warning(f"登出时发生错误: {str(e)}")
            if self.mongo_client:
                self.mongo_client.close()

def get_enhanced_details(user_id=None):
    """
    获取增强课程详情的便捷函数
    
    Args:
        user_id: 用户ID，如果为None则使用第一个有凭证的用户
        
    Returns:
        dict: 详细的格式化课程数据，包含作业、测试和统计信息
    """
    scraper = BUCTScraperEnhanced()
    return scraper.run_enhanced_scraper(user_id)

def get_standard_format_details(user_id=None):
    """
    获取标准格式的课程详情
    
    Args:
        user_id: 用户ID，如果为None则使用第一个有凭证的用户
        
    Returns:
        list: 标准格式的任务列表，格式为:
        [
            {
                "type": "homework" | "test",
                "subject": "课程名称",
                "details": {
                    "task": "任务名称",
                    "deadline": "截止时间",
                    "url": "链接"
                }
            }
        ]
    """
    scraper = BUCTScraperEnhanced()
    try:
        # 登录
        if not scraper.login(user_id):
            return []
        
        # 获取全面数据
        comprehensive_data = scraper.get_comprehensive_course_details()
        if not comprehensive_data:
            return []
        
        # 返回标准格式
        return scraper.format_to_standard_json(comprehensive_data)
        
    except Exception as e:
        logger.error(f"获取标准格式详情失败: {str(e)}")
        return []
    finally:
        # 清理资源
        if scraper.client:
            try:
                scraper.client.logout()
                logger.info("已成功登出BUCT课程平台")
            except Exception as e:
                logger.warning(f"登出时发生错误: {str(e)}")
        if scraper.mongo_client:
            scraper.mongo_client.close()

if __name__ == "__main__":
    import json
    
    # 可以通过命令行参数传入用户ID和格式选择
    user_id = sys.argv[1] if len(sys.argv) > 1 else None
    format_type = sys.argv[2] if len(sys.argv) > 2 else "enhanced"  # enhanced 或 standard
    
    if format_type == "standard":
        # 获取标准格式数据
        result = get_standard_format_details(user_id)
        
        if result:
            print("✅ 标准格式爬虫运行成功")
            print(f"📋 获取到 {len(result)} 个任务")
            print("\n📄 标准JSON格式输出:")
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            print("❌ 标准格式爬虫运行失败")
            sys.exit(1)
    else:
        # 获取增强格式数据
        result = get_enhanced_details(user_id)
        
        if result:
            print("✅ 增强爬虫运行成功")
            print(f"📝 获取到 {len(result.get('assignments', []))} 个作业")
            print(f"🧪 获取到 {len(result.get('tests', []))} 个测试")
            print(f"📊 统计信息: {result.get('statistics', {})}")
            print(f"⏰ 查询时间: {result.get('query_time')}")
            
            # 同时显示标准格式
            standard_format = result.get('standard_format', [])
            if standard_format:
                print(f"📄 标准JSON格式 ({len(standard_format)} 个任务):")
                print(json.dumps(standard_format, ensure_ascii=False, indent=2))
        else:
            print("❌ 增强爬虫运行失败")
            sys.exit(1)