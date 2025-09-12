import requests
from bs4 import BeautifulSoup
import pandas as pd

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

# 3. 遍历课程 -> 找作业列表
for cname, lid in hw_courses:
    # 进入课程主页
    course_url = f"https://course.buct.edu.cn/meol/jpk/course/layout/newpage/index.jsp?courseId={lid}"
    c_html = session.get(course_url).text
    csoup = BeautifulSoup(c_html, "html.parser")

    # 找到“课程活动”的 columnId
    act = csoup.find("a", title="课程活动")
    if act is None or "href" not in act.attrs:
        print(f"Warning: Could not find '课程活动' link for course {cname}")
        continue
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

# 5. 遍历课程 -> 找测试列表
for cname, lid in t_courses:
    # 进入课程主页
    course_url = f"https://course.buct.edu.cn/meol/jpk/course/layout/newpage/index.jsp?courseId={lid}"
    c_html = session.get(course_url).text
    csoup = BeautifulSoup(c_html, "html.parser")

    # 找到“在线测试”的 columnId
    test = csoup.find("a", string="在线测试")
    if not test:
        continue
    column_id = test["href"].split("columnId=")[1]

    # 跳转到测试列表
    test_list_url = f"https://course.buct.edu.cn/meol/jpk/course/course_column_preview_transfer.jsp?columnId={column_id}"
    test_page = session.get(test_list_url).text
    tsoup = BeautifulSoup(test_page, "html.parser")

    # 解析测试表格 - 使用 ttt.py 的逻辑
    table = tsoup.find("table")
    if not table:
        print(f"未找到测试表格，课程: {cname}")
        continue

    exams = []
    rows = table.find_all("tr")[1:]  # 跳过表头

    for row in rows:
        cols = row.find_all("td")
        if len(cols) < 5:
            continue  # 跳过非数据行

        # 提取考试信息 - 按照 ttt.py 的逻辑
        title = cols[0].get_text(strip=True)
        start_time = cols[1].get_text(strip=True)
        end_time = cols[2].get_text(strip=True)
        times_allowed = cols[3].get_text(strip=True)
        time_limit = cols[4].get_text(strip=True)

        # 查看结果链接
        result_link = None
        result_tag = cols[-1].find("a")
        if result_tag:
            result_link = result_tag["href"]

        # 获取测试详情（如果需要）
        link = cols[0].find("a")
        if link and "href" in link.attrs:
            detail_url = f"https://course.buct.edu.cn/meol/exam/student/{link['href']}"
            d_html = session.get(detail_url).text
            dsoup = BeautifulSoup(d_html, "html.parser")
            desc = dsoup.select_one("td.text")
            desc_text = desc.get_text("\n", strip=True) if desc else "(无详细说明)"
        else:
            desc_text = "(无法获取详情)"

        # 打印结果 - 保持原有格式但使用新字段
        print(cname, title, start_time, end_time, times_allowed, time_limit, desc_text[:50], "...")
        
        exams.append({
            "课程名称": cname,
            "考试标题": title,
            "开始时间": start_time,
            "截止时间": end_time,
            "允许次数": times_allowed,
            "限制用时": time_limit,
            "结果链接": result_link,
            "详细说明": desc_text
        })

