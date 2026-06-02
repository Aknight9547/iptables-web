from flask import Blueprint, jsonify

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    return 'iptables Web Management Service'

@bp.route('/api')
def api_index():
    return jsonify({
        'endpoints': [
            '/api/rules',
            '/api/history',
            '/api/templates',
            '/api/system/info',
            '/api/system/stats',
            '/api/health',
            '/api/export',
            '/api/import'
        ]
    })

