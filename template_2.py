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

# 解析作业
hw_courses = []
for li in soup.select("li a[onclick*='t=hw']"):
    course_name = li.get_text(strip=True)
    href = li["onclick"]  # 里面有 lid=xxxx
    lid = href.split("lid=")[1].split("&")[0]
    hw_courses.append((course_name, lid))

# 3. 遍历课程 -> 找作业列表
for cname, lid in hw_courses:
    # 进入课程主页
    course_url = f"https://course.buct.edu.cn/meol/jpk/course/layout/newpage/index.jsp?courseId={lid}"
    c_html = session.get(course_url).text
    csoup = BeautifulSoup(c_html, "html.parser")

    # 找到“课程活动”的 columnId
    act = csoup.find("a", title="课程活动")
    column_id = act["href"].split("columnId=")[1]

    # 跳转到作业列表
    task_list_url = f"https://course.buct.edu.cn/meol/jpk/course/course_column_preview_transfer.jsp?columnId={column_id}"
    task_page = session.get(task_list_url).text
    tsoup = BeautifulSoup(task_page, "html.parser")

    # 解析表格
    for row in tsoup.select("table.valuelist tr")[1:]:
        cols = row.find_all("td")
        if not cols: continue
        title = cols[0].get_text(strip=True)
        deadline = cols[1].get_text(strip=True)
        teacher = cols[3].get_text(strip=True)

        link = cols[0].find("a")["href"]
        hwtid = link.split("hwtid=")[1]

        # 4. 作业详情
        detail_url = f"https://course.buct.edu.cn/meol/common/hw/student/{link}"
        d_html = session.get(detail_url).text
        dsoup = BeautifulSoup(d_html, "html.parser")
        content = dsoup.select_one("td.text").get_text("\n", strip=True)

        print(cname, title, deadline, teacher, content[:50], "...")
