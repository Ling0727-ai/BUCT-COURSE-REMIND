import requests
from lxml import etree
from pprint import pprint

s_id = {
    "subject" : "19284"
}

sids = s_id.values()


headers = {
    "Cookie": "JSESSIONID=BE745AFE5A05EAABE344C1F74285F8D4.TM2; DWRSESSIONID=8XaxDGAPz11icl8t42$SGeDsZAp",
    "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Mobile Safari/537.36 Edg/140.0.0.0"
}

for i in sids:
    url = f"https://course.buct.edu.cn/meol/common/question/test/student/list.jsp?tagbug=client&cateId={i}&status=1&strStyle=new03"
    req = requests.get(url,headers=headers).text
    tree = etree.HTML(req)
    title = tree.xpath("/html/body/div/table/tbody/tr[2]/td[1]/text()")
    stu = tree.xpath("/html/body/div/table/tbody/tr[2]/td[8]")
    print(req)

    print(title,stu)