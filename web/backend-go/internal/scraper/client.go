package scraper

// BUCTClient 北化课程平台客户端，提供便捷的API访问
type BUCTClient struct {
	Auth        *BUCTAuth
	CourseUtils *CourseUtils
	TestUtils   *TestUtils
	Username    string
	Password    string
}

// NewBUCTClient 创建新的客户端实例
func NewBUCTClient(username, password string) *BUCTClient {
	client := &BUCTClient{
		Auth:     NewBUCTAuth(),
		Username: username,
		Password: password,
	}
	return client
}

// Login 登录课程平台
func (c *BUCTClient) Login() error {
	if err := c.Auth.Login(c.Username, c.Password); err != nil {
		return err
	}

	httpClient, _ := c.Auth.GetClient()
	c.CourseUtils = NewCourseUtils(httpClient)
	c.TestUtils = NewTestUtils(httpClient)

	return nil
}

// Logout 退出登录
func (c *BUCTClient) Logout() {
	c.Auth.Logout()
	c.CourseUtils = nil
	c.TestUtils = nil
}

// IsLoggedIn 检查是否已登录
func (c *BUCTClient) IsLoggedIn() bool {
	return c.Auth.IsLoggedIn
}

// GetPendingTasks 获取待办任务
func (c *BUCTClient) GetPendingTasks() (*PendingTasksResult, error) {
	if !c.IsLoggedIn() {
		return nil, ErrNotLoggedIn
	}

	// 获取待提交作业和测试课程
	homeworkCourses, err := c.CourseUtils.GetPendingHomework()
	if err != nil {
		return nil, err
	}

	testCourses, err := c.TestUtils.GetPendingTests()
	if err != nil {
		return nil, err
	}

	// 获取每个课程的详细作业信息
	var detailedHomework []HomeworkWithCourse
	for _, course := range homeworkCourses {
		lid := course.LID
		if lid != "" {
			courseDetails, err := c.CourseUtils.GetCourseDetails(lid)
			if err != nil {
				continue
			}

			homeworkList := courseDetails.HomeworkList
			for _, hw := range homeworkList {
				// 只保留未完成且未超时的作业
				if hw.CanSubmit {
					detailedHomework = append(detailedHomework, HomeworkWithCourse{
						HomeworkInfo: hw,
						CourseName:   course.CourseName,
						LID:          lid,
					})
				}
			}
		}
	}

	// 获取每个课程的详细测试信息
	var detailedTests []TestWithCourse
	for _, course := range testCourses {
		lid := course.LID
		if lid != "" {
			testDetails, err := c.TestUtils.GetTestList(lid)
			if err != nil {
				continue
			}

			testList := testDetails.TestList
			for _, test := range testList {
				if test.CanStart {
					detailedTests = append(detailedTests, TestWithCourse{
						TestInfo:   test,
						CourseName: course.CourseName,
						LID:        lid,
					})
				}
			}
		}
	}

	return &PendingTasksResult{
		Success: true,
		Data: PendingTasksData{
			Homework: detailedHomework,
			Tests:    detailedTests,
			Stats: TasksStats{
				HomeworkCount: len(detailedHomework),
				TestsCount:    len(detailedTests),
				TotalCount:    len(detailedHomework) + len(detailedTests),
			},
		},
	}, nil
}

// GetPendingHomework 获取待提交作业的课程列表
func (c *BUCTClient) GetPendingHomework() ([]CourseInfo, error) {
	if !c.IsLoggedIn() {
		return nil, ErrNotLoggedIn
	}
	return c.CourseUtils.GetPendingHomework()
}

// GetCourseDetails 获取指定课程的作业详情
func (c *BUCTClient) GetCourseDetails(lid string) (*CourseDetails, error) {
	if !c.IsLoggedIn() {
		return nil, ErrNotLoggedIn
	}
	return c.CourseUtils.GetCourseDetails(lid)
}

// GetHomeworkDetail 获取单个作业的详细信息
func (c *BUCTClient) GetHomeworkDetail(hwtid string) (*HomeworkDetail, error) {
	if !c.IsLoggedIn() {
		return nil, ErrNotLoggedIn
	}
	return c.CourseUtils.GetHomeworkDetail(hwtid)
}

// GetHomeworkTasks 获取作业的具体任务要求
func (c *BUCTClient) GetHomeworkTasks(url string) ([]string, error) {
	if !c.IsLoggedIn() {
		return nil, ErrNotLoggedIn
	}
	return c.CourseUtils.GetHomeworkTasks(url)
}

// GetAllPendingHomeworkDetails 批量获取所有作业详情（含时间分析）
func (c *BUCTClient) GetAllPendingHomeworkDetails() ([]CourseDetails, error) {
	if !c.IsLoggedIn() {
		return nil, ErrNotLoggedIn
	}
	return c.CourseUtils.GetAllPendingHomeworkDetails()
}

// GetPendingTests 获取待提交测试的课程列表
func (c *BUCTClient) GetPendingTests() ([]CourseInfo, error) {
	if !c.IsLoggedIn() {
		return nil, ErrNotLoggedIn
	}
	return c.TestUtils.GetPendingTests()
}

// GetTestList 获取指定课程的测试列表
func (c *BUCTClient) GetTestList(lid string) (*TestDetails, error) {
	if !c.IsLoggedIn() {
		return nil, ErrNotLoggedIn
	}
	return c.TestUtils.GetTestList(lid)
}

// GetTestDetail 获取单个测试的详细信息
func (c *BUCTClient) GetTestDetail(testID string) (*TestDetail, error) {
	if !c.IsLoggedIn() {
		return nil, ErrNotLoggedIn
	}
	return c.TestUtils.GetTestDetail(testID)
}

// GetCourses 获取所有课程
func (c *BUCTClient) GetCourses() ([]CourseInfo, error) {
	if !c.IsLoggedIn() {
		return nil, ErrNotLoggedIn
	}
	return c.CourseUtils.LidUtils.GetAllCourseLIDs()
}
