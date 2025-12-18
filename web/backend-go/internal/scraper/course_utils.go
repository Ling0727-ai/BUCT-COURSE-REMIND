package scraper

import (
	"fmt"
	"html"
	"net/http"
	"regexp"
	"strings"
	"time"

	"github.com/PuerkitoBio/goquery"
)

// CourseUtils 北化课程平台作业解析工具类
type CourseUtils struct {
	Client   *http.Client
	BaseURL  string
	LidUtils *LidUtils
}

// HomeworkInfo 作业信息结构
type HomeworkInfo struct {
	Title       string `json:"title"`
	HWTID       string `json:"hwtid"`
	DetailHref  string `json:"detail_href"`
	Deadline    string `json:"deadline"`
	Score       string `json:"score"`
	Publisher   string `json:"publisher"`
	SubmitHref  string `json:"submit_href"`
	ResultHref  string `json:"result_href"`
	CanSubmit   bool   `json:"can_submit"`
	HasResult   bool   `json:"has_result"`
	IsGroup     bool   `json:"is_group"`
	Status      string `json:"status"`
	Description string `json:"description,omitempty"` // 作业详细描述
	// 时间分析相关
	TimeRemaining string `json:"time_remaining,omitempty"`
	IsUrgent      bool   `json:"is_urgent,omitempty"`
}

// CourseDetails 课程详情结构
type CourseDetails struct {
	LID          string         `json:"lid"`
	CourseName   string         `json:"course_name,omitempty"`
	HomeworkList []HomeworkInfo `json:"homework_list"`
	TotalCount   int            `json:"total_count"`
	UrgentCount  int            `json:"urgent_count,omitempty"`
	CourseInfo   *CourseInfo    `json:"course_info,omitempty"`
}

// HomeworkDetail 作业详细信息
type HomeworkDetail struct {
	HWTID        string   `json:"hwtid"`
	Title        string   `json:"title"`
	Description  string   `json:"description"`
	Deadline     string   `json:"deadline"`
	Requirements string   `json:"requirements"`
	Attachments  []string `json:"attachments"`
}

// NewCourseUtils 创建新的课程工具实例
func NewCourseUtils(client *http.Client) *CourseUtils {
	return &CourseUtils{
		Client:   client,
		BaseURL:  "https://course.buct.edu.cn",
		LidUtils: NewLidUtils(client),
	}
}

// GetPendingHomework 获取待提交作业列表
func (c *CourseUtils) GetPendingHomework() ([]CourseInfo, error) {
	return c.LidUtils.GetHomeworkLIDs()
}

// GetCourseDetails 获取课程作业列表信息
func (c *CourseUtils) GetCourseDetails(lid string) (*CourseDetails, error) {
	// 首先访问课程主页，获取作业列表
	courseMainURL := fmt.Sprintf("%s/meol/jpk/course/layout/newpage/index.jsp?courseId=%s", c.BaseURL, lid)

	doc, err := makeRequest(c.Client, courseMainURL, "")
	if err != nil {
		return nil, fmt.Errorf("获取课程详情失败: %v", err)
	}

	// 添加短暂延迟
	time.Sleep(300 * time.Millisecond)

	// 调试：打印页面所有链接
	fmt.Printf("课程 %s 主页链接:\n", lid)
	linkCount := 0
	doc.Find("a").Each(func(i int, s *goquery.Selection) {
		href, _ := s.Attr("href")
		text := strings.TrimSpace(s.Text())
		if href != "" || text != "" {
			linkCount++
			if linkCount <= 20 { // 只打印前20个链接
				fmt.Printf("  链接 %d: href=%s, text=%s\n", linkCount, href, text)
			}
		}
	})
	fmt.Printf("  总共 %d 个链接\n", linkCount)

	// 查找作业相关链接
	var homeworkLink string
	doc.Find("a[href]").Each(func(i int, s *goquery.Selection) {
		href, exists := s.Attr("href")
		if !exists {
			return
		}
		text := strings.TrimSpace(s.Text())
		if strings.Contains(href, "course_column_preview_transfer.jsp") && strings.Contains(text, "作业") {
			homeworkLink = href
			fmt.Printf("找到作业链接: %s (文本: %s)\n", href, text)
		}
	})

	// 如果找不到带 "作业" 文字的链接，尝试查找 hwtask.jsp 链接
	if homeworkLink == "" {
		doc.Find("a[href]").Each(func(i int, s *goquery.Selection) {
			href, exists := s.Attr("href")
			if !exists {
				return
			}
			if strings.Contains(href, "hwtask.jsp") {
				homeworkLink = href
				fmt.Printf("找到作业链接(hwtask.jsp): %s\n", href)
			}
		})
	}

	if homeworkLink == "" {
		// 如果没找到作业链接，返回空结果
		fmt.Printf("课程 %s 未找到作业链接\n", lid)
		return &CourseDetails{
			LID:          lid,
			HomeworkList: []HomeworkInfo{},
			TotalCount:   0,
		}, nil
	}

	// 构造完整的作业页面URL
	var homeworkURL string
	if strings.HasPrefix(homeworkLink, "/") {
		homeworkURL = c.BaseURL + homeworkLink
	} else if strings.HasPrefix(homeworkLink, "../../") {
		homeworkURL = c.BaseURL + "/meol/jpk/course/layout/newpage/" + homeworkLink
	} else {
		homeworkURL = homeworkLink
	}

	fmt.Printf("访问作业页面: %s\n", homeworkURL)

	// 访问作业页面
	time.Sleep(500 * time.Millisecond)
	hwDoc, err := makeRequest(c.Client, homeworkURL, courseMainURL)
	if err != nil {
		return nil, fmt.Errorf("获取作业列表失败: %v", err)
	}

	// 调试：打印找到的表格数量
	tableCount := hwDoc.Find("table.valuelist").Length()
	fmt.Printf("作业页面找到 %d 个 table.valuelist\n", tableCount)

	return c.parseHomeworkTable(hwDoc, lid)
}

// GetHomeworkDetail 获取单个作业的详细信息
func (c *CourseUtils) GetHomeworkDetail(hwtid string) (*HomeworkDetail, error) {
	detailURL := fmt.Sprintf("%s/meol/common/hw/student/hwtask.view.jsp?hwtid=%s", c.BaseURL, hwtid)
	referer := c.BaseURL + "/meol/common/hw/student/hwtask.jsp?tagbug=client&strStyle=new03"

	time.Sleep(300 * time.Millisecond)
	doc, err := makeRequest(c.Client, detailURL, referer)
	if err != nil {
		return nil, fmt.Errorf("获取作业详情失败: %v", err)
	}

	return c.parseHomeworkDetail(doc, hwtid), nil
}

// GetHomeworkTasks 获取作业详情页面中的具体题目要求
func (c *CourseUtils) GetHomeworkTasks(url string) ([]string, error) {
	// 构造完整URL
	var fullURL string
	if strings.HasPrefix(url, "/") {
		fullURL = c.BaseURL + url
	} else {
		fullURL = url
	}

	referer := c.BaseURL + "/meol/common/hw/student/hwtask.jsp?tagbug=client&strStyle=new03"

	time.Sleep(300 * time.Millisecond)
	doc, err := makeRequest(c.Client, fullURL, referer)
	if err != nil {
		return nil, fmt.Errorf("获取作业任务详情失败: %v", err)
	}

	var tasks []string

	// 查找隐藏的input字段，通常包含作业内容
	doc.Find("input[type='hidden']").Each(func(i int, s *goquery.Selection) {
		name, _ := s.Attr("name")
		if strings.Contains(name, "content") {
			value, exists := s.Attr("value")
			if exists && value != "" {
				// HTML解码
				decodedHTML := html.UnescapeString(value)

				// 解析HTML内容
				contentDoc, err := goquery.NewDocumentFromReader(strings.NewReader(decodedHTML))
				if err == nil {
					// 提取所有<p>标签中的文本
					contentDoc.Find("p").Each(func(j int, p *goquery.Selection) {
						text := strings.TrimSpace(p.Text())
						if text != "" {
							tasks = append(tasks, text)
						}
					})

					// 如果没有p标签，直接提取文本
					if len(tasks) == 0 {
						text := strings.TrimSpace(contentDoc.Text())
						if text != "" {
							tasks = append(tasks, text)
						}
					}
				}
			}
		}
	})

	// 如果没有找到隐藏input，尝试查找id="body"的div（备用方案）
	if len(tasks) == 0 {
		doc.Find("div#body").Each(func(i int, s *goquery.Selection) {
			s.Find("p").Each(func(j int, p *goquery.Selection) {
				text := strings.TrimSpace(p.Text())
				if text != "" {
					tasks = append(tasks, text)
				}
			})
		})
	}

	return tasks, nil
}

// GetAllPendingHomeworkDetails 获取所有待提交作业的详细信息，包含时间分析
func (c *CourseUtils) GetAllPendingHomeworkDetails() ([]CourseDetails, error) {
	pendingHomework, err := c.GetPendingHomework()
	if err != nil {
		fmt.Printf("获取待提交作业列表失败: %v\n", err)
		return nil, err
	}

	fmt.Printf("获取到 %d 门有待提交作业的课程\n", len(pendingHomework))

	var allHomeworkDetails []CourseDetails

	for _, course := range pendingHomework {
		lid := course.LID
		courseName := course.CourseName
		fmt.Printf("正在获取课程详情: %s (LID: %s)\n", courseName, lid)

		homeworkDetails, err := c.GetCourseDetails(lid)
		if err != nil {
			fmt.Printf("获取课程 %s (LID: %s) 的作业详情失败: %v\n", courseName, lid, err)
			continue
		}

		fmt.Printf("课程 %s 有 %d 条作业\n", courseName, len(homeworkDetails.HomeworkList))

		homeworkDetails.CourseName = courseName
		homeworkDetails.CourseInfo = &course

		// 添加时间分析，并获取作业详细描述
		urgentCount := 0
		currentTime := time.Now()

		for i := range homeworkDetails.HomeworkList {
			hw := &homeworkDetails.HomeworkList[i]

			// 获取作业详细描述
			if hw.DetailHref != "" {
				tasks, err := c.GetHomeworkTasks(hw.DetailHref)
				if err == nil && len(tasks) > 0 {
					// 将任务列表合并为一个描述字符串
					hw.Description = strings.Join(tasks, " ")
				}
				// 添加短暂延迟避免请求过快
				time.Sleep(300 * time.Millisecond)
			}

			deadlineStr := hw.Deadline
			if deadlineStr != "" {
				// 解析时间格式：2025年9月23日 23:59:00
				deadline, err := parseChineseDateTime(deadlineStr)
				if err == nil {
					timeDiff := deadline.Sub(currentTime)
					if timeDiff.Seconds() > 0 {
						days := int(timeDiff.Hours() / 24)
						hours := int(timeDiff.Hours()) % 24
						minutes := int(timeDiff.Minutes()) % 60

						if days > 0 {
							hw.TimeRemaining = fmt.Sprintf("%d天%d小时%d分钟", days, hours, minutes)
						} else if hours > 0 {
							hw.TimeRemaining = fmt.Sprintf("%d小时%d分钟", hours, minutes)
						} else {
							hw.TimeRemaining = fmt.Sprintf("%d分钟", minutes)
						}

						// 检查是否为紧急作业（24小时内截止）
						if timeDiff <= 24*time.Hour {
							urgentCount++
							hw.IsUrgent = true
						}
					} else {
						hw.TimeRemaining = "已过期"
						hw.IsUrgent = false
					}
				} else {
					hw.TimeRemaining = "时间格式错误"
					hw.IsUrgent = false
				}
			} else {
				hw.TimeRemaining = "无截止时间"
				hw.IsUrgent = false
			}
		}

		homeworkDetails.UrgentCount = urgentCount
		allHomeworkDetails = append(allHomeworkDetails, *homeworkDetails)

		// 添加延迟，避免批量请求过快
		time.Sleep(800 * time.Millisecond)
	}

	return allHomeworkDetails, nil
}

// parseHomeworkTable 解析作业列表表格
func (c *CourseUtils) parseHomeworkTable(doc *goquery.Document, lid string) (*CourseDetails, error) {
	time.Sleep(500 * time.Millisecond)

	var homeworkList []HomeworkInfo

	doc.Find("table.valuelist tr").Each(func(i int, row *goquery.Selection) {
		if i == 0 {
			return // 跳过表头
		}

		hwInfo := c.parseHomeworkRow(row)
		if hwInfo != nil {
			homeworkList = append(homeworkList, *hwInfo)
		}
	})

	return &CourseDetails{
		LID:          lid,
		HomeworkList: homeworkList,
		TotalCount:   len(homeworkList),
	}, nil
}

// parseHomeworkRow 解析单行作业信息
func (c *CourseUtils) parseHomeworkRow(row *goquery.Selection) *HomeworkInfo {
	cells := row.Find("td")
	if cells.Length() < 8 {
		return nil
	}

	hwInfo := &HomeworkInfo{}

	// 作业标题和链接
	titleCell := cells.Eq(0)
	titleLink := titleCell.Find("a.infolist")
	if titleLink.Length() > 0 {
		hwInfo.Title = strings.TrimSpace(titleLink.Text())
		detailHref, _ := titleLink.Attr("href")

		// 构造完整的详情URL
		if strings.HasPrefix(detailHref, "/") {
			hwInfo.DetailHref = c.BaseURL + detailHref
		} else if strings.HasPrefix(detailHref, "../../") {
			hwInfo.DetailHref = c.BaseURL + "/meol/common/hw/student/" + detailHref
		} else if strings.HasPrefix(detailHref, "hwtask.view.jsp") {
			hwInfo.DetailHref = c.BaseURL + "/meol/common/hw/student/" + detailHref
		} else {
			hwInfo.DetailHref = detailHref
		}

		// 提取作业ID
		if strings.Contains(detailHref, "hwtid=") {
			re := regexp.MustCompile(`hwtid=([^&]+)`)
			matches := re.FindStringSubmatch(detailHref)
			if len(matches) >= 2 {
				hwInfo.HWTID = matches[1]
			}
		}
	}

	// 分组作业标识
	groupImg := titleCell.Find("img[title='分组作业']")
	hwInfo.IsGroup = groupImg.Length() > 0

	// 截止时间、分数、发布人
	hwInfo.Deadline = strings.TrimSpace(cells.Eq(1).Text())
	hwInfo.Score = strings.TrimSpace(cells.Eq(2).Text())
	hwInfo.Publisher = strings.TrimSpace(cells.Eq(3).Text())

	// 提交作业链接
	submitCell := cells.Eq(5)
	submitLink := submitCell.Find("a.enter")
	if submitLink.Length() > 0 {
		hwInfo.SubmitHref, _ = submitLink.Attr("href")
	}

	// 判断是否可以提交
	deadlineStr := hwInfo.Deadline
	scoreText := hwInfo.Score
	hasSubmitLink := submitLink.Length() > 0

	// 检查是否已过期
	isNotExpired := true
	if deadlineStr != "" {
		deadline, err := parseChineseDateTime(deadlineStr)
		if err == nil {
			isNotExpired = deadline.After(time.Now())
		}
	}

	// 检查是否已完成（有分数表示已完成）
	isNotCompleted := scoreText == "" || strings.TrimSpace(scoreText) == ""

	// 只有同时满足：有提交链接、未过期、未完成 才认为可以提交
	hwInfo.CanSubmit = hasSubmitLink && isNotExpired && isNotCompleted

	// 查看结果链接
	resultCell := cells.Eq(6)
	resultLink := resultCell.Find("a.view")
	if resultLink.Length() > 0 {
		hwInfo.ResultHref, _ = resultLink.Attr("href")
		hwInfo.HasResult = true
	}

	// 状态判断
	if !hwInfo.HasResult && strings.Contains(resultCell.Text(), "未提交") {
		hwInfo.Status = "未提交"
	}

	// 如果有作业ID，构造详情链接
	if hwInfo.HWTID != "" {
		hwInfo.DetailHref = fmt.Sprintf("https://course.buct.edu.cn/meol/common/hw/student/hwtask.view.jsp?hwtid=%s", hwInfo.HWTID)
	}

	return hwInfo
}

// parseHomeworkDetail 解析作业详情页面
func (c *CourseUtils) parseHomeworkDetail(doc *goquery.Document, hwtid string) *HomeworkDetail {
	detail := &HomeworkDetail{
		HWTID:       hwtid,
		Attachments: []string{},
	}

	// 作业标题
	titleElem := doc.Find("h1, h2, h3").First()
	if titleElem.Length() > 0 {
		detail.Title = strings.TrimSpace(titleElem.Text())
	}

	// 作业描述
	contentDiv := doc.Find("div.content, div.description").First()
	if contentDiv.Length() > 0 {
		detail.Description = strings.TrimSpace(contentDiv.Text())
	}

	return detail
}

// parseChineseDateTime 解析中文日期时间格式
func parseChineseDateTime(dateTimeStr string) (time.Time, error) {
	// 格式：2025年9月23日 23:59:00
	re := regexp.MustCompile(`(\d{4})年(\d{1,2})月(\d{1,2})日\s+(\d{1,2}):(\d{1,2}):(\d{1,2})`)
	matches := re.FindStringSubmatch(dateTimeStr)
	if len(matches) < 7 {
		return time.Time{}, fmt.Errorf("无法解析日期时间: %s", dateTimeStr)
	}

	return time.Parse("2006-01-02 15:04:05",
		fmt.Sprintf("%s-%02s-%02s %02s:%02s:%02s",
			matches[1], matches[2], matches[3], matches[4], matches[5], matches[6]))
}
