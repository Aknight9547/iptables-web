from flask import Blueprint, request, jsonify
from models import RuleHistory, db
from datetime import datetime, timedelta
import json
import re
from iptables_manager import IptablesManager

history_bp = Blueprint('history', __name__)
iptables = IptablesManager()

@history_bp.route('/api/history', methods=['GET'])
def get_history():
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 20))
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    action_type = request.args.get('action_type')
    
    query = RuleHistory.query.order_by(RuleHistory.created_at.desc())
    
    if action_type:
        query = query.filter(RuleHistory.action_type == action_type)
    
    if start_date:
        try:
            start = datetime.strptime(start_date, '%Y-%m-%d')
            query = query.filter(RuleHistory.created_at >= start)
        except:
            pass
    
    if end_date:
        try:
            end = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)
            query = query.filter(RuleHistory.created_at < end)
        except:
            pass
    
    total = query.count()
    history = query.offset((page - 1) * per_page).limit(per_page).all()
    
    result = []
    for h in history:
        result.append({
            'id': h.id,
            'action_type': h.action_type,
            'table_name': h.table_name,
            'chain_name': h.chain_name,
            'rule_content': h.rule_content,
            'old_rule_content': h.old_rule_content,
            'rule_number': h.rule_number,
            'operator_ip': h.operator_ip,
            'created_at': h.created_at.isoformat(),
            'notes': h.notes
        })
    
    return jsonify({'history': result, 'total': total, 'page': page})

def convert_rule_format(rule):
    config = {
        'table': rule.get('table', 'filter'),
        'chain': rule.get('chain', 'INPUT'),
        'protocol': rule.get('protocol'),
        'source': rule.get('source'),
        'destination': rule.get('destination'),
        'in_interface': rule.get('in'),
        'out_interface': rule.get('out'),
        'target': rule.get('target', 'ACCEPT')
    }
    
    options = rule.get('options', '')
    if options:
        dport_match = re.search(r'dpt:(\d+)', options)
        if dport_match:
            config['dport'] = dport_match.group(1)
        
        sport_match = re.search(r'spt:(\d+)', options)
        if sport_match:
            config['sport'] = sport_match.group(1)
        
        to_match = re.search(r'to:([\d.:]+)', options)
        if to_match:
            config['to_destination'] = to_match.group(1)
    
    return config

@history_bp.route('/api/history/<int:history_id>/rollback', methods=['POST'])
def rollback(history_id):
    history = RuleHistory.query.get(history_id)
    if not history:
        return jsonify({'success': False, 'error': '历史记录不存在'})
    
    if history.action_type == 'add':
        rule_num = history.rule_number
        if not rule_num:
            rules = iptables.list_rules(history.table_name, history.chain_name)
            if rules:
                rule_num = len(rules)
            else:
                rule_num = 1
        result = iptables.delete_rule(history.table_name, history.chain_name, rule_num)
    elif history.action_type == 'delete':
        try:
            rule = json.loads(history.rule_content)
            config = convert_rule_format(rule)
            result = iptables.add_rule(config)
        except Exception as e:
            return jsonify({'success': False, 'error': f'无法解析规则配置: {str(e)}'})
    elif history.action_type == 'update':
        try:
            old_rule = json.loads(history.old_rule_content) if history.old_rule_content else {}
            old_config = convert_rule_format(old_rule) if isinstance(old_rule, dict) else {}
            rule_num = history.rule_number or 1
            result = iptables.update_rule(history.table_name, history.chain_name, rule_num, old_config)
        except Exception as e:
            return jsonify({'success': False, 'error': f'无法解析规则配置: {str(e)}'})
    else:
        return jsonify({'success': False, 'error': '不支持的操作类型'})
    
    if result['success']:
        rollback_history = RuleHistory(
            action_type='rollback',
            table_name=history.table_name,
            chain_name=history.chain_name,
            rule_content=f'Rollback from {history_id}',
            old_rule_content=history.rule_content,
            operator_ip=request.remote_addr
        )
        db.session.add(rollback_history)
        db.session.commit()
    
    return jsonify(result)

@history_bp.route('/api/history/export', methods=['GET'])
def export_history():
    from flask import Response
    format_type = request.args.get('format', 'json')
    
    history = RuleHistory.query.all()
    data = []
    for h in history:
        data.append({
            'id': h.id,
            'action_type': h.action_type,
            'table_name': h.table_name,
            'chain_name': h.chain_name,
            'rule_content': h.rule_content,
            'old_rule_content': h.old_rule_content,
            'created_at': h.created_at.isoformat()
        })
    
    if format_type == 'csv':
        import csv
        from io import StringIO
        output = StringIO()
        writer = csv.writer(output)
        writer.writerow(['id', 'action_type', 'table_name', 'chain_name', 'rule_content', 'old_rule_content', 'created_at'])
        for row in data:
            writer.writerow([row['id'], row['action_type'], row['table_name'], row['chain_name'], row['rule_content'], row['old_rule_content'], row['created_at']])
        return Response(output.getvalue(), mimetype='text/csv', headers={'Content-Disposition': 'attachment; filename=history.csv'})
    else:
        return jsonify(data)