class BUCTCourseApp {
    constructor() {
        this.apiBase = window.location.origin + '/api';
        this.init();
    }

    init() {
        this.bindEvents();
        this.loadTasks();
    }

    bindEvents() {
        const refreshBtn = document.getElementById('refreshBtn');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => this.loadTasks());
        }

        const loginForm = document.getElementById('loginForm');
        if (loginForm) {
            loginForm.addEventListener('submit', (e) => this.handleLogin(e));
        }
    }

    async loadTasks() {
        const loadingElement = document.getElementById('loading');
        const tasksContainer = document.getElementById('tasksContainer');
        const errorElement = document.getElementById('error');
        const refreshBtn = document.getElementById('refreshBtn');

        if (loadingElement) loadingElement.style.display = 'block';
        if (tasksContainer) tasksContainer.style.display = 'none';
        if (errorElement) errorElement.style.display = 'none';
        if (refreshBtn) refreshBtn.disabled = true;

        try {
            const response = await fetch(`${this.apiBase}/tasks`);
            const data = await response.json();

            if (data.success) {
                this.displayTasks(data.data);
                if (errorElement) errorElement.style.display = 'none';
            } else {
                this.showError(data.message || '获取任务失败');
            }
        } catch (error) {
            this.showError('网络错误，请检查服务器连接');
            console.error('Error loading tasks:', error);
        } finally {
            if (loadingElement) loadingElement.style.display = 'none';
            if (tasksContainer) tasksContainer.style.display = 'grid';
            if (refreshBtn) refreshBtn.disabled = false;
        }
    }

    displayTasks(tasks) {
        const homeworkContainer = document.getElementById('homeworkList');
        const testsContainer = document.getElementById('testsList');

        if (homeworkContainer) {
            homeworkContainer.innerHTML = this.renderCourseList(tasks.homework, 'homework');
        }

        if (testsContainer) {
            testsContainer.innerHTML = this.renderCourseList(tasks.tests, 'test');
        }

        // 更新统计信息
        this.updateStats(tasks);
    }

    renderCourseList(courses, type) {
        if (!courses || courses.length === 0) {
            return `<div class="empty">暂无待提交${type === 'homework' ? '作业' : '测试'}</div>`;
        }

        return courses.map((course, index) => `
            <div class="course-item">
                <h4>${course[0] || '未命名课程'}</h4>
                <p>课程ID: ${course[1] || '暂无'}</p>
                <small>${type === 'homework' ? '作业' : '测试'} #${index + 1}</small>
            </div>
        `).join('');
    }

    updateStats(tasks) {
        const homeworkCount = tasks.homework?.length || 0;
        const testsCount = tasks.tests?.length || 0;
        const totalCount = homeworkCount + testsCount;

        const statsElement = document.getElementById('stats');
        if (statsElement) {
            statsElement.innerHTML = `
                <div style="text-align: center; color: white; margin-bottom: 20px;">
                    <h3>任务统计</h3>
                    <p>待提交作业: ${homeworkCount} | 待提交测试: ${testsCount} | 总计: ${totalCount}</p>
                </div>
            `;
        }
    }

    showError(message) {
        const errorElement = document.getElementById('error');
        if (errorElement) {
            errorElement.innerHTML = `
                <strong>错误:</strong> ${message}
                <br><small>请检查网络连接或联系管理员</small>
            `;
            errorElement.style.display = 'block';
        }
    }

    async handleLogin(e) {
        e.preventDefault();
        
        const formData = new FormData(e.target);
        const username = formData.get('username');
        const password = formData.get('password');

        try {
            const response = await fetch(`${this.apiBase}/login`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ username, password })
            });

            const data = await response.json();

            if (data.success) {
                alert('登录成功！');
                window.location.reload();
            } else {
                alert(`登录失败: ${data.message}`);
            }
        } catch (error) {
            alert('登录请求失败，请检查网络连接');
            console.error('Login error:', error);
        }
    }
}

// 页面加载完成后初始化应用
document.addEventListener('DOMContentLoaded', () => {
    new BUCTCourseApp();
});