package scraper

import (
	"errors"
	"net/http"
	"net/http/cookiejar"
	"net/url"
	"strings"
	"time"
)

// BUCTAuth 北化课程平台认证类
type BUCTAuth struct {
	Client     *http.Client
	BaseURL    string
	IsLoggedIn bool
}

// NewBUCTAuth 创建新的认证实例
func NewBUCTAuth() *BUCTAuth {
	jar, _ := cookiejar.New(nil)
	client := &http.Client{
		Jar:     jar,
		Timeout: 30 * time.Second,
		CheckRedirect: func(req *http.Request, via []*http.Request) error {
			// 允许重定向，最多10次
			if len(via) >= 10 {
				return errors.New("太多重定向")
			}
			return nil
		},
	}

	return &BUCTAuth{
		Client:     client,
		BaseURL:    "https://course.buct.edu.cn",
		IsLoggedIn: false,
	}
}

// Login 登录到北化课程平台
func (auth *BUCTAuth) Login(username, password string) error {
	loginURL := auth.BaseURL + "/meol/loginCheck.do"

	// 构建登录表单数据
	formData := url.Values{}
	formData.Set("IPT_LOGINUSERNAME", username)
	formData.Set("IPT_LOGINPASSWORD", password)

	req, err := http.NewRequest("POST", loginURL, strings.NewReader(formData.Encode()))
	if err != nil {
		return err
	}

	req.Header.Set("Content-Type", "application/x-www-form-urlencoded")
	req.Header.Set("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36")
	req.Header.Set("Accept", "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8")
	req.Header.Set("Accept-Language", "zh-CN,zh;q=0.9,en;q=0.8")
	req.Header.Set("Referer", auth.BaseURL+"/meol/loginCheck.do")
	req.Header.Set("Origin", auth.BaseURL)

	resp, err := auth.Client.Do(req)
	if err != nil {
		return err
	}
	defer resp.Body.Close()

	// 检查登录是否成功
	// 假设成功登录会重定向到非登录页，失败则停留在登录页或重定向回登录页
	finalURL := resp.Request.URL.String()
	if strings.Contains(finalURL, "login.do") || strings.Contains(finalURL, "loginCheck.do") {
		auth.IsLoggedIn = false
		return errors.New("登录失败，请检查用户名和密码")
	}

	auth.IsLoggedIn = true
	return nil
}

// GetClient 获取登录后的HTTP客户端
func (auth *BUCTAuth) GetClient() (*http.Client, error) {
	if !auth.IsLoggedIn {
		return nil, errors.New("请先调用Login方法进行登录")
	}
	return auth.Client, nil
}

// Logout 注销登录
func (auth *BUCTAuth) Logout() {
	logoutURL := "https://portal.buct.edu.cn/cas/logout"
	req, _ := http.NewRequest("GET", logoutURL, nil)
	auth.Client.Do(req)

	// 重新创建一个新的cookie jar
	jar, _ := cookiejar.New(nil)
	auth.Client.Jar = jar
	auth.IsLoggedIn = false
}

// SetBaseURL 设置基础URL（用于测试或其他环境）
func (auth *BUCTAuth) SetBaseURL(baseURL string) {
	auth.BaseURL = strings.TrimSuffix(baseURL, "/")
}
