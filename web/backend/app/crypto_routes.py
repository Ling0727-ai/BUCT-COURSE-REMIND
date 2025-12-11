"""
加密相关路由
提供RSA公钥获取等加密服务
"""

from flask import Blueprint, jsonify, current_app

from .rsa_crypto import get_rsa_crypto

crypto_bp = Blueprint('crypto', __name__, url_prefix='/api/crypto')


@crypto_bp.route('/public-key', methods=['GET'])
def get_public_key():
    """获取RSA公钥"""
    try:
        rsa_crypto = get_rsa_crypto()

        # 检查RSA是否启用
        if not rsa_crypto.is_enabled():
            current_app.logger.info("RSA加密已禁用")
            return jsonify({
                'success': False,
                'error': 'RSA加密已禁用',
                'disabled': True
            }), 200

        key_info = rsa_crypto.get_public_key_info()

        # 检查公钥是否获取成功
        if key_info is None:
            current_app.logger.error("RSA公钥获取失败：无法生成密钥对")
            return jsonify({
                'success': False,
                'error': '无法生成RSA密钥对'
            }), 500

        current_app.logger.info("RSA公钥获取成功")
        return jsonify({
            'success': True,
            'data': key_info
        })

    except Exception as e:
        current_app.logger.error(f"获取RSA公钥失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': '获取公钥失败'
        }), 500


@crypto_bp.route('/challenge', methods=['GET'])
def get_challenge():
    """获取加密挑战"""
    try:
        rsa_crypto = get_rsa_crypto()
        challenge_data = rsa_crypto.create_challenge()

        current_app.logger.info("加密挑战生成成功")
        return jsonify({
            'success': True,
            'data': challenge_data
        })

    except Exception as e:
        current_app.logger.error(f"生成加密挑战失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': '生成挑战失败'
        }), 500
