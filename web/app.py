from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from buct_course import BUCTAuth, CourseUtils

app = Flask(__name__)
CORS(app)

# 配置
BUCT_USERNAME = "***REMOVED***"
BUCT_PASSWORD = "***REMOVED***"

@app.route('/')
def index():
    return render_template('index_simple.html')

@app.route('/api/tasks')
def get_tasks():
    """获取待办任务API接口"""
    try:
        auth = BUCTAuth()
        if auth.login(BUCT_USERNAME, BUCT_PASSWORD):
            session = auth.get_session()
            course_utils = CourseUtils(session)
            
            tasks = course_utils.get_pending_tasks()
            
            return jsonify({
                'success': True,
                'data': {
                    'homework': tasks['homework'],
                    'tests': tasks['tests']
                }
            })
        else:
            return jsonify({
                'success': False,
                'message': '登录失败'
            }), 401
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'服务器错误: {str(e)}'
        }), 500

@app.route('/api/login', methods=['POST'])
def custom_login():
    """自定义登录API"""
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({
                'success': False,
                'message': '用户名和密码不能为空'
            }), 400
        
        auth = BUCTAuth()
        if auth.login(username, password):
            return jsonify({
                'success': True,
                'message': '登录成功'
            })
        else:
            return jsonify({
                'success': False,
                'message': '登录失败，请检查用户名和密码'
            }), 401
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'登录错误: {str(e)}'
        }), 500

@app.route('/health')
def health_check():
    """健康检查接口"""
    return jsonify({'status': 'ok', 'service': 'buct-course-remind'})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)