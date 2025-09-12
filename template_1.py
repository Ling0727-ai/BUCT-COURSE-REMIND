import requests
from bs4 import BeautifulSoup

USERNAME = "***REMOVED***"
PASSWORD = "***REMOVED***"

BASE_URL = "https://course.buct.edu.cn"
LOGIN_PAGE = BASE_URL + "/meol/index.do"
LOGIN_URL = BASE_URL + "/meol/loginCheck.do?menuId=1063"
REMINDER_URL = BASE_URL + "/meol/welcomepage/student/interaction_reminder_v8.jsp"

def fetch_reminders():
    session = requests.Session()

    # 1. 拿 token
    r = session.get(LOGIN_PAGE)
    soup = BeautifulSoup(r.text, "html.parser")
    token = soup.find("input", {"name": "logintoken"})["value"]

    # 2. 登录
    payload = {
        "IPT_LOGINUSERNAME": USERNAME,
        "IPT_LOGINPASSWORD": PASSWORD,
        "IPT_URL": "",
        "enterLid": "",
        "logintoken": token,
    }
    session.post(LOGIN_URL, data=payload)

    # 3. 抓取互动提醒页面
    resp = session.get(REMINDER_URL)
    soup = BeautifulSoup(resp.text, "html.parser")

    result = {"homework": [], "tests": []}

    # 找到所有 li
    lis = soup.select("#reminder > li")
    for li in lis:
        text = li.get_text(strip=True)
        if "待提交作业" in text:
            for c in li.select("ul li a"):
                course = c.text.strip()
                # 解析 onclick 里的 lid
                onclick = c.get("onclick", "")
                lid = None
                if "lid=" in onclick:
                    lid = onclick.split("lid=")[1].split("&")[0]
                result["homework"].append({"course": course, "lid": lid})
        elif "待提交测试" in text:
            for c in li.select("ul li a"):
                course = c.text.strip()
                onclick = c.get("onclick", "")
                lid = None
                if "lid=" in onclick:
                    lid = onclick.split("lid=")[1].split("&")[0]
                result["tests"].append({"course": course, "lid": lid})

    return result

if __name__ == "__main__":
    data = fetch_reminders()
    print("待提交作业：")
    for hw in data["homework"]:
        print(f"- {hw['course']} (lid={hw['lid']})")

    print("\n待提交测试：")
    for t in data["tests"]:
        print(f"- {t['course']} (lid={t['lid']})")
