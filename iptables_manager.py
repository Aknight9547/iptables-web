import subprocess
import shlex
import json
import re
from datetime import datetime, timedelta

class IptablesManager:
    def __init__(self):
        self.tables = ['filter', 'nat', 'mangle', 'raw']
        self.chains = {
            'filter': ['INPUT', 'OUTPUT', 'FORWARD'],
            'nat': ['PREROUTING', 'POSTROUTING', 'INPUT', 'OUTPUT'],
            'mangle': ['PREROUTING', 'POSTROUTING', 'INPUT', 'OUTPUT', 'FORWARD'],
            'raw': ['PREROUTING', 'OUTPUT']
        }
        self.targets = ['ACCEPT', 'DROP', 'REJECT', 'REDIRECT', 'MASQUERADE', 'LOG']
    
    def run_command(self, cmd):
        try:
            args = shlex.split(cmd)
            result = subprocess.run(args, capture_output=True, text=True, check=True)
            return {'success': True, 'output': result.stdout, 'error': ''}
        except subprocess.CalledProcessError as e:
            return {'success': False, 'output': '', 'error': e.stderr}
        except Exception as e:
            return {'success': False, 'output': '', 'error': str(e)}
    
    def list_rules(self, table='filter', chain=None):
        cmd = f'sudo iptables -t {table} -L -n -v --line-numbers'
        result = self.run_command(cmd)
        if not result['success']:
            return []
        
        rules = []
        current_chain = None
        chain_rules = []
        
        for line in result['output'].split('\n'):
            line = line.strip()
            if not line:
                continue
            
            if line.startswith('Chain'):
                if current_chain and chain_rules:
                    rules.extend(chain_rules)
                parts = line.split()
                current_chain = parts[1]
                chain_rules = []
                continue
            
            if current_chain and line[0].isdigit():
                parts = line.split()
                if len(parts) >= 10:
                    options = ' '.join(parts[10:]) if len(parts) > 10 else ''
                    to_destination = ''
                    to_match = re.search(r'to:([\d.:]+)', options)
                    if to_match:
                        to_destination = to_match.group(1)
                    
                    rule = {
                        'number': int(parts[0]),
                        'table': table,
                        'chain': current_chain,
                        'pkts': parts[1],
                        'bytes': parts[2],
                        'target': parts[3],
                        'protocol': parts[4],
                        'opt': parts[5],
                        'in': parts[6],
                        'out': parts[7],
                        'source': parts[8],
                        'destination': parts[9],
                        'options': options,
                        'to_destination': to_destination
                    }
                    chain_rules.append(rule)
        
        if current_chain and chain_rules:
            rules.extend(chain_rules)
        
        if chain:
            rules = [r for r in rules if r['chain'] == chain]
        
        return rules
    
    def get_all_rules(self):
        all_rules = []
        for table in self.tables:
            rules = self.list_rules(table)
            all_rules.extend(rules)
        return all_rules
    
    def add_rule(self, config):
        table = config.get('table', 'filter')
        chain = config.get('chain', 'INPUT')
        protocol = config.get('protocol')
        source = config.get('source')
        destination = config.get('destination')
        sport = config.get('sport')
        dport = config.get('dport')
        in_interface = config.get('in_interface')
        out_interface = config.get('out_interface')
        target = config.get('target', 'ACCEPT')
        state = config.get('state')
        limit = config.get('limit')
        to_destination = config.get('to_destination')
        
        cmd = f'sudo iptables -t {table} -A {chain}'
        
        if protocol:
            cmd += f' -p {protocol}'
        if source:
            cmd += f' -s {source}'
        if destination:
            cmd += f' -d {destination}'
        
        if in_interface and in_interface != '*':
            if chain != 'POSTROUTING':
                cmd += f' -i {in_interface}'
        
        if out_interface and out_interface != '*':
            if chain != 'PREROUTING':
                cmd += f' -o {out_interface}'
        
        if sport and protocol:
            cmd += f' --sport {sport}'
        if dport and protocol:
            cmd += f' --dport {dport}'
        if state:
            cmd += f' -m state --state {state}'
        if limit:
            cmd += f' -m limit --limit {limit}'
        cmd += f' -j {target}'
        
        if to_destination:
            if target == 'DNAT':
                cmd += f' --to-destination {to_destination}'
            elif target == 'SNAT':
                cmd += f' --to-source {to_destination}'
        
        result = self.run_command(cmd)
        
        if result['success']:
            rules = self.list_rules(table, chain)
            if rules:
                result['rule_number'] = len(rules)
        
        return result
    
    def delete_rule(self, table, chain, rule_number):
        cmd = f'sudo iptables -t {table} -D {chain} {rule_number}'
        return self.run_command(cmd)
    
    def update_rule(self, table, chain, rule_number, new_config):
        delete_result = self.delete_rule(table, chain, rule_number)
        if not delete_result['success']:
            return delete_result
        
        new_config['table'] = table
        new_config['chain'] = chain
        return self.add_rule(new_config)
    
    def save_rules(self, path=None):
        if path:
            cmd = f'sudo iptables-save > {path}'
        else:
            cmd = 'sudo iptables-save'
        return self.run_command(cmd)
    
    def restore_rules(self, content):
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.iptables', delete=False) as f:
            f.write(content)
            temp_path = f.name
        
        try:
            cmd = f'sudo iptables-restore < {temp_path}'
            result = self.run_command(cmd)
            return result
        finally:
            import os
            os.unlink(temp_path)
    
    def get_stats(self):
        stats = {
            'total_rules': 0,
            'table_stats': {}
        }
        
        for table in self.tables:
            rules = self.list_rules(table)
            count = len(rules)
            stats['table_stats'][table] = count
            stats['total_rules'] += count
        
        return stats
    
    def get_chain_policy(self, table, chain):
        cmd = f'sudo iptables -t {table} -L {chain} -n'
        result = self.run_command(cmd)
        if not result['success']:
            return None
        
        for line in result['output'].split('\n'):
            if line.startswith('Chain'):
                parts = line.split()
                if len(parts) > 3 and parts[2] == 'policy':
                    return parts[3]
        return None