import logging
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict

from bson import ObjectId
from flask import Blueprint, jsonify, request, current_app, session

from . import mongo
from .auth import login_required
from .notification_services import check_and_send_notifications, send_webhook_notification

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 创建蓝图
webhooks_bp = Blueprint('webhooks', __name__)


class ReminderType(Enum):
    """提醒类型"""
    NEW_HOMEWORK = "新作业"
    DEADLINE_APPROACHING = "即将截止"


class NotificationStatus(Enum):
    """通知状态"""
    SUCCESS = "成功"
    FAILED = "失败"
    NOTHING = "未改变"


class Homework:
    """作业信息"""

    def __init__(self, homework_id: str, title: str, course: str,
                 deadline: datetime, created_at: datetime):
        self.homework_id = homework_id
        self.title = title
        self.course = course
        self.deadline = deadline
        self.created_at = created_at
        self.notification_status = NotificationStatus.NOTHING

    def __str__(self):
        return f"{self.course} - {self.title}"

    def time_until_deadline(self) -> timedelta:
        """计算距离截止时间"""
        return self.deadline - datetime.now()

    def is_within_threshold(self, hours_before: int) -> bool:
        """检查是否在阈值范围内"""
        time_left = self.time_until_deadline()
        return timedelta(0) <= time_left <= timedelta(hours=hours_before)


class WebhookConfig:
    """Webhook 配置"""

    def __init__(self, url: str, request_body: str = "",
                 headers: Dict[str, str] = None, method: str = "GET"):
        self.url = url
        self.request_body = request_body
        self.headers = headers or {}
        self.method = method

    # 注释掉 HomeworkReminderWebhook 类，只保留邮箱提醒功能
    # class HomeworkReminderWebhook:
    #     """作业提醒 Webhook 系统"""
    #
    #     def __init__(self, config: WebhookConfig):
    #         self.config = config
    #         self.failed_times = 0
    #         self.max_failed_before_notify = 3
    #
    #     def send_new_homework_reminder(self, homework: Homework) -> NotificationStatus:
    #         """发送新作业提醒"""
    #         logger.info(f"发送新作业提醒: {homework}")
    #
    #         params = {
    #             "reminder_type": ReminderType.NEW_HOMEWORK.value,
    #             "homework_id": homework.homework_id,
    #             "title": homework.title,
    #             "course": homework.course,
    #             "deadline": homework.deadline.strftime("%Y-%m-%d %H:%M:%S"),
    #             "created_at": homework.created_at.strftime("%Y-%m-%d %H:%M:%S"),
    #             "time_left": str(homework.time_until_deadline())
    #         }
    #
    #         return self._execute_webhook(params)
    #
    #     def send_deadline_reminder(self, homeworks: List[Homework],
    #                               threshold_hours: int) -> NotificationStatus:
    #         """发送截止时间提醒"""
    #         if not homeworks:
    #             return NotificationStatus.NOTHING
    #
    #         logger.info(f"发送截止时间提醒，共 {len(homeworks)} 个作业")
    #
    #         homework_list = []
    #         for hw in homeworks:
    #             homework_list.append({
    #                 "homework_id": hw.homework_id,
    #                 "title": hw.title,
    #                 "course": hw.course,
    #                 "deadline": hw.deadline.strftime("%Y-%m-%d %H:%M:%S"),
    #                 "time_left": str(hw.time_until_deadline())
    #             })
    #
    #         params = {
    #             "reminder_type": ReminderType.DEADLINE_APPROACHING.value,
    #             "threshold_hours": threshold_hours,
    #             "homework_count": len(homeworks),
    #             "homeworks": homework_list
    #         }
    #
    #         return self._execute_webhook(params)
    #
    #     def batch_check_and_remind(self, homeworks: List[Homework],
    #                                threshold_hours: int) -> Dict[str, NotificationStatus]:
    #         """批量检查并提醒"""
    #         results = {
    #             "new_homework": NotificationStatus.NOTHING,
    #             "deadline_approaching": NotificationStatus.NOTHING
    #         }
    #
    #         # 检查新作业（例如：创建时间在最近1小时内）
    #         new_homeworks = [hw for hw in homeworks
    #                         if (datetime.now() - hw.created_at) < timedelta(hours=1)]
    #
    #         # 检查即将截止的作业
    #         approaching_homeworks = [hw for hw in homeworks
    #                                 if hw.is_within_threshold(threshold_hours)]
    #
    #         # 发送新作业提醒
    #         if new_homeworks:
    #             for hw in new_homeworks:
    #                 status = self.send_new_homework_reminder(hw)
    #                 if status == NotificationStatus.FAILED:
    #                     results["new_homework"] = NotificationStatus.FAILED
    #                 elif status == NotificationStatus.SUCCESS:
    #                     results["new_homework"] = NotificationStatus.SUCCESS
    #
    #         # 发送截止时间提醒
    #         if approaching_homeworks:
    #             results["deadline_approaching"] = self.send_deadline_reminder(
    #                 approaching_homeworks, threshold_hours
    #             )
    #
    #         return results
    #
    #     def _execute_webhook(self, params: Dict) -> NotificationStatus:
    #         """执行 Webhook 调用"""
    #         try:
    #             # 替换参数
    #             url = self._replace_params(self.config.url, params)
    #             body = self._replace_params(self.config.request_body, params)
    #
    #             # 确定请求方法和内容类型
    #             method = self.config.method.upper()
    #             headers = self.config.headers.copy()
    #
    #             if body:
    #                 method = "POST"
    #                 # 判断是否为 JSON
    #                 if self._is_json(body):
    #                     headers["Content-Type"] = "application/json"
    #                 else:
    #                     headers["Content-Type"] = "application/x-www-form-urlencoded"
    #
    #             # 发送请求
    #             logger.info(f"发送 Webhook 请求: {method} {url}")
    #
    #             if method == "POST":
    #                 response = requests.post(url, data=body, headers=headers, timeout=10)
    #             else:
    #                 response = requests.get(url, headers=headers, timeout=10)
    #
    #             response.raise_for_status()
    #
    #             logger.info(f"Webhook 调用成功! 返回数据: {response.text[:200]}")
    #             self.failed_times = 0
    #             return NotificationStatus.SUCCESS
    #
    #         except Exception as e:
    #             logger.error(f"Webhook 调用失败! 异常信息: {str(e)}")
    #             self.failed_times += 1
    #
    #             # 只在第3次失败时才真正通知失败
    #             if self.failed_times >= self.max_failed_before_notify:
    #                 logger.warning(f"已连续失败 {self.failed_times} 次")
    #                 return NotificationStatus.FAILED
    #             else:
    #                 logger.info(f"失败次数: {self.failed_times}/{self.max_failed_before_notify}")
    #                 return NotificationStatus.NOTHING
    #
    #     def _replace_params(self, template: str, params: Dict) -> str:
    #         """替换参数模板"""
    #         if not template:
    #             return ""
    #
    #         result = template
    #
    #         # 如果是 JSON 格式，直接替换整个对象
    #         if self._is_json(template):
    #             try:
    #                 # 尝试解析为 JSON 并进行智能替换
    #                 template_dict = json.loads(template)
    #                 merged = {**template_dict, **params}
    #                 return json.dumps(merged, ensure_ascii=False)
    #             except:
    #                 pass
    #
    #         # 否则进行字符串替换
    #         for key, value in params.items():
    #             placeholder = f"#{{{key}}}"
    #             if isinstance(value, (list, dict)):
    #                 value = json.dumps(value, ensure_ascii=False)
    #             result = result.replace(placeholder, str(value))
    #
    #         return result
    #
    #     def _is_json(self, s: str) -> bool:
    #         """检查字符串是否为有效 JSON"""
    #         if not s:
    #             return False
    #         s = s.strip()
    #         if not (s.startswith("{") or s.startswith("[")):
    #             return False
    #         try:
    #             json.loads(s)
    #             return True
    #         except:
    #             return False

    # 使用示例 - 注释掉非邮箱相关的webhook配置
    # if __name__ == "__main__":
    # # 配置 Webhook（示例使用钉钉机器人格式）- 注释掉，只保留邮箱提醒
    # webhook_config = WebhookConfig(
    #     url="https://oapi.dingtalk.com/robot/send?access_token=YOUR_TOKEN",
    #     request_body=json.dumps({
    #         "msgtype": "markdown",
    #         "markdown": {
    #             "title": "作业提醒",
    #             "text": "## #{reminder_type}\n\n**作业**: #{title}\n\n**课程**: #{course}\n\n**截止时间**: #{deadline}\n\n**剩余时间**: #{time_left}"
    #         }
    #     }),
    #     headers={"Content-Type": "application/json"}
    # )

    # # 创建提醒系统
    # reminder = HomeworkReminderWebhook(webhook_config)

    # 创建测试作业
    homework1 = Homework(
        homework_id="HW001",
        title="数据结构大作业",
        course="计算机科学",
        deadline=datetime.now() + timedelta(hours=12),
        created_at=datetime.now() - timedelta(minutes=30)
    )

    homework2 = Homework(
        homework_id="HW002",
        title="高等数学习题",
        course="数学",
        deadline=datetime.now() + timedelta(days=2),
        created_at=datetime.now() - timedelta(days=1)
    )

    # # 批量检查并提醒（阈值设为24小时）
    # results = reminder.batch_check_and_remind([homework1, homework2], threshold_hours=24)
    # 
    # print(f"提醒结果: {results}")
    # 
    print("当前只支持邮箱提醒功能")


@webhooks_bp.route('/scan_due_soon', methods=['POST'])
@login_required
def scan_due_soon():
    """扫描即将截止的作业（24小时内）并发送提醒"""
    try:
        # 获取当前时间
        now = datetime.now()

        # 查询24小时内到期的作业 - 使用正确的集合名称
        urgent_assignments = list(mongo.db.assignments.find({
            'due_date': {'$lte': now + timedelta(days=1), '$gt': now}
        }))

        logger.info(f"扫描到 {len(urgent_assignments)} 个24小时内到期的作业")

        if not urgent_assignments:
            return jsonify({
                'success': True,
                'message': '没有发现24小时内到期的作业',
                'count': 0
            })

        # 使用现有的通知服务发送提醒 - 只发送邮箱提醒
        check_and_send_notifications()

        # 记录发送的作业信息
        assignment_details = []
        for assignment in urgent_assignments:
            assignment_details.append({
                'subject': assignment.get('subject', '未知科目'),
                'title': assignment.get('title', '未知作业'),
                'due_date': assignment.get('due_date', '').strftime('%Y-%m-%d %H:%M:%S') if assignment.get(
                    'due_date') else '未知时间'
            })

        logger.info(f"成功处理 {len(urgent_assignments)} 个即将到期作业的提醒")

        return jsonify({
            'success': True,
            'message': f'已发送{len(urgent_assignments)}个即将到期作业的提醒',
            'count': len(urgent_assignments),
            'assignments': assignment_details
        })

    except Exception as e:
        logger.error(f"扫描即将截止作业失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'扫描失败: {str(e)}'
        }), 500


@webhooks_bp.route('/manual', methods=['POST'])
@login_required
def manual_reminder():
    """手动触发提醒（前端调用）- 只支持邮箱提醒"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': '请求体必须为JSON格式'
            }), 400

        # 支持两种参数格式：assignment_id 或 自由文本
        assignment_id = data.get('assignment_id')
        custom_message = data.get('message')
        subject = data.get('subject', '未知科目')
        title = data.get('title', '未知作业')
        due_date = data.get('due_date')

        logger.info(f"收到手动提醒请求: assignment_id={assignment_id}, subject={subject}, title={title}")

        if assignment_id:
            # 根据assignment_id查询作业信息
            assignment = mongo.db.assignments.find_one({'_id': assignment_id})
            if not assignment:
                return jsonify({
                    'success': False,
                    'error': f'未找到ID为 {assignment_id} 的作业'
                }), 404

            # 构建消息
            due_date_str = assignment.get('due_date', '').strftime('%Y-%m-%d %H:%M:%S') if assignment.get(
                'due_date') else '未知时间'
            message = f"""⚠️ 手动提醒

科目: {assignment.get('subject', '未知科目')}
作业: {assignment.get('title', '未知作业')}
截止时间: {due_date_str}"""

        elif custom_message:
            # 使用自定义消息
            message = custom_message

        else:
            # 使用提供的参数构建消息
            due_date_str = due_date if due_date else '未知时间'
            message = f"""⚠️ 手动提醒

科目: {subject}
作业: {title}
截止时间: {due_date_str}"""

        # 获取当前用户的注册邮箱
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({
                'success': False,
                'error': '用户未登录'
            }), 401

        user = mongo.db.users.find_one({'_id': ObjectId(user_id)})
        if not user or not user.get('email'):
            return jsonify({
                'success': False,
                'error': '未找到用户邮箱，请在设置中配置邮箱'
            }), 400

        to_email = user['email']
        logger.info(f"使用用户注册邮箱发送提醒: {to_email}")

        # 发送邮箱通知
        try:
            # 创建简化的webhook配置对象
            email_config = {
                'type': 'email',
                'enabled': True,
                'config': {
                    'to_email': to_email
                }
            }

            success = send_webhook_notification(email_config, message)
            if success:
                logger.info(f"成功发送到邮箱: {to_email}")
                result = {
                    'success': True,
                    'message': f'手动提醒发送完成 - 成功发送到邮箱: {to_email}',
                    'stats': {
                        'success_count': 1,
                        'failed_count': 0,
                        'sent_to': to_email
                    }
                }
            else:
                logger.warning(f"发送到邮箱失败: {to_email}")
                result = {
                    'success': False,
                    'error': f'发送到邮箱失败: {to_email}',
                    'stats': {
                        'success_count': 0,
                        'failed_count': 1,
                        'sent_to': to_email
                    }
                }
        except Exception as e:
            logger.error(f"发送邮箱通知失败: {str(e)}")
            result = {
                'success': False,
                'error': f'发送邮箱通知失败: {str(e)}',
                'stats': {
                    'success_count': 0,
                    'failed_count': 1,
                    'sent_to': to_email
                }
            }

        logger.info(f"手动提醒处理完成: {result['message']}")
        return jsonify(result)

    except Exception as e:
        logger.error(f"手动提醒失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'手动提醒失败: {str(e)}'
        }), 500


@webhooks_bp.route('/test', methods=['POST'])
@login_required
def test_webhook():
    """测试邮箱webhook配置"""
    try:
        # 发送测试消息
        test_message = f"🔔 Test Reminder\n\nThis is a test message to verify email webhook configuration.\nSent at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

        # 获取当前用户的注册邮箱
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({
                'success': False,
                'error': '用户未登录'
            }), 401

        user = mongo.db.users.find_one({'_id': ObjectId(user_id)})
        if not user or not user.get('email'):
            return jsonify({
                'success': False,
                'error': '未找到用户邮箱，请在设置中配置邮箱'
            }), 400

        to_email = user['email']
        logger.info(f"测试发送到用户注册邮箱: {to_email}")

        # 发送测试通知到邮箱
        try:
            # 创建简化的webhook配置对象
            email_config = {
                'type': 'email',
                'enabled': True,
                'config': {
                    'to_email': to_email
                }
            }

            success = send_webhook_notification(email_config, test_message)
            if success:
                logger.info(f"测试邮件发送成功到: {to_email}")
                return jsonify({
                    'success': True,
                    'message': f'测试完成 - 成功发送到邮箱: {to_email}',
                    'test_message': test_message
                })
            else:
                logger.warning(f"测试邮件发送失败到: {to_email}")
                return jsonify({
                    'success': False,
                    'error': f'测试邮件发送失败到: {to_email}',
                    'test_message': test_message
                })
        except Exception as e:
            logger.error(f"测试邮箱webhook失败: {str(e)}")
            return jsonify({
                'success': False,
                'error': f'测试失败: {str(e)}',
                'test_message': test_message
            })

    except Exception as e:
        logger.error(f"测试webhook失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'测试失败: {str(e)}'
        }), 500
