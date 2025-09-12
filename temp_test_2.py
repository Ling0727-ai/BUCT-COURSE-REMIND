import requests
from bs4 import BeautifulSoup
import time
import re

session = requests.Session()
# 设置请求头，模拟浏览器行为
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
})

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
        print(f"找到待提交测试: {text}")
        for c in li.select("ul li a"):
            course_name = c.text.strip()
            onclick = c.get("onclick", "")
            href = c.get("href", "")
            lid = None
            if "lid=" in onclick:
                lid = onclick.split("lid=")[1].split("&")[0]
            # 跳过汇总信息（lid为None的）
            if lid:
                print(f"测试课程: {course_name}, lid: {lid}, onclick: {onclick}, href: {href}")
                result["tests"].append((course_name, lid, onclick, href))
            else:
                print(f"跳过汇总信息: {course_name}")

# 分离作业和测试
hw_courses = result["homework"]
t_courses = result["tests"]

# 3. 遍历课程 -> 找作业列表
for cname, lid in hw_courses:
    # 进入课程主页
    course_url = f"https://course.buct.edu.cn/meol/jpk/course/layout/newpage/index.jsp?courseId={lid}"
    c_html = session.get(course_url).text
    csoup = BeautifulSoup(c_html, "html.parser")

    # 找到"课程活动"的 columnId
    act = csoup.find("a", title="课程活动")
    if not act:
        print(f"课程 {cname} 未找到'课程活动'链接，跳过")
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

        link = cols[0].find("a")
        if not link:
            continue
        link_href = link["href"]
        hwtid = link_href.split("hwtid=")[1]

        # 4. 作业详情
        detail_url = f"https://course.buct.edu.cn/meol/common/hw/student/{link_href}"
        d_html = session.get(detail_url).text
        dsoup = BeautifulSoup(d_html, "html.parser")
        content = dsoup.select_one("td.text")
        if content:
            content_text = content.get_text("\n", strip=True)
            print(cname, title, deadline, teacher, content_text[:50], "...")
        else:
            print(cname, title, deadline, teacher, "无内容详情")

# 5. 遍历课程 -> 找测试列表
print(f"找到 {len(t_courses)} 个测试课程")
for idx, test_course in enumerate(t_courses):
    cname, lid, onclick, href = test_course
    print(f"处理测试课程 {idx+1}: {cname}")
    
    # 添加延迟避免频繁访问
    time.sleep(2)
    
    # 直接从onclick中提取测试URL
    if "enter_course.jsp" in onclick and "t=test" in onclick:
        # 解析onclick中的URL
        test_url_match = re.search(r"'(.*?)'", onclick)
        if test_url_match:
            test_url = test_url_match.group(1)
            if test_url.startswith("./"):
                test_url = test_url[2:]  # 移除开头的./
            test_url = f"https://course.buct.edu.cn/meol/{test_url}"
            print(f"直接访问测试URL: {test_url}")
            
            try:
                test_html = session.get(test_url).text
                
                # 检查是否被限制访问
                if "访问过于频繁" in test_html:
                    print(f"检测到访问限制，等待10秒后重试...")
                    time.sleep(10)
                    test_html = session.get(test_url).text
                
                # 保存测试页面内容以便调试
                with open(f"debug_test_{cname}.html", "w", encoding="utf-8") as f:
                    f.write(test_html)
                print(f"已保存测试页面到 debug_test_{cname}.html")
                
                testsoup = BeautifulSoup(test_html, "html.parser")
                
                # 解析测试列表 - 尝试多种表格选择器
                tables = testsoup.select("table.valuelist, table.list, table.table, table")
                if tables:
                    for table in tables:
                        rows = table.select("tr")
                        if len(rows) > 1:  # 至少有表头和数据行
                            print(f"找到 {len(rows)-1} 个测试")
                            for row in rows[1:]:
                                cols = row.find_all("td")
                                if not cols or len(cols) < 2:
                                    continue
                                
                                title = cols[0].get_text(strip=True)
                                deadline = cols[1].get_text(strip=True) if len(cols) > 1 else ""
                                status = cols[-1].get_text(strip=True) if len(cols) > 2 else ""
                                
                                link_tag = cols[0].find("a")
                                if link_tag:
                                    href = link_tag.get("href", "")
                                    if href:
                                        if not href.startswith("http"):
                                            if href.startswith("/"):
                                                href = "https://course.buct.edu.cn" + href
                                            else:
                                                href = f"https://course.buct.edu.cn/meol/common/exam/student/{href}"
                                        
                                        # 添加延迟
                                        time.sleep(1)
                                        
                                        # 获取测试详情
                                        try:
                                            detail_html = session.get(href).text
                                            detailsoup = BeautifulSoup(detail_html, "html.parser")
                                            
                                            # 解析测试详情
                                            desc = ""
                                            desc_tag = detailsoup.select_one("div#examInfo, table.infotable, div.info, div.description")
                                            if desc_tag:
                                                desc = desc_tag.get_text("\n", strip=True)
                                            
                                            print("[测试]", cname, title, deadline, status, desc[:50] + "..." if desc else "")
                                        except Exception as e:
                                            print(f"获取测试详情出错: {e}")
                                else:
                                    print(f"[测试] {cname} - {title} - {deadline} - {status}")
                else:
                    print(f"未找到测试表格，尝试查找测试信息")
                    # 尝试查找测试标题或说明
                    test_elements = testsoup.find_all(string=re.compile(r'测试|考试|exam', re.I))
                    if test_elements:
                        for element in test_elements:
                            parent = element.parent
                            if parent.name == "a" and parent.get("href"):
                                href = parent.get("href")
                                title = element.strip()
                                print(f"[测试] {cname} - {title} - 链接: {href}")
                            elif parent.name in ["div", "td", "li", "span"]:
                                title = element.strip()
                                print(f"[测试] {cname} - {title}")
                    else:
                        print(f"未找到测试信息，页面内容可能已改变")
            except Exception as e:
                print(f"访问测试页面出错: {e}")
        else:
            print(f"无法从onclick中解析URL: {onclick}")
    else:
        print(f"onclick格式不符合预期: {onclick}")
