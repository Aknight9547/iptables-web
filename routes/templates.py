from flask import Blueprint, request, jsonify
from models import RuleTemplate, db
from datetime import datetime
import json
from iptables_manager import IptablesManager

templates_bp = Blueprint('templates', __name__)
iptables = IptablesManager()

DEFAULT_TEMPLATES = [
    {'name': '开放SSH端口', 'description': '允许SSH连接（端口22）', 'table': 'filter', 'chain': 'INPUT', 'config': {'protocol': 'tcp', 'dport': '22', 'target': 'ACCEPT'}},
    {'name': '开放HTTP端口', 'description': '允许HTTP访问（端口80）', 'table': 'filter', 'chain': 'INPUT', 'config': {'protocol': 'tcp', 'dport': '80', 'target': 'ACCEPT'}},
    {'name': '开放HTTPS端口', 'description': '允许HTTPS访问（端口443）', 'table': 'filter', 'chain': 'INPUT', 'config': {'protocol': 'tcp', 'dport': '443', 'target': 'ACCEPT'}},
    {'name': '开放MySQL端口', 'description': '允许MySQL连接（端口3306）', 'table': 'filter', 'chain': 'INPUT', 'config': {'protocol': 'tcp', 'dport': '3306', 'target': 'ACCEPT'}},
    {'name': '开放Redis端口', 'description': '允许Redis连接（端口6379）', 'table': 'filter', 'chain': 'INPUT', 'config': {'protocol': 'tcp', 'dport': '6379', 'target': 'ACCEPT'}},
    {'name': '禁止Ping响应', 'description': '拒绝ICMP请求', 'table': 'filter', 'chain': 'INPUT', 'config': {'protocol': 'icmp', 'target': 'DROP'}},
    {'name': '允许已建立连接', 'description': '允许已建立和相关连接通过', 'table': 'filter', 'chain': 'INPUT', 'config': {'protocol': 'tcp', 'state': 'ESTABLISHED,RELATED', 'target': 'ACCEPT'}},
    {'name': '允许本地回环', 'description': '允许本地回环接口通信', 'table': 'filter', 'chain': 'INPUT', 'config': {'source': '127.0.0.1', 'target': 'ACCEPT'}},
]

def init_templates():
    import sqlite3
    try:
        cursor = db.session.connection().connection.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='rule_template'")
        if not cursor.fetchone():
            db.create_all()
        
        for template in DEFAULT_TEMPLATES:
            existing = RuleTemplate.query.filter_by(name=template['name']).first()
            if not existing:
                new_template = RuleTemplate(
                    name=template['name'],
                    description=template['description'],
                    table_name=template['table'],
                    chain_name=template['chain'],
                    rule_config=json.dumps(template['config']),
                    is_builtin=True
                )
                db.session.add(new_template)
        db.session.commit()
    except Exception as e:
        print(f"Error initializing templates: {e}")
        db.session.rollback()

@templates_bp.route('/api/templates', methods=['GET'])
def get_templates():
    templates = RuleTemplate.query.all()
    result = []
    for t in templates:
        result.append({
            'id': t.id,
            'name': t.name,
            'description': t.description,
            'table_name': t.table_name,
            'chain_name': t.chain_name,
            'rule_config': json.loads(t.rule_config),
            'category': t.category,
            'is_builtin': t.is_builtin,
            'created_at': t.created_at.isoformat()
        })
    return jsonify({'templates': result})

@templates_bp.route('/api/templates/<int:template_id>/apply', methods=['POST'])
def apply_template(template_id):
    template = RuleTemplate.query.get(template_id)
    if not template:
        return jsonify({'success': False, 'message': '模板不存在'})
    
    try:
        config = json.loads(template.rule_config)
        config['table'] = template.table_name
        config['chain'] = template.chain_name
        
        result = iptables.add_rule(config)
        if result['success']:
            result['message'] = f'规则 "{template.name}" 已应用'
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@templates_bp.route('/api/templates', methods=['POST'])
def create_template():
    data = request.get_json()
    name = data.get('name')
    description = data.get('description', '')
    table_name = data.get('table', 'filter')
    chain_name = data.get('chain', 'INPUT')
    rule_config = data.get('rule_config', {})
    
    if not name:
        return jsonify({'success': False, 'message': '模板名称不能为空'})
    
    existing = RuleTemplate.query.filter_by(name=name).first()
    if existing:
        return jsonify({'success': False, 'message': '模板名称已存在'})
    
    template = RuleTemplate(
        name=name,
        description=description,
        table_name=table_name,
        chain_name=chain_name,
        rule_config=json.dumps(rule_config),
        is_builtin=False
    )
    db.session.add(template)
    db.session.commit()
    
    return jsonify({'success': True, 'template_id': template.id})

@templates_bp.route('/api/templates/<int:template_id>', methods=['DELETE'])
def delete_template(template_id):
    template = RuleTemplate.query.get(template_id)
    if not template:
        return jsonify({'success': False, 'message': '模板不存在'})
    
    if template.is_builtin:
        return jsonify({'success': False, 'message': '内置模板不能删除'})
    
    db.session.delete(template)
    db.session.commit()
    
    return jsonify({'success': True})