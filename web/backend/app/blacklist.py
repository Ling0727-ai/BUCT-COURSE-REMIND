# -*- coding: utf-8 -*-
"""
科目黑名单模块

用户可以将不需要追踪的科目加入黑名单：
  - 主界面不再显示该科目的作业/测试
  - scraper 抓取时在 lid 层直接跳过，减少无效请求
"""

import logging
import re
from datetime import datetime
from typing import List, Optional

from bson import ObjectId
from flask import Blueprint, jsonify, request, session

from . import mongo
from .auth import login_required

logger = logging.getLogger(__name__)

blacklist_bp = Blueprint('blacklist', __name__, url_prefix='/api/blacklist')


# ==============================================================================
#  Blacklist 数据模型辅助函数
# ==============================================================================

def _get_blacklist_collection():
    return mongo.db.blacklist


def get_user_blacklisted_ids(user_id: str) -> List[str]:
    """
    获取用户黑名单中所有 subject_id 列表。
    供 scraper / assignments 等模块内部调用。
    """
    try:
        docs = _get_blacklist_collection().find(
            {'user_id': user_id},
            {'subject_id': 1, '_id': 0}
        )
        return [d['subject_id'] for d in docs]
    except Exception as e:
        logger.error(f"获取黑名单失败 user={user_id}: {e}")
        return []


def extract_course_id(url: str) -> Optional[str]:
    """从课程 URL 中提取 courseId 参数，提取不到返回 None。"""
    if not url:
        return None
    m = re.search(r'courseId=(\d+)', url)
    return m.group(1) if m else None


# ==============================================================================
#  API 路由
# ==============================================================================

@blacklist_bp.route('', methods=['GET'])
@login_required
def get_blacklist():
    """获取当前用户的黑名单列表"""
    try:
        user_id = session.get('user_id')
        col = _get_blacklist_collection()
        docs = list(col.find({'user_id': user_id}).sort('created_at', -1))
        result = []
        for d in docs:
            result.append({
                'id': str(d['_id']),
                'subject_id': d.get('subject_id', ''),
                'subject_name': d.get('subject_name', ''),
                'created_at': d.get('created_at', datetime.utcnow()).isoformat()
            })
        return jsonify({'success': True, 'blacklist': result, 'count': len(result)})
    except Exception as e:
        logger.error(f"获取黑名单失败: {e}")
        return jsonify({'success': False, 'error': '获取黑名单失败'}), 500


@blacklist_bp.route('', methods=['POST'])
@login_required
def add_to_blacklist():
    """添加科目到黑名单（幂等）"""
    try:
        user_id = session.get('user_id')
        data = request.get_json() or {}
        subject_id = data.get('subject_id', '').strip()
        if not subject_id:
            return jsonify({'success': False, 'error': 'subject_id 不能为空'}), 400

        col = _get_blacklist_collection()
        # 幂等：已存在则直接返回成功
        existing = col.find_one({'user_id': user_id, 'subject_id': subject_id})
        if existing:
            return jsonify({'success': True, 'message': '已在黑名单中'})

        now = datetime.utcnow()
        col.insert_one({
            'user_id': user_id,
            'subject_id': subject_id,
            'subject_name': data.get('subject_name', ''),
            'created_at': now,
            'updated_at': now
        })

        # 同时确保索引存在（幂等建索引）
        try:
            col.create_index([('user_id', 1), ('subject_id', 1)], unique=True)
        except Exception:
            pass

        return jsonify({'success': True, 'message': '已加入黑名单'})
    except Exception as e:
        logger.error(f"添加黑名单失败: {e}")
        return jsonify({'success': False, 'error': '添加失败'}), 500


@blacklist_bp.route('/<subject_id>', methods=['DELETE'])
@login_required
def remove_from_blacklist(subject_id):
    """从黑名单移除单个科目"""
    try:
        user_id = session.get('user_id')
        col = _get_blacklist_collection()
        col.delete_one({'user_id': user_id, 'subject_id': subject_id})
        return jsonify({'success': True, 'message': '已从黑名单移除'})
    except Exception as e:
        logger.error(f"移除黑名单失败: {e}")
        return jsonify({'success': False, 'error': '移除失败'}), 500


@blacklist_bp.route('', methods=['DELETE'])
@login_required
def clear_blacklist():
    """清空当前用户黑名单"""
    try:
        user_id = session.get('user_id')
        col = _get_blacklist_collection()
        col.delete_many({'user_id': user_id})
        return jsonify({'success': True, 'message': '黑名单已清空'})
    except Exception as e:
        logger.error(f"清空黑名单失败: {e}")
        return jsonify({'success': False, 'error': '清空失败'}), 500

