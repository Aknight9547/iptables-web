from flask import Blueprint, request, jsonify
from iptables_manager import IptablesManager
import json
import csv

import_export_bp = Blueprint('import_export', __name__)
iptables = IptablesManager()

def parse_iptables_save(content):
    rules = []
    current_table = 'filter'
    current_chain = None
    
    lines = content.strip().split('\n')
    for line in lines:
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        
        if line.startswith('*'):
            current_table = line[1:]
            continue
        
        if line.startswith(':'):
            parts = line.split()
            current_chain = parts[0][1:]
            continue
        
        if line.startswith('-A'):
            rules.append({
                'table': current_table,
                'command': line,
                'type': 'append'
            })
        
        if line.startswith('-D'):
            rules.append({
                'table': current_table,
                'command': line,
                'type': 'delete'
            })
        
        if line.startswith('-I'):
            rules.append({
                'table': current_table,
                'command': line,
                'type': 'insert'
            })
    
    return rules

def parse_json_rules(content):
    try:
        data = json.loads(content)
        if isinstance(data, list):
            return data
        elif isinstance(data, dict) and 'rules' in data:
            return data['rules']
    except:
        pass
    return []

@import_export_bp.route('/api/export', methods=['GET'])
def export_rules():
    from flask import Response
    format_type = request.args.get('format', 'iptables')
    table = request.args.get('table')
    
    if format_type == 'iptables':
        if table:
            result = iptables.run_command(f'sudo iptables-save -t {table}')
        else:
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
        content = data['content']
        try:
            parsed_rules = json.loads(content)
            if isinstance(parsed_rules, dict) and 'rules' in parsed_rules:
                parsed_rules = parsed_rules['rules']
            if isinstance(parsed_rules, list):
                success_count = 0
                failed_count = 0
                errors = []
                
                for rule in parsed_rules:
                    result = iptables.add_rule(rule)
                    if result['success']:
                        success_count += 1
                    else:
                        failed_count += 1
                        errors.append(result.get('error', 'Unknown error'))
                
                return jsonify({
                    'success': failed_count == 0,
                    'imported_count': success_count,
                    'failed_count': failed_count,
                    'message': f'成功导入 {success_count} 条规则，失败 {failed_count} 条',
                    'errors': errors
                })
        except json.JSONDecodeError:
            pass
        
        result = iptables.restore_rules(content)
        return jsonify(result)
    
    elif 'rules' in data:
        rules = data['rules']
        success_count = 0
        failed_count = 0
        errors = []
        
        for rule in rules:
            result = iptables.add_rule(rule)
            if result['success']:
                success_count += 1
            else:
                failed_count += 1
                errors.append(result.get('error', 'Unknown error'))
        
        return jsonify({
            'success': failed_count == 0,
            'imported_count': success_count,
            'failed_count': failed_count,
            'message': f'成功导入 {success_count} 条规则，失败 {failed_count} 条',
            'errors': errors
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
        content = data['content']
        
        try:
            parsed_rules = json.loads(content)
            if isinstance(parsed_rules, dict) and 'rules' in parsed_rules:
                parsed_rules = parsed_rules['rules']
            if isinstance(parsed_rules, list):
                current_rules = iptables.get_all_rules()
                for rule in parsed_rules:
                    table = rule.get('table', 'filter')
                    chain = rule.get('chain', 'INPUT')
                    dport = rule.get('dport')
                    destination = rule.get('destination')
                    
                    exists = False
                    for cr in current_rules:
                        if cr['table'] == table and cr['chain'] == chain:
                            if dport and cr.get('options', '').find(f'dpt:{dport}') != -1:
                                exists = True
                                break
                            if destination and cr.get('destination') == destination:
                                exists = True
                                break
                    
                    if exists:
                        conflicts.append(rule)
                    preview.append({
                        'type': 'json',
                        'table': table,
                        'chain': chain,
                        'description': f"{table} {chain} {'dport:' + str(dport) if dport else ''}"
                    })
                return jsonify({'preview': preview, 'conflicts': conflicts})
        except json.JSONDecodeError:
            pass
        
        rules = parse_iptables_save(content)
        for rule in rules:
            preview.append({
                'type': 'iptables-save',
                'table': rule['table'],
                'command': rule['command'],
                'description': f"{rule['table']}: {rule['command'][:50]}..."
            })
    
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