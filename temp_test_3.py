import requests
from bs4 import BeautifulSoup
import pandas as pd

def parse_exam_table(html_content):
    soup = BeautifulSoup(html_content, "html.parser")
    table = soup.find("table", class_="valuelist")

    exams = []
    if not table:
        return exams

    rows = table.find_all("tr")[1:]  # 跳过表头
    for row in rows:
        cols = row.find_all("td")
        if not cols:
            continue
        
        title = cols[0].get_text(strip=True)
        start_time = cols[1].get_text(strip=True)
        end_time = cols[2].get_text(strip=True)
        times_allowed = cols[3].get_text(strip=True)
        duration = cols[4].get_text(strip=True)

        # 结果链接（如果有）
        result_link = None
        result_tag = cols[-1].find("a")
        if result_tag and "href" in result_tag.attrs:
            result_link = result_tag["href"]

        exams.append({
            "标题": title,
            "开始时间": start_time,
            "截止时间": end_time,
            "允许测试次数": times_allowed,
            "限制用时(分钟)": duration,
            "查看结果链接": result_link
        })

    return exams


if __name__ == "__main__":
    # 假设 HTML 存在本地文件 exam.html
    with open("exam.html", "r", encoding="utf-8") as f:
        html_content = f.read()

    exams = parse_exam_table(html_content)

    # 打印结果
    for exam in exams:
        print(exam)

    # 也可以导出 Excel
    df = pd.DataFrame(exams)
    df.to_excel("考试信息.xlsx", index=False, encoding="utf-8-sig")
    print("已保存到 考试信息.xlsx")
