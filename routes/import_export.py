from flask import Blueprint, request, jsonify
from iptables_manager import IptablesManager
import json
import csv

import_export_bp = Blueprint('import_export', __name__)
iptables = IptablesManager()

@import_export_bp.route('/api/export', methods=['GET'])
def export_rules():
    from flask import Response
    format_type = request.args.get('format', 'iptables')
    table = request.args.get('table')
    
    if format_type == 'iptables':
        result = iptables.save_rules()
        if result['success']:
            return Response(result['output'], mimetype='text/plain', headers={'Content-Disposition': 'attachment; filename=iptables-backup.txt'})
        else:
            return jsonify(result)
    
    elif format_type == 'json':
        if table:
            rules = iptables.list_rules(table)
        else:
            rules = iptables.get_all_rules()
        return jsonify({'rules': rules})
    
    elif format_type == 'csv':
        if table:
            rules = iptables.list_rules(table)
        else:
            rules = iptables.get_all_rules()
        
        output = []
        if rules:
            headers = rules[0].keys()
            output.append(','.join(headers))
            for rule in rules:
                row = []
                for h in headers:
                    val = rule.get(h, '')
                    if isinstance(val, str) and ',' in val:
                        val = f'"{val}"'
                    row.append(str(val))
                output.append(','.join(row))
        
        return Response('\n'.join(output), mimetype='text/csv', headers={'Content-Disposition': 'attachment; filename=iptables-rules.csv'})
    
    return jsonify({'success': False, 'message': '不支持的格式'})

@import_export_bp.route('/api/import', methods=['POST'])
def import_rules():
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'message': '无数据'})
    
    if 'content' in data:
        result = iptables.restore_rules(data['content'])
        return jsonify(result)
    
    elif 'rules' in data:
        rules = data['rules']
        success_count = 0
        failed_count = 0
        
        for rule in rules:
            result = iptables.add_rule(rule)
            if result['success']:
                success_count += 1
            else:
                failed_count += 1
        
        return jsonify({
            'success': failed_count == 0,
            'imported_count': success_count,
            'failed_count': failed_count,
            'message': f'成功导入 {success_count} 条规则，失败 {failed_count} 条'
        })
    
    return jsonify({'success': False, 'message': '无效的数据格式'})

@import_export_bp.route('/api/import/preview', methods=['POST'])
def preview_import():
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'message': '无数据'})
    
    preview = []
    conflicts = []
    
    if 'content' in data:
        lines = data['content'].strip().split('\n')
        for line in lines:
            if line and not line.startswith('#'):
                preview.append({'command': line, 'type': 'iptables-save'})
    
    elif 'rules' in data:
        current_rules = iptables.get_all_rules()
        for rule in data['rules']:
            table = rule.get('table', 'filter')
            chain = rule.get('chain', 'INPUT')
            dport = rule.get('dport')
            
            exists = False
            for cr in current_rules:
                if cr['table'] == table and cr['chain'] == chain:
                    if dport and cr.get('options', '').find(f'dpt:{dport}') != -1:
                        exists = True
                        break
            
            if exists:
                conflicts.append(rule)
            preview.append(rule)
    
    return jsonify({'preview': preview, 'conflicts': conflicts})