import requests
from bs4 import BeautifulSoup

session = requests.Session()

# 1. 登录
session.post("https://course.buct.edu.cn/meol/loginCheck.do", data={
    "IPT_LOGINUSERNAME": "***REMOVED***",
    "IPT_LOGINPASSWORD": "***REMOVED***"
})

# 2. 获取待办列表
resp = session.get("https://course.buct.edu.cn/meol/welcomepage/student/interaction_reminder_v8.jsp")
soup = BeautifulSoup(resp.text, "html.parser")

# 初始化结果字典
result = {"homework": [], "tests": []}

# 找到所有 li
lis = soup.select("#reminder > li")
for li in lis:
    text = li.get_text(strip=True)
    if "待提交作业" in text:
        for c in li.select("ul li a"):
            course_name = c.text.strip()
            # 解析 onclick 里的 lid
            onclick = c.get("onclick", "")
            lid = None
            if "lid=" in onclick:
                lid = onclick.split("lid=")[1].split("&")[0]
            result["homework"].append((course_name, lid))
    elif "待提交测试" in text:
        for c in li.select("ul li a"):
            course_name = c.text.strip()
            onclick = c.get("onclick", "")
            lid = None
            if "lid=" in onclick:
                lid = onclick.split("lid=")[1].split("&")[0]
            result["tests"].append((course_name, lid))

# 分离作业和测试
hw_courses = result["homework"]
t_courses = result["tests"]

# 原来的 hw_courses 变量保持不变，新增 t_courses 变量
print("待提交作业:", hw_courses)
print("待提交测试:", t_courses)
