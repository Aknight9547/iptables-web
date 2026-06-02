from flask import Blueprint, jsonify
import os
import platform
from iptables_manager import IptablesManager

system_bp = Blueprint('system', __name__)
iptables = IptablesManager()

@system_bp.route('/api/system/info', methods=['GET'])
def get_system_info():
    info = {
        'hostname': os.uname().nodename,
        'os_version': platform.platform(),
        'kernel_version': os.uname().release,
        'python_version': platform.python_version(),
        'status': 'running'
    }
    return jsonify(info)

@system_bp.route('/api/system/stats', methods=['GET'])
def get_stats():
    stats = iptables.get_stats()
    return jsonify(stats)

@system_bp.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'ok', 'timestamp': str(__import__('datetime').datetime.now())})