import requests
from bs4 import BeautifulSoup
from pprint import pprint

class Get_Tests():
    def __init__(self):
        pass

    def generate_class_selection(self, order:int):
        return "classicLook" + str(order)

    def get_test_info(self, soup,  order:int):
        class_name = self.generate_class_selection(order)
        print(f"正在提取 class: {class_name}")
        cells = soup.select(f'td.{class_name}')
        if len(cells) != 0:
            title = cells[0].get_text(strip=True) if cells[0].text else ""
            date = cells[1].get_text(strip=True) if len(cells) > 1 and cells[1].text else ""
            diedline = cells[2].get_text(strip=True) if len(cells) > 2 and cells[2].text else ""
            img_tag = cells[-3].find('img', src="../../../../styles/default/image/go.gif")
            print(img_tag)
            if  img_tag:
                state = 1
            else:
                state = 0
            
            return {
                "title": title,
                "date": date,
                "diedline": diedline,
                "state": state
            }
        else:
            return {
                "state": 0
            }

def fliter(lst: list):
    return [i for i in lst if i["state"] == 1]

lst = []
s_id = {
    "" : "34060"
}

sids = s_id.values()


headers = {
    "Cookie": "DWRSESSIONID=EZQ4cO15GFX1hqq$PySARNhN9Ap; JSESSIONID=F6D8502C72A3B4D40D1DBA6C6E90B623.TM2; Hm_lvt_242c27c7689290b81407f20c9264ca25=1757555509; Hm_lpvt_242c27c7689290b81407f20c9264ca25=1757555509; HMACCOUNT=EFE68CEEF080F3B6; Hm_lvt_17b563784d03d91c8d275255939159fc=1757555509; Hm_lpvt_17b563784d03d91c8d275255939159fc=1757555509",
    "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Mobile Safari/537.36 Edg/140.0.0.0"
}

for i in sids:
    url = f"https://course.buct.edu.cn/meol/common/question/test/student/list.jsp?sortColumn=createTime&pagingNumberPer=7&status=1&tagbug=client&sortDirection=-1&strStyle=new03&cateId={i}&pagingPage=3&"
    req = requests.get(url, headers=headers).content.decode('gbk')
    soup = BeautifulSoup(req, 'html.parser')
    
    # 提取所有 td.classicLook0 的内容
    for j in range(0,8):
        lst.append(Get_Tests().get_test_info(soup, j))

lst = fliter(lst)
pprint(lst)