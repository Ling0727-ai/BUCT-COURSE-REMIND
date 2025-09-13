"""
北化课程平台工具模块
"""

import requests
import datetime
from bs4 import BeautifulSoup
from .exceptions import NetworkError, ParseError

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
            lid = None
            if "lid=" in onclick:
                lid = onclick.split("lid=")[1].split("&")[0]
            
            courses.append({
                "course_name": course_name,
                "lid": lid,
                "url": f"{self.base_url}/meol/common/hw/student/hwtask.jsp?lid={lid}" if lid else None
            })
        return courses
    
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