# web/backend/app/scraper.py

import logging
from threading import Lock
from buct_course import BUCTClient
from bson import ObjectId

# 导入mongo实例，以便查询数据库
from . import mongo
from .model import User

# 配置日志
logger = logging.getLogger(__name__)

class BUCTScraperEnhanced:
    """
    一个增强的BUCT课程信息抓取器。
    - 使用新版 buct_course 库。
    - 为每个用户动态登录和抓取数据。
    - 管理 BUCTClient 实例。
    """
    def __init__(self):
        self.clients = {}  # 使用字典为每个用户管理一个BUCTClient实例
        self.lock = Lock()
        logger.info("BUCTScraperEnhanced 初始化完成")

    def _get_client(self, user_id):
        """为指定用户获取或创建一个BUCTClient实例"""
        with self.lock:
            if user_id not in self.clients:
                self.clients[user_id] = BUCTClient()
                logger.info(f"为用户 {user_id} 创建了新的 BUCTClient 实例")
            return self.clients[user_id]

    def _get_user_credentials(self, user_id):
        """从数据库获取用户的学号和密码"""
        try:
            user = mongo.db.users.find_one({'_id': ObjectId(user_id)})
            if not user:
                logger.error(f"未在数据库中找到用户: {user_id}")
                return None, None
            
            student_id = user.get('student_id')
            encrypted_s_password = user.get('s_password')

            if not student_id or not encrypted_s_password:
                logger.warning(f"用户 {user_id} 未设置学号或密码")
                return None, None
            
            # 创建User模型实例来解密密码
            user_model = User(mongo.db)
            s_password = user_model.get_decrypted_s_password(user)
            
            if not s_password:
                logger.error(f"用户 {user_id} 密码解密失败")
                return None, None
            
            return student_id, s_password
        except Exception as e:
            logger.error(f"从数据库获取用户 {user_id} 凭证时出错: {e}")
            return None, None

    def _format_deadline(self, deadline_str):
        """
        格式化截止时间
        将 '2025年9月23日 23:59:00' 格式转换为 '2025-09-23 23:59:00' 格式
        """
        if not deadline_str:
            return ""
        
        try:
            from datetime import datetime
            # 解析中文时间格式
            dt = datetime.strptime(deadline_str, '%Y年%m月%d日 %H:%M:%S')
            # 转换为标准格式
            return dt.strftime('%Y-%m-%d %H:%M:%S')
        except ValueError as e:
            logger.warning(f"时间格式解析失败: {deadline_str}, 错误: {e}")
            # 如果解析失败，返回原始字符串
            return deadline_str

    def _format_test_deadline(self, deadline_str):
        """
        格式化测试截止时间
        测试时间可能是多种格式，需要统一转换为标准格式
        """
        if not deadline_str:
            return ""
        
        try:
            from datetime import datetime
            
            # 尝试解析不同的时间格式
            formats_to_try = [
                '%Y-%m-%d %H:%M:%S',  # 2025-12-14 23:59:00
                '%Y年%m月%d日 %H:%M:%S',  # 2025年12月14日 23:59:00
                '%Y-%m-%dT%H:%M:%S',  # ISO格式
                '%Y-%m-%dT%H:%M:%SZ',  # ISO格式带Z
            ]
            
            for fmt in formats_to_try:
                try:
                    dt = datetime.strptime(deadline_str.replace('Z', ''), fmt)
                    return dt.strftime('%Y-%m-%d %H:%M:%S')
                except ValueError:
                    continue
            
            # 如果所有格式都失败，返回原始字符串
            logger.warning(f"测试时间格式无法解析: {deadline_str}")
            return deadline_str
            
        except Exception as e:
            logger.warning(f"测试时间格式解析异常: {deadline_str}, 错误: {e}")
            return deadline_str

    def auto_login(self, user_id):
        """
        使用数据库中的凭证为指定用户自动登录。
        如果已经登录，则跳过。
        """
        client = self._get_client(user_id)
        if client.auth.is_logged_in():
            logger.info(f"用户 {user_id} 已登录，跳过自动登录")
            return True, "已登录"

        student_id, s_password = self._get_user_credentials(user_id)
        if not student_id or not s_password:
            return False, "未找到用户凭证"

        logger.info(f"尝试为用户 {user_id} (学号: {student_id}) 登录...")
        try:
            login_success = client.login(student_id, s_password)
            if login_success:
                logger.info(f"用户 {user_id} 登录成功")
                return True, "登录成功"
            else:
                logger.warning(f"用户 {user_id} 登录失败")
                return False, "登录失败，请检查学号和密码"
        except Exception as e:
            logger.error(f"用户 {user_id} 登录时发生异常: {e}", exc_info=True)
            return False, f"登录异常: {e}"

    def get_pending_tasks(self, user_id):
        """
        获取指定用户的待办作业和测试列表。
        返回格式：
        {
          subject: '',  # 科目
          title: '',    # 作业的title / 测试的title
          deadline: "", # 截止时间
          details: "",  # 只有作业需要加，内容为具体的作业详情信息
          url: ""       # 链接
        }
        """
        logger.info(f"开始为用户 {user_id} 获取待办任务...")
        
        login_ok, message = self.auto_login(user_id)
        if not login_ok:
            return {'success': False, 'error': message}
            
        client = self._get_client(user_id)
        if not client.course_utils or not client.test_utils:
             raise RuntimeError("客户端未完全初始化，缺少 course_utils 或 test_utils。")

        try:
            logger.info(f"正在为用户 {user_id} 获取详细作业...")
            # 1. 获取详细作业
            homework_courses = client.course_utils.get_pending_homework()
            formatted_tasks = []
            
            for course in homework_courses:
                lid = course.get('lid')
                course_name = course.get('course_name', '未知课程')
                if not lid: continue
                
                try:
                    course_details = client.course_utils.get_course_details(lid)
                    for hw in course_details.get('homework_list', []):
                        if hw.get('can_submit', False):
                            # 获取作业详细信息
                            details_text = ""
                            if hw.get('detail_href'):
                                try:
                                    tasks = client.course_utils.get_homework_tasks(hw['detail_href'])
                                    if tasks:
                                        details_text = ''.join(tasks)
                                except Exception as e:
                                    logger.warning(f"获取作业详情失败: {e}")
                                    details_text = hw.get('title', '')
                            
                            # 获取并处理截止时间
                            deadline = hw.get('deadline', '')
                            logger.info(f"作业 '{hw.get('title', '未知作业')}' 原始截止时间: {deadline}")
                            
                            # 转换时间格式：从 '2025年9月23日 23:59:00' 转换为标准格式
                            formatted_deadline = self._format_deadline(deadline)
                            logger.info(f"作业 '{hw.get('title', '未知作业')}' 格式化后截止时间: {formatted_deadline}")
                            
                            # 构造标准格式
                            # 生成作业链接
                            homework_url = f"https://course.buct.edu.cn/meol/jpk/course/layout/newpage/index.jsp?courseId={lid}"
                            
                            task_info = {
                                'subject': course_name,
                                'title': hw.get('title', '未知作业'),
                                'deadline': formatted_deadline,
                                'details': details_text,
                                'url': homework_url,
                                'type': 'homework'  # 内部标识
                            }
                            formatted_tasks.append(task_info)
                            logger.info(f"✅ 添加作业: {task_info['subject']} - {task_info['title']} (截止: {task_info['deadline']})")
                            
                except Exception as e:
                    logger.error(f"获取课程 {course_name} 作业详情失败: {e}")

            logger.info(f"正在为用户 {user_id} 获取详细测试...")
            # 2. 获取详细测试
            test_courses_raw = client.test_utils.get_pending_tests()
            logger.info(f"从库获取的原始测试课程数量: {len(test_courses_raw) if test_courses_raw else 0}")
            logger.info(f"原始测试课程详情: {test_courses_raw}")
            
            if test_courses_raw:
                test_courses = client.test_utils.filter_tests(test_courses_raw)
                logger.info(f"过滤后的测试课程数量: {len(test_courses) if test_courses else 0}")
                logger.info(f"过滤后的测试课程: {test_courses}")
                
                for course in test_courses:
                    lid = course.get('lid')
                    course_name = course.get('course_name', '未知课程')
                    logger.info(f"处理测试课程: {course_name} (LID: {lid})")
                    
                    if not lid: 
                        logger.warning(f"课程 {course_name} 没有LID，跳过")
                        continue
                    
                    try:
                        logger.info(f"正在获取课程 '{course_name}' (LID: {lid}) 的测试列表...")
                        test_list_data = client.test_utils.get_test_list(lid)
                        logger.info(f"从 get_test_list 收到的数据结构: {type(test_list_data)}")
                        logger.info(f"测试列表数据: {test_list_data}")
                        
                        # 使用原始课程名称，不使用test_list_data中可能不准确的course_name
                        actual_course_name = course_name
                        test_list = test_list_data.get('test_list', [])
                        
                        logger.info(f"课程 '{actual_course_name}' 原始测试数量: {len(test_list)}")
                        
                        # 处理所有测试，根据时间和状态判断是否显示
                        from datetime import datetime
                        current_time = datetime.now()
                        
                        for i, test in enumerate(test_list):
                            logger.info(f"处理测试 {i+1}: {test}")
                            
                            # 检查测试状态和时间
                            can_start = test.get('can_start', False)
                            status = test.get('status', '未知')
                            start_time_str = test.get('start_time', '')
                            end_time_str = test.get('end_time', '')
                            
                            logger.info(f"测试状态: can_start={can_start}, status={status}")
                            logger.info(f"测试时间: start={start_time_str}, end={end_time_str}")
                            
                            # 判断测试是否应该显示
                            should_show = False
                            
                            # 如果可以开始，直接显示
                            if can_start:
                                should_show = True
                                logger.info("✅ 测试可以开始")
                            else:
                                # 检查是否在有效时间范围内且未完成
                                try:
                                    if start_time_str and end_time_str:
                                        # 解析时间
                                        if 'T' in start_time_str:
                                            start_time = datetime.fromisoformat(start_time_str.replace('Z', '+00:00'))
                                        else:
                                            start_time = datetime.strptime(start_time_str, '%Y-%m-%d %H:%M:%S')
                                        
                                        if 'T' in end_time_str:
                                            end_time = datetime.fromisoformat(end_time_str.replace('Z', '+00:00'))
                                        else:
                                            end_time = datetime.strptime(end_time_str, '%Y-%m-%d %H:%M:%S')
                                        
                                        # 检查是否在时间范围内
                                        if start_time <= current_time <= end_time:
                                            # 检查是否未完成 (status != '已完成' 且 score 为空)
                                            score = test.get('score', '').strip()
                                            if not score and status != '已完成':
                                                should_show = True
                                                logger.info("✅ 测试在有效时间内且未完成")
                                            else:
                                                logger.info(f"❌ 测试已完成 (score={score}, status={status})")
                                        else:
                                            logger.info(f"❌ 测试不在有效时间内 (当前: {current_time})")
                                    else:
                                        logger.info("❌ 测试缺少时间信息")
                                except Exception as e:
                                    logger.warning(f"解析测试时间失败: {e}")
                            
                            if should_show:
                                # 构造测试URL
                                test_url = ""
                                # 生成测试链接
                                test_url = f"https://course.buct.edu.cn/meol/common/question/test/student/list.jsp?sortColumn=createTime&status=1&tagbug=client&sortDirection=-1&strStyle=new03&cateId={lid}&pagingPage=1&pagingNumberPer=30"
                                
                                # 生成测试标题 - 优先使用测试的具体标题
                                test_title = test.get('title')
                                if test_title:
                                    # 如果有具体的测试标题，使用原始课程名称 + 测试标题
                                    test_title = f"{course_name} - {test_title}"
                                else:
                                    # 如果没有测试标题，使用原始课程名称 + 默认格式
                                    test_title = f"{course_name}测试{i+1}"
                                
                                # 格式化测试截止时间
                                formatted_end_time = self._format_test_deadline(end_time_str)
                                logger.info(f"测试 '{test_title}' 格式化后截止时间: {formatted_end_time}")
                                
                                # 构造标准格式
                                task_info = {
                                    'subject': course_name,
                                    'title': test_title,
                                    'deadline': formatted_end_time,
                                    'details': "",  # 测试不需要details字段
                                    'url': test_url,
                                    'type': 'test'  # 内部标识
                                }
                                formatted_tasks.append(task_info)
                                logger.info(f"✅ 添加测试: {task_info['subject']} - {task_info['title']} (截止: {task_info['deadline']})")
                            else:
                                logger.info(f"❌ 跳过测试: {test.get('title', '未知测试')}")
                                
                    except Exception as e:
                        logger.error(f"获取课程 {course_name} 测试列表失败: {e}", exc_info=True)
            else:
                logger.warning("没有获取到任何测试课程")

            # 3. 构造返回数据
            homework_tasks = [task for task in formatted_tasks if task['type'] == 'homework']
            test_tasks = [task for task in formatted_tasks if task['type'] == 'test']
            
            # 移除内部标识字段
            for task in formatted_tasks:
                task.pop('type', None)
            
            response_data = {
                "tasks": formatted_tasks,
                "stats": {
                    "homework_count": len(homework_tasks),
                    "tests_count": len(test_tasks),
                    "total_count": len(formatted_tasks)
                }
            }
            
            logger.info(f"成功获取用户 {user_id} 的数据: {response_data['stats']}")
            return {'success': True, 'data': response_data}

        except Exception as e:
            logger.error(f"为用户 {user_id} 获取待办任务时发生异常: {e}", exc_info=True)
            self.logout(user_id)
            return {'success': False, 'error': f"获取数据时发生异常: {e}"}

    def logout(self, user_id):
        """
        登出指定用户的会话并清理资源。
        """
        with self.lock:
            if user_id in self.clients:
                client = self.clients.pop(user_id)
                try:
                    if client:
                        client.logout()
                        logger.info(f"成功登出用户 {user_id} 的会话")
                except Exception as e:
                    logger.error(f"登出用户 {user_id} 的会话时出错: {e}")
                logger.info(f"用户 {user_id} 的 scraper 客户端已清理")
                return True
        logger.warning(f"尝试登出未找到客户端的用户: {user_id}")
        return False

# --- 单例模式 ---
_scraper_instance = None
_scraper_lock = Lock()

def get_scraper():
    """
    获取 BUCTScraperEnhanced 的单例。
    """
    global _scraper_instance
    with _scraper_lock:
        if _scraper_instance is None:
            _scraper_instance = BUCTScraperEnhanced()
            logger.info("创建了全局 scraper 实例")
    return _scraper_instance