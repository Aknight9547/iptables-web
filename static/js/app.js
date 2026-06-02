let currentPage = 'dashboard';
let selectedRules = [];

function showPage(page) {
    document.querySelectorAll('[id$="-page"]').forEach(el => el.style.display = 'none');
    document.querySelectorAll('.nav-link').forEach(el => el.classList.remove('active'));
    
    currentPage = page;
    document.getElementById(page + '-page').style.display = 'block';
    
    const navLinks = document.querySelectorAll('.nav-link');
    navLinks.forEach(link => {
        if (link.getAttribute('onclick').includes(page)) {
            link.classList.add('active');
        }
    });
    
    document.getElementById('page-title').textContent = getPageTitle(page);
    
    if (page === 'dashboard') loadDashboard();
    else if (page === 'rules') loadRules();
    else if (page === 'history') loadHistory();
    else if (page === 'templates') loadTemplates();
    else if (page === 'system') loadSystemInfo();
}

function getPageTitle(page) {
    const titles = {
        'dashboard': '仪表盘',
        'rules': '规则管理',
        'history': '历史记录',
        'templates': '规则模板',
        'import_export': '导入导出',
        'system': '系统状态'
    };
    return titles[page] || '未知页面';
}

async function loadDashboard() {
    try {
        const stats = await fetch('/api/system/stats').then(r => r.json());
        document.getElementById('total-rules').textContent = stats.total_rules;
        document.getElementById('filter-rules').textContent = stats.table_stats.filter || 0;
        document.getElementById('nat-rules').textContent = stats.table_stats.nat || 0;
        document.getElementById('mangle-rules').textContent = stats.table_stats.mangle || 0;
        
        const history = await fetch('/api/history?per_page=5').then(r => r.json());
        const tbody = document.querySelector('#recent-history tbody');
        tbody.innerHTML = '';
        
        history.history.forEach(h => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${formatDate(h.created_at)}</td>
                <td>${getActionText(h.action_type)}</td>
                <td>${h.table_name}</td>
                <td>${h.chain_name}</td>
            `;
            tbody.appendChild(row);
        });
    } catch (e) {
        console.error(e);
    }
}

async function loadRules() {
    try {
        const rules = await fetch('/api/rules').then(r => r.json());
        const tbody = document.querySelector('#rules-table tbody');
        tbody.innerHTML = '';
        
        rules.rules.forEach(rule => {
            const row = document.createElement('tr');
            row.dataset.table = rule.table;
            row.dataset.chain = rule.chain;
            row.dataset.number = rule.number;
            
            const checkbox = `<input type="checkbox" class="rule-checkbox" onchange="toggleSelectRule(this, ${rule.number}, '${rule.table}', '${rule.chain}')">`;
            const dport = rule.options ? rule.options.match(/dpt:(\d+)/) : null;
            const sport = rule.options ? rule.options.match(/spt:(\d+)/) : null;
            
            let portInfo = '';
            if (dport) portInfo += `dpt:${dport[1]}`;
            if (sport) portInfo += portInfo ? `, spt:${sport[1]}` : `spt:${sport[1]}`;
            
            if (rule.to_destination) {
                portInfo += portInfo ? ` -> ` : '';
                portInfo += rule.to_destination;
            }
            
            row.innerHTML = `
                <td>${checkbox}</td>
                <td>${rule.number}</td>
                <td>${rule.table}</td>
                <td>${rule.chain}</td>
                <td>${rule.protocol}</td>
                <td>${rule.source}</td>
                <td>${rule.destination}</td>
                <td>${portInfo}</td>
                <td><span class="badge ${getTargetClass(rule.target)}">${rule.target}</span></td>
                <td>
                    <button class="btn btn-sm btn-primary" data-number="${rule.number}" data-table="${rule.table}" data-chain="${rule.chain}" onclick="editRule(${rule.number}, '${rule.table}', '${rule.chain}')">编辑</button>
                    <button class="btn btn-sm btn-danger" onclick="deleteRule(${rule.number}, '${rule.table}', '${rule.chain}')">删除</button>
                </td>
            `;
            tbody.appendChild(row);
        });
        
        document.getElementById('select-all').onchange = function() {
            document.querySelectorAll('.rule-checkbox').forEach(cb => cb.checked = this.checked);
            updateBatchDelete();
        };
    } catch (e) {
        console.error(e);
    }
}

function toggleSelectRule(checkbox, number, table, chain) {
    const key = `${table}-${chain}-${number}`;
    if (checkbox.checked) {
        selectedRules.push({ table, chain, number });
    } else {
        selectedRules = selectedRules.filter(r => !(r.table === table && r.chain === chain && r.number === number));
    }
    updateBatchDelete();
}

function updateBatchDelete() {
    const btn = document.getElementById('batch-delete-btn');
    btn.style.display = selectedRules.length > 0 ? 'inline-block' : 'none';
}

function filterRules() {
    const table = document.getElementById('table-filter').value;
    const chain = document.getElementById('chain-filter').value;
    const search = document.getElementById('search-input').value.toLowerCase();
    
    document.querySelectorAll('#rules-table tbody tr').forEach(row => {
        const rowTable = row.dataset.table;
        const rowChain = row.dataset.chain;
        const rowText = row.textContent.toLowerCase();
        
        const matchTable = !table || rowTable === table;
        const matchChain = !chain || rowChain === chain;
        const matchSearch = !search || rowText.includes(search);
        
        row.style.display = (matchTable && matchChain && matchSearch) ? '' : 'none';
    });
}

function showAddRuleModal() {
    document.getElementById('rule-form').reset();
    document.querySelector('.modal-title').textContent = '添加规则';
    document.querySelector('#rule-form-btn').textContent = '确认添加';
    document.querySelector('#rule-form-btn').setAttribute('data-action', 'add');
    document.getElementById('addRuleModal').style.display = 'block';
    document.getElementById('addRuleModal').classList.add('show');
    document.body.style.overflow = 'hidden';
}

function closeModal(modalId) {
    document.getElementById(modalId).style.display = 'none';
    document.getElementById(modalId).classList.remove('show');
    document.body.style.overflow = '';
}

let editingRule = null;

async function editRule(number, table, chain) {
    editingRule = { number, table, chain };
    
    try {
        const response = await fetch(`/api/rules?table=${table}&chain=${chain}`);
        const result = await response.json();
        const rule = result.rules.find(r => r.number === number);
        
        if (!rule) {
            alert('未找到该规则');
            return;
        }
        
        document.querySelector('select[name="table"]').value = rule.table;
        document.querySelector('select[name="chain"]').value = rule.chain;
        document.querySelector('select[name="target"]').value = rule.target;
        document.querySelector('select[name="protocol"]').value = rule.protocol || '';
        document.querySelector('input[name="source"]').value = rule.source;
        document.querySelector('input[name="destination"]').value = rule.destination;
        
        const dportMatch = rule.options ? rule.options.match(/dpt:(\d+)/) : null;
        const sportMatch = rule.options ? rule.options.match(/spt:(\d+)/) : null;
        if (dportMatch) {
            document.querySelector('input[name="dport"]').value = dportMatch[1];
        }
        if (sportMatch) {
            document.querySelector('input[name="sport"]').value = sportMatch[1];
        }
        
        const inInterface = rule.in || '';
        document.querySelector('input[name="in_interface"]').value = inInterface === '*' ? '' : inInterface;
        
        const outInterface = rule.out || '';
        document.querySelector('input[name="out_interface"]').value = outInterface === '*' ? '' : outInterface;
        
        document.querySelector('.modal-title').textContent = '编辑规则';
        document.querySelector('#rule-form-btn').textContent = '保存修改';
        document.querySelector('#rule-form-btn').setAttribute('data-action', 'edit');
        document.getElementById('addRuleModal').style.display = 'block';
        document.getElementById('addRuleModal').classList.add('show');
        document.body.style.overflow = 'hidden';
    } catch (e) {
        console.error(e);
        alert('加载规则失败: ' + e.message);
    }
}

function submitRuleForm() {
    const form = document.getElementById('rule-form');
    const data = {};
    
    form.querySelectorAll('select, input').forEach(el => {
        if (el.value) {
            data[el.name] = el.value;
        }
    });
    
    const target = data['target'];
    if ((target === 'DNAT' || target === 'SNAT') && !data['to_destination']) {
        alert('请填写DNAT/SNAT目标地址');
        return;
    }
    
    const action = document.querySelector('#rule-form-btn').getAttribute('data-action');
    if (action === 'edit') {
        submitEdit(data);
    } else {
        submitAdd(data);
    }
}

async function submitAdd(data) {
    try {
        const response = await fetch('/api/rules', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        const result = await response.json();
        
        if (result.success) {
            alert('规则添加成功');
            closeModal('addRuleModal');
            loadRules();
        } else {
            alert('添加失败: ' + result.error);
        }
    } catch (e) {
        alert('添加失败: ' + e.message);
    }
}

async function submitEdit(data) {
    try {
        const response = await fetch(`/api/rules/${editingRule.number}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        const result = await response.json();
        
        if (result.success) {
            alert('规则修改成功');
            closeModal('addRuleModal');
            loadRules();
        } else {
            alert('修改失败: ' + result.error);
        }
    } catch (e) {
        alert('修改失败: ' + e.message);
    }
    
    editingRule = null;
}

function deleteRule(number, table, chain) {
    document.getElementById('confirm-message').textContent = `确定要删除这条规则吗？\n表: ${table}, 链: ${chain}, 序号: ${number}`;
    document.getElementById('confirm-btn').onclick = async function() {
        try {
            const response = await fetch(`/api/rules/${table}/${chain}/${number}`, { method: 'DELETE' });
            const result = await response.json();
            
            if (result.success) {
                alert('删除成功');
                loadRules();
            } else {
                alert('删除失败: ' + result.error);
            }
        } catch (e) {
            alert('删除失败: ' + e.message);
        }
        closeModal('confirmModal');
    };
    document.getElementById('confirmModal').style.display = 'block';
    document.getElementById('confirmModal').classList.add('show');
    document.body.style.overflow = 'hidden';
}

function batchDeleteRules() {
    document.getElementById('confirm-message').textContent = `确定要删除选中的 ${selectedRules.length} 条规则吗？`;
    document.getElementById('confirm-btn').onclick = async function() {
        try {
            const response = await fetch('/api/rules/batch-delete', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ rule_ids: selectedRules })
            });
            const result = await response.json();
            
            if (result.success) {
                alert(`成功删除 ${result.results.filter(r => r.success).length} 条规则`);
                selectedRules = [];
                updateBatchDelete();
                loadRules();
            } else {
                alert('批量删除失败');
            }
        } catch (e) {
            alert('批量删除失败: ' + e.message);
        }
        closeModal('confirmModal');
    };
    document.getElementById('confirmModal').style.display = 'block';
    document.getElementById('confirmModal').classList.add('show');
    document.body.style.overflow = 'hidden';
}

async function loadHistory() {
    try {
        const history = await fetch('/api/history').then(r => r.json());
        const tbody = document.querySelector('#history-table tbody');
        tbody.innerHTML = '';
        
        history.history.forEach(h => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${formatDate(h.created_at)}</td>
                <td>${getActionText(h.action_type)}</td>
                <td>${h.table_name}</td>
                <td>${h.chain_name}</td>
                <td>
                    ${h.action_type !== 'rollback' ? `<button class="btn btn-sm btn-warning" onclick="rollback(${h.id})">回滚</button>` : ''}
                </td>
            `;
            tbody.appendChild(row);
        });
    } catch (e) {
        console.error(e);
    }
}

async function rollback(id) {
    document.getElementById('confirm-message').textContent = '确定要回滚此操作吗？';
    document.getElementById('confirm-btn').onclick = async function() {
        try {
            const response = await fetch(`/api/history/${id}/rollback`, { method: 'POST' });
            const result = await response.json();
            
            if (result.success) {
                alert('回滚成功');
                loadHistory();
            } else {
                alert('回滚失败: ' + result.error);
            }
        } catch (e) {
            alert('回滚失败: ' + e.message);
        }
        closeModal('confirmModal');
    };
    document.getElementById('confirmModal').style.display = 'block';
    document.getElementById('confirmModal').classList.add('show');
    document.body.style.overflow = 'hidden';
}

function filterHistory() {
    const startDate = document.getElementById('start-date').value;
    const endDate = document.getElementById('end-date').value;
    const action = document.getElementById('action-filter').value;
    
    let url = '/api/history';
    const params = [];
    if (startDate) params.push(`start_date=${startDate}`);
    if (endDate) params.push(`end_date=${endDate}`);
    if (action) params.push(`action_type=${action}`);
    
    if (params.length > 0) url += '?' + params.join('&');
    
    fetch(url).then(r => r.json()).then(history => {
        const tbody = document.querySelector('#history-table tbody');
        tbody.innerHTML = '';
        
        history.history.forEach(h => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${formatDate(h.created_at)}</td>
                <td>${getActionText(h.action_type)}</td>
                <td>${h.table_name}</td>
                <td>${h.chain_name}</td>
                <td>
                    ${h.action_type !== 'rollback' ? `<button class="btn btn-sm btn-warning" onclick="rollback(${h.id})">回滚</button>` : ''}
                </td>
            `;
            tbody.appendChild(row);
        });
    });
}

function exportHistory() {
    const format = document.getElementById('export-format')?.value || 'json';
    window.open(`/api/history/export?format=${format}`);
}

async function loadTemplates() {
    try {
        const templates = await fetch('/api/templates').then(r => r.json());
        const tbody = document.querySelector('#templates-table tbody');
        tbody.innerHTML = '';
        
        templates.templates.forEach(t => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${t.name}</td>
                <td>${t.description || '-'}</td>
                <td>${t.table_name}</td>
                <td>${t.chain_name}</td>
                <td>${t.is_builtin ? '是' : '否'}</td>
                <td>
                    <button class="btn btn-sm btn-primary" onclick="applyTemplate(${t.id})">应用</button>
                    ${!t.is_builtin ? `<button class="btn btn-sm btn-danger" onclick="deleteTemplate(${t.id})">删除</button>` : ''}
                </td>
            `;
            tbody.appendChild(row);
        });
    } catch (e) {
        console.error(e);
    }
}

function showAddTemplateModal() {
    alert('创建模板功能即将实现');
}

async function applyTemplate(id) {
    try {
        const response = await fetch(`/api/templates/${id}/apply`, { method: 'POST' });
        const result = await response.json();
        
        if (result.success) {
            alert('模板应用成功');
            loadRules();
        } else {
            alert('应用失败: ' + result.error);
        }
    } catch (e) {
        alert('应用失败: ' + e.message);
    }
}

async function deleteTemplate(id) {
    try {
        const response = await fetch(`/api/templates/${id}`, { method: 'DELETE' });
        const result = await response.json();
        
        if (result.success) {
            alert('删除成功');
            loadTemplates();
        } else {
            alert('删除失败: ' + result.message);
        }
    } catch (e) {
        alert('删除失败: ' + e.message);
    }
}

function exportRules() {
    const format = document.getElementById('export-format').value;
    const table = document.getElementById('export-table').value;
    
    let url = `/api/export?format=${format}`;
    if (table) url += `&table=${table}`;
    
    window.open(url);
}

async function previewImport() {
    const content = document.getElementById('import-content').value;
    try {
        const response = await fetch('/api/import/preview', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ content })
        });
        const result = await response.json();
        
        if (result.conflicts && result.conflicts.length > 0) {
            alert(`检测到 ${result.conflicts.length} 条规则冲突`);
        } else {
            alert(`预览成功，共 ${result.preview.length} 条规则`);
        }
    } catch (e) {
        alert('预览失败: ' + e.message);
    }
}

async function importRules() {
    const content = document.getElementById('import-content').value;
    if (!content) {
        alert('请输入要导入的规则内容');
        return;
    }
    
    document.getElementById('confirm-message').textContent = '确定要导入这些规则吗？这将覆盖现有规则。';
    document.getElementById('confirm-btn').onclick = async function() {
        try {
            const response = await fetch('/api/import', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ content })
            });
            const result = await response.json();
            
            if (result.success) {
                alert('导入成功');
                loadRules();
            } else {
                alert('导入失败: ' + result.error);
            }
        } catch (e) {
            alert('导入失败: ' + e.message);
        }
        closeModal('confirmModal');
    };
    document.getElementById('confirmModal').style.display = 'block';
    document.getElementById('confirmModal').classList.add('show');
    document.body.style.overflow = 'hidden';
}

async function loadSystemInfo() {
    try {
        const info = await fetch('/api/system/info').then(r => r.json());
        const tbody = document.getElementById('system-info');
        tbody.innerHTML = '';
        
        for (const [key, value] of Object.entries(info)) {
            const row = document.createElement('tr');
            row.innerHTML = `<td>${key}</td><td>${value}</td>`;
            tbody.appendChild(row);
        }
    } catch (e) {
        console.error(e);
    }
}

function refreshRules() {
    if (currentPage === 'rules') {
        loadRules();
    } else if (currentPage === 'dashboard') {
        loadDashboard();
    }
}

function formatDate(dateStr) {
    const date = new Date(dateStr);
    return date.toLocaleString('zh-CN');
}

function getActionText(action) {
    const texts = {
        'add': '添加',
        'update': '修改',
        'delete': '删除',
        'rollback': '回滚'
    };
    return texts[action] || action;
}

function getTargetClass(target) {
    const classes = {
        'ACCEPT': 'bg-success text-dark',
        'DROP': 'bg-danger text-dark',
        'REJECT': 'bg-warning text-dark',
        'REDIRECT': 'bg-info text-dark',
        'MASQUERADE': 'bg-primary text-dark',
        'DNAT': 'bg-purple text-dark',
        'SNAT': 'bg-indigo text-dark'
    };
    return classes[target] || 'bg-secondary text-dark';
}

function toggleDnatFields() {
    const target = document.querySelector('select[name="target"]').value;
    const dnatFields = document.getElementById('dnat-fields');
    if (target === 'DNAT' || target === 'SNAT') {
        dnatFields.style.display = 'flex';
    } else {
        dnatFields.style.display = 'none';
    }
}

document.addEventListener('DOMContentLoaded', function() {
    showPage('dashboard');
    
    document.querySelectorAll('.modal').forEach(modal => {
        modal.addEventListener('click', function(e) {
            if (e.target === modal) {
                closeModal(modal.id);
            }
        });
    });
});