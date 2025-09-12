from bs4 import BeautifulSoup

class CourseUtils:
    def __init__(self, session):
        self.session = session
        self.base_url = "https://course.buct.edu.cn"
    
    def get_pending_tasks(self):
        """获取待办任务列表（作业和测试）"""
        url = f"{self.base_url}/meol/welcomepage/student/interaction_reminder_v8.jsp"
        resp = self.session.get(url)
        soup = BeautifulSoup(resp.text, "html.parser")
        
        result = {"homework": [], "tests": []}
        
        lis = soup.select("#reminder > li")
        for li in lis:
            text = li.get_text(strip=True)
            if "待提交作业" in text:
                result["homework"] = self._extract_course_info(li)
            elif "待提交测试" in text:
                result["tests"] = self._extract_course_info(li)
        
        return result
    
    def _extract_course_info(self, li_element):
        """从li元素中提取课程信息和lid"""
        courses = []
        for c in li_element.select("ul li a"):
            course_name = c.text.strip()
            onclick = c.get("onclick", "")
            lid = None
            if "lid=" in onclick:
                lid = onclick.split("lid=")[1].split("&")[0]
            courses.append((course_name, lid))
        return courses
    
    def get_homework_courses(self):
        """专门获取待提交作业的课程列表"""
        tasks = self.get_pending_tasks()
        return tasks["homework"]
    
    def get_test_courses(self):
        """专门获取待提交测试的课程列表"""
        tasks = self.get_pending_tasks()
        return tasks["tests"]