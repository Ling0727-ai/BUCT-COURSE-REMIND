"""
北化课程平台工具模块
"""

import requests
import datetime
from bs4 import BeautifulSoup

# 处理相对导入问题，支持直接运行和模块导入
try:
    from .exceptions import NetworkError, ParseError
except ImportError:
    # 如果相对导入失败，尝试绝对导入或定义本地异常类
    try:
        from exceptions import NetworkError, ParseError
    except ImportError:
        # 定义本地异常类用于直接运行
        class NetworkError(Exception):
            """网络错误"""
            pass
        
        class ParseError(Exception):
            """解析错误"""
            pass

class CourseUtils:
    """北化课程平台工具类"""
    
    def __init__(self, session):
        """
        初始化课程工具
        
        Args:
            session: requests.Session对象（需要已登录）
        """
        self.session = session
        self.base_url = "https://course.buct.edu.cn"
    
    def get_pending_tasks(self):
        """
        获取待办任务列表（作业和测试）
        
        Returns:
            dict: 包含作业和测试的字典
            {
                'homework': [(课程名, lid), ...],
                'tests': [(课程名, lid), ...]
            }
            
        Raises:
            NetworkError: 网络请求错误
            ParseError: 解析HTML错误
        """
        try:
            url = f"{self.base_url}/meol/welcomepage/student/interaction_reminder_v8.jsp"
            resp = self.session.get(url, timeout=10)
            resp.raise_for_status()
            
            soup = BeautifulSoup(resp.text, "html.parser")
            
            result = {
                "success": True,
                "data": {
                    "homework": [], 
                    "tests": [],
                    "timestamp": datetime.datetime.now().isoformat(),
                    "source_url": url
                }
            }
            
            lis = soup.select("#reminder > li")
            for li in lis:
                text = li.get_text(strip=True)
                if "待提交作业" in text:
                    result["data"]["homework"] = self._extract_course_info(li)
                elif "待提交测试" in text:
                    result["data"]["tests"] = self._extract_course_info(li)
            
            # 添加统计信息
            result["data"]["stats"] = {
                "homework_count": len(result["data"]["homework"]),
                "tests_count": len(result["data"]["tests"]),
                "total_count": len(result["data"]["homework"]) + len(result["data"]["tests"])
            }
            
            return result
            
        except requests.exceptions.RequestException as e:
            raise NetworkError(f"获取待办任务失败: {str(e)}")
        except Exception as e:
            raise ParseError(f"解析待办任务失败: {str(e)}")
    
    def _extract_course_info(self, li_element):
        """
        从li元素中提取课程信息和lid
        
        Args:
            li_element: BeautifulSoup的li元素
            
        Returns:
            list: 包含课程信息的字典列表
        """
        courses = []
        for c in li_element.select("ul li a"):
            course_name = c.text.strip()
            onclick = c.get("onclick", "")
            href = c.get("href", "")
            lid = None
            
            # 尝试多种方式提取课程ID
            # 1. 从onclick属性中提取lid
            if "lid=" in onclick:
                try:
                    lid = onclick.split("lid=")[1].split("&")[0].split("'")[0].split('"')[0]
                except:
                    pass
            
            # 2. 从onclick属性中提取courseId
            if not lid and "courseId=" in onclick:
                try:
                    lid = onclick.split("courseId=")[1].split("&")[0].split("'")[0].split('"')[0]
                except:
                    pass
            
            # 3. 从href属性中提取lid
            if not lid and "lid=" in href:
                try:
                    lid = href.split("lid=")[1].split("&")[0]
                except:
                    pass
            
            # 4. 从href属性中提取courseId
            if not lid and "courseId=" in href:
                try:
                    lid = href.split("courseId=")[1].split("&")[0]
                except:
                    pass
            
            # 5. 尝试从URL路径中提取数字ID
            if not lid:
                import re
                # 尝试匹配各种可能的ID格式
                patterns = [
                    r'lid[=:](\d+)',
                    r'courseId[=:](\d+)', 
                    r'course[Ii]d[=:](\d+)',
                    r'/course/(\d+)/',
                    r'id[=:](\d+)'
                ]
                
                for pattern in patterns:
                    match = re.search(pattern, onclick + " " + href)
                    if match:
                        lid = match.group(1)
                        break
            
            # 过滤掉统计信息，只保留真正的课程
            if self._is_valid_course_name(course_name) and lid and lid.isdigit():
                courses.append({
                    "course_name": course_name,
                    "lid": lid,
                    "url": f"{self.base_url}/meol/common/hw/student/hwtask.jsp?lid={lid}"
                })
            elif not self._is_valid_course_name(course_name):
                # 跳过统计信息，不添加到结果中
                print(f"跳过统计信息: {course_name}")
            else:
                # 如果是有效课程名但无法提取lid，记录调试信息
                print(f"警告: 无法提取课程ID - 课程名: {course_name}, onclick: {onclick[:100]}, href: {href[:100]}")
        return courses
    
    def _is_valid_course_name(self, course_name):
        """
        判断是否为有效的课程名称（过滤掉统计信息）
        
        Args:
            course_name: 课程名称
            
        Returns:
            bool: 是否为有效课程名称
        """
        # 过滤掉统计信息的关键词
        invalid_keywords = [
            "门课程有待提交作业",
            "门课程有待提交测试", 
            "个作业",
            "个测试",
            "统计",
            "总计",
            "共计"
        ]
        
        # 如果课程名称包含这些关键词，认为是统计信息
        for keyword in invalid_keywords:
            if keyword in course_name:
                return False
        
        # 如果课程名称太短或者只包含数字，也可能是统计信息
        if len(course_name.strip()) < 3:
            return False
            
        # 如果课程名称只包含数字和特殊字符，可能是统计信息
        import re
        if re.match(r'^[\d\s\-\+\(\)（）]+$', course_name):
            return False
            
        return True
    
    def get_homework_courses(self):
        """
        专门获取待提交作业的课程列表
        
        Returns:
            list: 课程信息的字典列表
        """
        tasks = self.get_pending_tasks()
        return tasks["homework"]
    
    def get_test_courses(self):
        """
        专门获取待提交测试的课程列表
        
        Returns:
            list: 课程信息的字典列表
        """
        tasks = self.get_pending_tasks()
        return tasks["tests"]
    
    def get_course_details(self, lid):
        """
        获取课程详细信息
        
        Args:
            lid: 课程ID
            
        Returns:
            dict: 课程详细信息
            
        Note: 需要根据具体页面结构实现
        """
        # 这里可以扩展获取课程详细信息的逻辑
        return {"lid": lid, "details": "待实现"}
    
    def set_base_url(self, base_url):
        """设置基础URL（用于测试或其他环境）"""
        self.base_url = base_url.rstrip('/')