package scraper

import (
	"fmt"
	"net/http"
	"regexp"
	"strings"

	"github.com/PuerkitoBio/goquery"
)

// TestUtils 北化课程平台测试工具类
type TestUtils struct {
	Client   *http.Client
	BaseURL  string
	LidUtils *LidUtils
}

// TestInfo 测试信息结构
type TestInfo struct {
	Title           string `json:"title"`
	TestID          string `json:"test_id"`
	StartTime       string `json:"start_time"`
	EndTime         string `json:"end_time"`
	AllowedAttempts string `json:"allowed_attempts"`
	Duration        string `json:"duration"`
	CanStart        bool   `json:"can_start"`
	StartHref       string `json:"start_href"`
	SubmitStatus    string `json:"submit_status"`
	ResultHref      string `json:"result_href"`
	HasResult       bool   `json:"has_result"`
	Status          string `json:"status"`
	TestLink        string `json:"test_link,omitempty"`
	CourseName      string `json:"course_name,omitempty"`
}

// TestDetails 测试详情结构
type TestDetails struct {
	CourseName string     `json:"course_name"`
	LID        string     `json:"lid"`
	TestList   []TestInfo `json:"test_list"`
	TotalCount int        `json:"total_count"`
}

// TestDetail 单个测试详细信息
type TestDetail struct {
	TestID        string `json:"test_id"`
	Title         string `json:"title"`
	Description   string `json:"description"`
	StartTime     string `json:"start_time"`
	EndTime       string `json:"end_time"`
	Duration      string `json:"duration"`
	TotalScore    string `json:"total_score"`
	QuestionCount string `json:"question_count"`
	Instructions  string `json:"instructions"`
	TestURL       string `json:"test_url"`
}

// NewTestUtils 创建新的测试工具实例
func NewTestUtils(client *http.Client) *TestUtils {
	return &TestUtils{
		Client:   client,
		BaseURL:  "https://course.buct.edu.cn",
		LidUtils: NewLidUtils(client),
	}
}

// GetPendingTests 获取待提交测试列表
func (t *TestUtils) GetPendingTests() ([]CourseInfo, error) {
	return t.LidUtils.GetTestLIDs()
}

// GetTestList 获取指定课程的测试列表
func (t *TestUtils) GetTestList(lid string) (*TestDetails, error) {
	testURL := fmt.Sprintf(
		"%s/meol/common/question/test/student/list.jsp?sortColumn=createTime&status=1&tagbug=client&sortDirection=-1&strStyle=lesson19&cateId=%s&pagingPage=1&pagingNumberPer=7",
		t.BaseURL, lid)

	referer := fmt.Sprintf("%s/meol/jpk/course/layout/newpage/index.jsp?courseId=%s", t.BaseURL, lid)

	doc, err := makeRequest(t.Client, testURL, referer)
	if err != nil {
		return nil, fmt.Errorf("获取测试列表失败: %v", err)
	}

	return t.parseTestTable(doc, lid), nil
}

// GetTestDetail 获取单个测试的详细信息
func (t *TestUtils) GetTestDetail(testID string) (*TestDetail, error) {
	detailURL := fmt.Sprintf("%s/meol/common/question/test/student/view.jsp?testId=%s", t.BaseURL, testID)
	referer := t.BaseURL + "/meol/common/question/test/student/list.jsp"

	doc, err := makeRequest(t.Client, detailURL, referer)
	if err != nil {
		return nil, fmt.Errorf("获取测试详情失败: %v", err)
	}

	return t.parseTestDetail(doc, testID), nil
}

// FilterTests 过滤测试列表，移除不需要的项目
func (t *TestUtils) FilterTests(testCourses []CourseInfo) []CourseInfo {
	var filteredTests []CourseInfo

	for _, course := range testCourses {
		courseName := course.CourseName

		// 过滤逻辑：移除汇总信息和无效项目
		if course.LID != "" &&
			!(strings.Contains(courseName, "门课程") && strings.Contains(courseName, "待提交")) &&
			strings.TrimSpace(courseName) != "" {
			filteredTests = append(filteredTests, course)
		}
	}

	return filteredTests
}

// FilterAvailableTests 过滤测试列表，只保留可以进行的测试
func (t *TestUtils) FilterAvailableTests(testList []TestInfo) []TestInfo {
	var availableTests []TestInfo

	for _, test := range testList {
		// 只保留可以开始的测试
		if test.CanStart {
			availableTests = append(availableTests, test)
		}
	}

	return availableTests
}

// parseTestTable 解析测试列表表格
func (t *TestUtils) parseTestTable(doc *goquery.Document, lid string) *TestDetails {
	var testList []TestInfo
	courseName := "未知课程"

	// 尝试从页面中获取课程名称
	titleElem := doc.Find("title")
	if titleElem.Length() > 0 {
		titleText := strings.TrimSpace(titleElem.Text())
		if strings.Contains(titleText, "测试") {
			courseName = strings.Replace(titleText, "测试", "", -1)
			courseName = strings.TrimSpace(courseName)
		}
	}

	// 查找测试列表表格
	table := doc.Find("table.valuelist")
	if table.Length() == 0 {
		// 尝试其他可能的表格选择器
		table = doc.Find("table[border='0'][cellspacing='0'][cellpadding='0']")
	}

	if table.Length() > 0 {
		table.Find("tr").Each(func(i int, row *goquery.Selection) {
			if i == 0 {
				return // 跳过表头
			}

			testInfo := t.parseTestRow(row)
			if testInfo != nil {
				testList = append(testList, *testInfo)
			}
		})
	}

	return &TestDetails{
		CourseName: courseName,
		LID:        lid,
		TestList:   testList,
		TotalCount: len(testList),
	}
}

// parseTestRow 解析单行测试信息
func (t *TestUtils) parseTestRow(row *goquery.Selection) *TestInfo {
	cells := row.Find("td")
	if cells.Length() < 8 {
		return nil
	}

	testInfo := &TestInfo{}

	// 第1列：测试标题
	titleCell := cells.Eq(0)
	testInfo.Title = strings.TrimSpace(titleCell.Text())

	// 第2列：开始时间
	testInfo.StartTime = strings.TrimSpace(cells.Eq(1).Text())

	// 第3列：截止时间
	testInfo.EndTime = strings.TrimSpace(cells.Eq(2).Text())

	// 第4列：允许测试次数
	testInfo.AllowedAttempts = strings.TrimSpace(cells.Eq(3).Text())

	// 第5列：限制用时（分钟）
	testInfo.Duration = strings.TrimSpace(cells.Eq(4).Text())

	// 第6列：开始测试
	startTestCell := cells.Eq(5)
	startLink := startTestCell.Find("a")
	if startLink.Length() > 0 {
		onclick, exists := startLink.Attr("onclick")
		if exists && strings.Contains(onclick, "gotostart(") {
			// 提取测试ID
			re := regexp.MustCompile(`gotostart\('(\d+)'`)
			matches := re.FindStringSubmatch(onclick)
			if len(matches) >= 2 {
				testInfo.TestID = matches[1]
				testInfo.CanStart = true
				testInfo.StartHref = fmt.Sprintf("#start_test_%s", testInfo.TestID)
				testInfo.TestLink = fmt.Sprintf("https://course.buct.edu.cn/meol/common/question/test/student/test_start.jsp?testId=%s", testInfo.TestID)
			} else {
				testInfo.CanStart = false
			}
		} else {
			testInfo.CanStart = false
		}
	} else {
		testInfo.CanStart = false
	}

	// 第7列：交卷状态
	submitCell := cells.Eq(6)
	submitText := strings.TrimSpace(submitCell.Text())
	if submitText != "&nbsp;" {
		testInfo.SubmitStatus = submitText
	}

	// 第8列：查看结果
	resultCell := cells.Eq(7)
	resultLink := resultCell.Find("a")
	if resultLink.Length() > 0 {
		testInfo.ResultHref, _ = resultLink.Attr("href")
		testInfo.HasResult = true
		testInfo.Status = "已完成"
	} else {
		testInfo.HasResult = false
		if testInfo.CanStart {
			testInfo.Status = "可进行"
		} else {
			testInfo.Status = "未开始"
		}
	}

	return testInfo
}

// parseTestDetail 解析测试详情页面
func (t *TestUtils) parseTestDetail(doc *goquery.Document, testID string) *TestDetail {
	detail := &TestDetail{
		TestID:  testID,
		TestURL: fmt.Sprintf("https://course.buct.edu.cn/meol/common/question/test/student/test_start.jsp?testId=%s", testID),
	}

	// 测试标题
	titleElem := doc.Find("h1, h2, h3").First()
	if titleElem.Length() > 0 {
		detail.Title = strings.TrimSpace(titleElem.Text())
	}

	// 测试描述和说明
	contentDiv := doc.Find("div.content, div.description").First()
	if contentDiv.Length() > 0 {
		detail.Description = strings.TrimSpace(contentDiv.Text())
	}

	// 查找测试信息表格
	doc.Find("table.info tr").Each(func(i int, row *goquery.Selection) {
		cells := row.Find("td, th")
		if cells.Length() >= 2 {
			key := strings.TrimSpace(cells.Eq(0).Text())
			value := strings.TrimSpace(cells.Eq(1).Text())

			switch {
			case strings.Contains(key, "开始时间"):
				detail.StartTime = value
			case strings.Contains(key, "结束时间"):
				detail.EndTime = value
			case strings.Contains(key, "持续时间") || strings.Contains(key, "考试时长"):
				detail.Duration = value
			case strings.Contains(key, "总分"):
				detail.TotalScore = value
			case strings.Contains(key, "题目数") || strings.Contains(key, "问题数"):
				detail.QuestionCount = value
			}
		}
	})

	return detail
}
