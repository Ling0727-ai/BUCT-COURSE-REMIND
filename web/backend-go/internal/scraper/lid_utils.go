package scraper

import (
	"fmt"
	"io"
	"net/http"
	"regexp"
	"strings"
	"time"

	"github.com/PuerkitoBio/goquery"
	"golang.org/x/text/encoding/simplifiedchinese"
	"golang.org/x/text/transform"
)

// LidUtils 课程LID获取工具类
type LidUtils struct {
	Client  *http.Client
	BaseURL string
}

// CourseInfo 课程信息结构
type CourseInfo struct {
	CourseName string `json:"course_name"`
	LID        string `json:"lid"`
	CourseID   string `json:"course_id"`
	Type       string `json:"type"`
	URL        string `json:"url"`
}

// PendingTasks 待办任务结构
type PendingTasks struct {
	Homework []CourseInfo `json:"homework"`
	Tests    []CourseInfo `json:"tests"`
}

// NewLidUtils 创建新的LID工具实例
func NewLidUtils(client *http.Client) *LidUtils {
	return &LidUtils{
		Client:  client,
		BaseURL: "https://course.buct.edu.cn",
	}
}

// GetPendingTasks 获取待办任务列表（作业和测试）
func (l *LidUtils) GetPendingTasks() (*PendingTasks, error) {
	url := l.BaseURL + "/meol/welcomepage/student/interaction_reminder_v8.jsp"

	req, err := http.NewRequest("GET", url, nil)
	if err != nil {
		return nil, err
	}

	req.Header.Set("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36")

	resp, err := l.Client.Do(req)
	if err != nil {
		return nil, fmt.Errorf("获取待办任务失败: %v", err)
	}
	defer resp.Body.Close()

	// 读取响应体用于调试
	bodyBytes, err := io.ReadAll(resp.Body)
	if err != nil {
		return nil, fmt.Errorf("读取响应失败: %v", err)
	}

	// 将 GBK 编码转换为 UTF-8
	utf8Reader := transform.NewReader(strings.NewReader(string(bodyBytes)), simplifiedchinese.GBK.NewDecoder())
	utf8Bytes, err := io.ReadAll(utf8Reader)
	if err != nil {
		// 如果转换失败，使用原始内容
		utf8Bytes = bodyBytes
	}
	bodyStr := string(utf8Bytes)

	// 调试日志
	fmt.Printf("待办任务页面响应长度: %d 字节\n", len(bodyStr))
	if len(bodyStr) < 500 {
		fmt.Printf("待办任务页面内容: %s\n", bodyStr)
	}

	doc, err := goquery.NewDocumentFromReader(strings.NewReader(bodyStr))
	if err != nil {
		return nil, fmt.Errorf("解析待办任务失败: %v", err)
	}

	result := &PendingTasks{
		Homework: make([]CourseInfo, 0),
		Tests:    make([]CourseInfo, 0),
	}

	// 查找所有链接用于调试
	allLinks := doc.Find("a[onclick]")
	fmt.Printf("找到 %d 个带onclick的链接\n", allLinks.Length())

	// 查找作业链接 - onclick 包含 &t=hw
	doc.Find("a[onclick*='&t=hw']").Each(func(i int, s *goquery.Selection) {
		onclick, _ := s.Attr("onclick")
		fmt.Printf("作业链接 %d: %s, onclick: %s\n", i, s.Text(), onclick)
		courseInfo := l.extractSingleCourseInfo(s, "homework")
		if courseInfo != nil {
			result.Homework = append(result.Homework, *courseInfo)
		}
	})

	// 查找测试链接 - onclick 包含 &t=test
	doc.Find("a[onclick*='&t=test']").Each(func(i int, s *goquery.Selection) {
		courseInfo := l.extractSingleCourseInfo(s, "test")
		if courseInfo != nil {
			result.Tests = append(result.Tests, *courseInfo)
		}
	})

	return result, nil
}

// GetHomeworkLIDs 专门获取待提交作业的课程LID列表
func (l *LidUtils) GetHomeworkLIDs() ([]CourseInfo, error) {
	tasks, err := l.GetPendingTasks()
	if err != nil {
		return nil, err
	}
	return tasks.Homework, nil
}

// GetTestLIDs 专门获取待提交测试的课程LID列表
func (l *LidUtils) GetTestLIDs() ([]CourseInfo, error) {
	tasks, err := l.GetPendingTasks()
	if err != nil {
		return nil, err
	}
	return tasks.Tests, nil
}

// GetAllCourseLIDs 获取所有课程的LID列表
func (l *LidUtils) GetAllCourseLIDs() ([]CourseInfo, error) {
	url := l.BaseURL + "/meol/homepage/student/index.jsp"

	req, err := http.NewRequest("GET", url, nil)
	if err != nil {
		return nil, err
	}

	req.Header.Set("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36")

	resp, err := l.Client.Do(req)
	if err != nil {
		return nil, fmt.Errorf("获取课程列表失败: %v", err)
	}
	defer resp.Body.Close()

	doc, err := goquery.NewDocumentFromReader(resp.Body)
	if err != nil {
		return nil, fmt.Errorf("解析课程列表失败: %v", err)
	}

	var courses []CourseInfo

	// 查找课程表格
	doc.Find("table.valuelist tr").Each(func(i int, s *goquery.Selection) {
		if i == 0 {
			return // 跳过表头
		}

		titleCell := s.Find("td").First()
		titleLink := titleCell.Find("a")

		if titleLink.Length() > 0 {
			courseName := strings.TrimSpace(titleLink.Text())
			href, exists := titleLink.Attr("href")
			if exists && strings.Contains(href, "courseId=") {
				// 提取课程ID
				lid := extractParam(href, "courseId")
				if lid != "" {
					courseURL := href
					if strings.HasPrefix(href, "/") {
						courseURL = l.BaseURL + href
					}

					courses = append(courses, CourseInfo{
						CourseName: courseName,
						LID:        lid,
						CourseID:   lid,
						Type:       "course",
						URL:        courseURL,
					})
				}
			}
		}
	})

	return courses, nil
}

// FindLIDByCourseName 根据课程名称查找对应的LID
func (l *LidUtils) FindLIDByCourseName(courseName string) (string, error) {
	courses, err := l.GetAllCourseLIDs()
	if err != nil {
		return "", err
	}

	courseNameLower := strings.ToLower(courseName)
	for _, course := range courses {
		if strings.Contains(strings.ToLower(course.CourseName), courseNameLower) {
			return course.LID, nil
		}
	}

	return "", nil
}

// extractSingleCourseInfo 从单个链接元素中提取课程信息
func (l *LidUtils) extractSingleCourseInfo(s *goquery.Selection, expectedType string) *CourseInfo {
	courseName := strings.TrimSpace(s.Text())
	onclick, exists := s.Attr("onclick")
	if !exists || !strings.Contains(onclick, "lid=") {
		return nil
	}

	// 提取LID
	lid := extractParamFromOnclick(onclick, "lid")
	if lid == "" {
		return nil
	}

	// 验证类型
	if expectedType == "homework" && !strings.Contains(onclick, "&t=hw") {
		return nil
	} else if expectedType == "test" && !strings.Contains(onclick, "&t=test") {
		return nil
	}

	// 过滤掉汇总信息
	if strings.Contains(courseName, "门课程") && strings.Contains(courseName, "待提交") {
		return nil
	}

	// 过滤掉特定的测试课程LID
	if expectedType == "test" && (lid == "24199" || lid == "27215") {
		return nil
	}

	// 根据类型生成不同的URL
	var courseURL string
	if expectedType == "test" {
		courseURL = fmt.Sprintf("%s/meol/common/question/test/student/list.jsp?sortColumn=createTime&status=1&tagbug=client&sortDirection=-1&strStyle=new03&cateId=%s&pagingPage=1&pagingNumberPer=30", l.BaseURL, lid)
	} else {
		courseURL = fmt.Sprintf("%s/meol/jpk/course/layout/newpage/index.jsp?courseId=%s", l.BaseURL, lid)
	}

	return &CourseInfo{
		CourseName: courseName,
		LID:        lid,
		CourseID:   lid,
		Type:       expectedType,
		URL:        courseURL,
	}
}

// extractParam 从URL中提取参数
func extractParam(url, paramName string) string {
	pattern := regexp.MustCompile(paramName + `=([^&]+)`)
	matches := pattern.FindStringSubmatch(url)
	if len(matches) >= 2 {
		return matches[1]
	}
	return ""
}

// extractParamFromOnclick 从onclick属性中提取参数
func extractParamFromOnclick(onclick, paramName string) string {
	pattern := regexp.MustCompile(paramName + `=([^&'"]+)`)
	matches := pattern.FindStringSubmatch(onclick)
	if len(matches) >= 2 {
		return matches[1]
	}
	return ""
}

// makeRequest 发起HTTP请求
func makeRequest(client *http.Client, url, referer string) (*goquery.Document, error) {
	req, err := http.NewRequest("GET", url, nil)
	if err != nil {
		return nil, err
	}

	req.Header.Set("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36")
	if referer != "" {
		req.Header.Set("Referer", referer)
	}

	// 添加延迟避免请求过快
	time.Sleep(300 * time.Millisecond)

	resp, err := client.Do(req)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	// 读取响应体
	body, err := io.ReadAll(resp.Body)
	if err != nil {
		return nil, err
	}

	// 将 GBK 编码转换为 UTF-8
	// 北化课程平台使用 GBK 编码
	utf8Reader := transform.NewReader(strings.NewReader(string(body)), simplifiedchinese.GBK.NewDecoder())
	utf8Body, err := io.ReadAll(utf8Reader)
	if err != nil {
		// 如果转换失败，尝试使用原始内容
		return goquery.NewDocumentFromReader(strings.NewReader(string(body)))
	}

	return goquery.NewDocumentFromReader(strings.NewReader(string(utf8Body)))
}
