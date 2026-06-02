from flask import Blueprint, request, jsonify
from iptables_manager import IptablesManager
from models import RuleHistory, db
from datetime import datetime
import json

rules_bp = Blueprint('rules', __name__)
iptables = IptablesManager()

@rules_bp.route('/api/rules', methods=['GET'])
def get_rules():
    table = request.args.get('table')
    chain = request.args.get('chain')
    search = request.args.get('search', '')
    
    if table:
        rules = iptables.list_rules(table, chain)
    else:
        rules = iptables.get_all_rules()
    
    if search:
        rules = [r for r in rules if search.lower() in str(r).lower()]
    
    return jsonify({'rules': rules, 'total': len(rules)})

@rules_bp.route('/api/rules', methods=['POST'])
def add_rule():
    config = request.get_json()
    operator_ip = request.remote_addr
    
    result = iptables.add_rule(config)
    
    if result['success']:
        history = RuleHistory(
            action_type='add',
            table_name=config.get('table', 'filter'),
            chain_name=config.get('chain', 'INPUT'),
            rule_content=json.dumps(config),
            rule_number=result.get('rule_number'),
            operator_ip=operator_ip
        )
        db.session.add(history)
        db.session.commit()
    
    return jsonify(result)

@rules_bp.route('/api/rules/<int:rule_number>', methods=['PUT'])
def update_rule(rule_number):
    config = request.get_json()
    table = config.get('table', 'filter')
    chain = config.get('chain', 'INPUT')
    operator_ip = request.remote_addr
    
    old_rules = iptables.list_rules(table, chain)
    old_rule = next((r for r in old_rules if r['number'] == rule_number), None)
    
    if not old_rule:
        return jsonify({'success': False, 'error': '规则不存在'})
    
    result = iptables.update_rule(table, chain, rule_number, config)
    
    if result['success']:
        history = RuleHistory(
            action_type='update',
            table_name=table,
            chain_name=chain,
            rule_content=json.dumps(config),
            old_rule_content=json.dumps(old_rule) if old_rule else None,
            rule_number=rule_number,
            operator_ip=operator_ip
        )
        db.session.add(history)
        db.session.commit()
    
    return jsonify(result)

@rules_bp.route('/api/rules/<table>/<chain>/<int:rule_number>', methods=['DELETE'])
def delete_rule(table, chain, rule_number):
    operator_ip = request.remote_addr
    
    old_rules = iptables.list_rules(table, chain)
    old_rule = next((r for r in old_rules if r['number'] == rule_number), None)
    
    result = iptables.delete_rule(table, chain, rule_number)
    
    if result['success']:
        history = RuleHistory(
            action_type='delete',
            table_name=table,
            chain_name=chain,
            rule_content=json.dumps(old_rule) if old_rule else '',
            operator_ip=operator_ip
        )
        db.session.add(history)
        db.session.commit()
    
    return jsonify(result)

@rules_bp.route('/api/rules/batch-delete', methods=['POST'])
def batch_delete_rules():
    data = request.get_json()
    rule_ids = data.get('rule_ids', [])
    results = []
    
    for rule_info in rule_ids:
        table = rule_info.get('table', 'filter')
        chain = rule_info.get('chain', 'INPUT')
        number = rule_info.get('number')
        
        if number:
            result = iptables.delete_rule(table, chain, number)
            results.append({'table': table, 'chain': chain, 'number': number, 'success': result['success']})
    
    return jsonify({'success': all(r['success'] for r in results), 'results': results})