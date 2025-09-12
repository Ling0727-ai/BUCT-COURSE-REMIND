import requests
from bs4 import BeautifulSoup

USERNAME = "***REMOVED***"
PASSWORD = "***REMOVED***"

# 基础 URL
BASE_URL = "https://course.buct.edu.cn"
LOGIN_PAGE = BASE_URL + "/meol/index.do"
LOGIN_URL = BASE_URL + "/meol/loginCheck.do?menuId=1063"
HOME_URL = BASE_URL + "/meol/personal.do"

def login_and_fetch():
    session = requests.Session()

    # 先访问登录页，拿 logintoken
    r = session.get(LOGIN_PAGE)
    soup = BeautifulSoup(r.text, "html.parser")
    token = soup.find("input", {"name": "logintoken"})["value"]

    payload = {
        "IPT_LOGINUSERNAME": USERNAME,
        "IPT_LOGINPASSWORD": PASSWORD,
        "IPT_URL": "",
        "enterLid": "",
        "logintoken": token,
    }

    resp = session.post(LOGIN_URL, data=payload)

    # 判断是否登录成功
    if "login" in resp.url or "错误" in resp.text:
        print("❌ 登录失败")
        return

    print("✅ 登录成功")

    # 访问个人主页
    home = session.get(HOME_URL)
    with open("personal.html", "w", encoding="utf-8") as f:
        f.write(home.text)
    print("👉 已保存 personal.html")

if __name__ == "__main__":
    login_and_fetch()
