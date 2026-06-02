# iptables Web管理服务 - 需求文档 (PRD)

## 1. 项目概述

**项目名称**: iptables-web
**项目类型**: Web管理控制台
**核心功能**: 为Linux系统提供基于Web界面的iptables规则管理能力
**目标用户**: 系统管理员、网络运维人员

### 1.1 业务背景
传统的iptables管理需要通过命令行操作，对操作人员的技术要求较高，且容易出现误操作。本系统通过Web界面提供可视化的规则管理，降低操作风险，提高管理效率。

### 1.2 项目范围
- ✅ 单台Linux服务器管理
- ✅ iptables规则查看、添加、修改、删除
- ✅ 规则变更历史记录与回滚
- ✅ 多表支持（filter、nat、mangle等）
- ❌ 用户认证系统
- ❌ 远程服务器管理

---

## 2. 功能需求

### 2.1 核心功能模块

#### 2.1.1 规则查看模块
**功能描述**: 以表格形式展示当前iptables的所有规则

**支持功能**:
- 按表（table）筛选：filter、nat、mangle、raw等
- 按链（chain）筛选：INPUT、OUTPUT、FORWARD、PREROUTING、POSTROUTING
- 规则详情展示：
  - 序号
  - 所属表（table）
  - 所属链（chain）
  - 规则条件（源地址、目标地址、端口、协议等）
  - 目标动作（ACCEPT、DROP、REJECT、LOG等）
  - 匹配计数（packets、bytes）
  - 备注/描述
- 支持搜索和过滤
- 实时刷新规则列表

**界面展示**:
```
┌─────┬───────┬────────┬────────────┬────────────┬─────────┬─────────┬────────────┬─────────────┐
│ 序号 │  表   │  链   │ 源地址     │ 目标地址   │ 协议   │ 端口    │ 动作       │ 操作        │
├─────┼───────┼────────┼────────────┼────────────┼─────────┼─────────┼────────────┼─────────────┤
│  1  │ filter│ INPUT │ 0.0.0.0/0  │ 0.0.0.0/0  │  tcp   │  22     │  ACCEPT   │ [编辑][删除]│
│  2  │ filter│ INPUT │ 0.0.0.0/0  │ 0.0.0.0/0  │  tcp   │  80     │  ACCEPT   │ [编辑][删除]│
│  3  │ filter│ INPUT │ 0.0.0.0/0  │ 0.0.0.0/0  │  all   │   -     │  DROP     │ [编辑][删除]│
└─────┴───────┴────────┴────────────┴────────────┴─────────┴─────────┴────────────┴─────────────┘
```

#### 2.1.2 规则添加模块
**功能描述**: 创建新的iptables规则

**支持配置的参数**:
- 目标表（table）：filter（默认）、nat、mangle、raw
- 目标链（chain）：INPUT、OUTPUT、FORWARD、PREROUTING、POSTROUTING
- 协议类型（protocol）：tcp、udp、icmp、all
- 源地址（source）：IP地址或网段（如：192.168.1.0/24）
- 目标地址（destination）：IP地址或网段
- 源端口（source port）：端口号或范围（如：1024:65535）
- 目标端口（destination port）：端口号或范围
- 入接口（input interface）：网卡名称
- 出接口（output interface）：网卡名称
- 目标动作（target）：ACCEPT、DROP、REJECT、REDIRECT、MASQUERADE等
- 扩展匹配：
  - 状态匹配（state）：NEW、ESTABLISHED、RELATED、INVALID
  - 连接数限制（connlimit）
  - 速率限制（limit）
- 备注信息：用于描述规则用途

**表单验证**:
- IP地址格式验证
- 端口范围验证（1-65535）
- 规则冲突检测
- 必填项检查

#### 2.1.3 规则编辑模块
**功能描述**: 修改现有的iptables规则

**支持功能**:
- 修改任意规则参数
- 规则顺序调整（通过拖拽或序号设置）
- 批量编辑
- 修改前显示原规则，修改后预览新规则
- 冲突检测

#### 2.1.4 规则删除模块
**功能描述**: 删除不需要的iptables规则

**支持功能**:
- 单条删除
- 批量删除（勾选多条规则）
- 删除确认对话框
- 删除前备份到历史记录

#### 2.1.5 规则历史与回滚模块
**功能描述**: 记录所有规则变更，支持回滚到历史版本

**功能细节**:
- 记录每次规则变更的：
  - 变更时间
  - 操作类型（添加、修改、删除）
  - 原规则内容
  - 新规则内容
  - 操作人（可记录IP地址或系统用户）
- 历史记录列表：
  ```
  ┌────────┬─────────────┬──────────┬────────────────────┬────────────────────┐
  │  时间  │  操作类型   │  操作人  │     原规则          │     新规则         │
  ├────────┼─────────────┼──────────┼────────────────────┼────────────────────┤
  │06-01 10:00│  添加    │ admin   │ -                  │ 允许TCP 80端口      │
  │06-01 09:30│  修改    │ admin   │ 允许TCP 22端口     │ 允许TCP 22端口(限IP)│
  │06-01 09:00│  删除    │ admin   │ 拒绝所有           │ -                  │
  └────────┴─────────────┴──────────┴────────────────────┴────────────────────┘
  ```
- 回滚功能：
  - 选择历史版本
  - 预览回滚后的规则变更
  - 确认回滚
  - 回滚记录自动保存
- 历史记录保留期限：默认30天，可配置
- 历史记录导出：支持JSON/CSV格式导出

#### 2.1.6 规则模板模块
**功能描述**: 提供常用的规则模板，快速创建常见规则

**预置模板**:
- 开放SSH端口（22）
- 开放HTTP端口（80）
- 开放HTTPS端口（443）
- 开放所有HTTP/HTTPS
- 开放MySQL端口（3306）
- 开放Redis端口（6379）
- 禁止ping响应
- 允许已建立连接
- 端口转发（DNAT）
- SNAT配置
- 防止DDoS基础防护
- 允许本地回环

**模板功能**:
- 一键应用模板
- 自定义模板创建
- 模板参数编辑
- 模板分类管理

#### 2.1.7 系统状态监控模块
**功能描述**: 显示iptables状态和系统信息

**监控内容**:
- iptables服务状态（是否运行）
- 规则总数统计
- 各表规则数量统计
- 各链规则数量统计
- 实时流量监控（可选）
- 系统基本信息：
  - 系统版本
  - 内核版本
  - 负载状态
  - 内存使用情况
  - CPU使用率

#### 2.1.8 规则导入导出模块
**功能描述**: 支持规则的备份和恢复

**导出功能**:
- 导出所有表和链的规则
- 导出格式：iptables-save格式
- 支持JSON格式导出
- 支持CSV格式导出（用于Excel查看）

**导入功能**:
- 导入iptables-restore格式文件
- 导入JSON格式规则
- 导入前规则冲突检测
- 导入前备份当前规则
- 导入预览和确认

---

## 3. 非功能需求

### 3.1 性能需求
- 规则列表加载时间：< 2秒（规则数<1000）
- 规则添加/修改响应时间：< 1秒
- 并发用户数：支持单用户（无认证场景）
- 系统资源占用：CPU < 5%，内存 < 100MB

### 3.2 安全性需求
- 所有iptables操作需要root权限（通过sudo）
- 操作日志完整记录
- 危险操作二次确认（如：删除所有规则、清空链）
- 防止恶意注入iptables命令
- 命令参数严格验证

### 3.3 可靠性需求
- 每次规则变更前自动备份
- 操作失败自动回滚
- 服务异常自动恢复
- 规则变更原子性保证

### 3.4 可用性需求
- 支持主流浏览器：Chrome、Firefox、Safari、Edge
- 响应式设计：支持桌面端和移动端
- 操作友好：错误提示明确、操作反馈及时
- 帮助文档：每个功能模块提供使用说明

### 3.5 可维护性需求
- 日志记录：操作日志、错误日志、访问日志
- 配置管理：配置文件管理，支持环境变量配置
- 升级维护：支持平滑升级，不影响现有规则

---

## 4. 技术架构

### 4.1 技术栈

**后端**:
- **框架**: Python Flask
- **数据库**: SQLite（用于存储历史记录和规则模板）
- **任务队列**: 不需要（单线程操作）

**前端**:
- **技术**: HTML5 + CSS3 + JavaScript
- **框架**: Bootstrap 5（响应式UI）
- **图标**: Font Awesome
- **表格插件**: DataTables（支持搜索、分页、排序）
- **HTTP请求**: 原生Fetch API

**系统集成**:
- **iptables操作**: Python subprocess调用系统iptables命令
- **权限管理**: sudo权限控制

### 4.2 系统架构图

```
┌─────────────────────────────────────────┐
│           Web Browser (Client)          │
│   ┌─────────────────────────────────┐   │
│   │     Bootstrap + DataTables      │   │
│   │     HTML/CSS/JavaScript         │   │
│   └─────────────────────────────────┘   │
└──────────────┬──────────────────────────┘
               │ HTTP/HTTPS
               ↓
┌─────────────────────────────────────────┐
│         Flask Web Server               │
│  ┌─────────────┬──────────────────┐    │
│  │  API Routes │  Template Engine  │    │
│  └─────────────┴──────────────────┘    │
└──────────────┬──────────────────────────┘
               │
    ┌──────────┼──────────┐
    ↓          ↓          ↓
┌────────┐ ┌────────┐ ┌────────┐
│ iptables│ │SQLite  │ │ System │
│Manager │ │Database│ │ Info   │
└────────┘ └────────┘ └────────┘
```

### 4.3 目录结构

```
iptables-web/
├── app.py                    # Flask应用主文件
├── config.py                 # 配置文件
├── requirements.txt          # Python依赖
├── database.py               # 数据库操作
├── iptables_manager.py       # iptables操作封装
├── models.py                 # 数据模型
├── routes/                   # 路由模块
│   ├── __init__.py
│   ├── rules.py              # 规则管理路由
│   ├── history.py            # 历史记录路由
│   ├── templates.py          # 规则模板路由
│   └── system.py             # 系统信息路由
├── templates/                # HTML模板
│   ├── base.html             # 基础模板
│   ├── index.html            # 首页/仪表盘
│   ├── rules.html            # 规则列表页
│   ├── rule_add.html         # 添加规则页
│   ├── rule_edit.html        # 编辑规则页
│   ├── history.html          # 历史记录页
│   ├── templates.html        # 规则模板页
│   └── import_export.html    # 导入导出页
├── static/                   # 静态资源
│   ├── css/
│   │   └── custom.css        # 自定义样式
│   └── js/
│       ├── app.js            # 主应用逻辑
│       ├── rules.js          # 规则管理JS
│       └── datatables-config.js
├── logs/                     # 日志目录
│   └── iptables-web.log
└── backups/                  # 规则备份目录
```

---

## 5. 界面设计

### 5.1 整体布局

**导航栏**:
- Logo/项目名称
- 菜单项：规则管理、历史记录、规则模板、导入导出、系统状态
- 右侧：刷新按钮、帮助文档入口

**主内容区**:
- 页面标题
- 功能操作区（工具栏）
- 内容区域（表格、表单等）
- 提示信息区

**底部**:
- 版本信息
- 系统运行状态

### 5.2 页面设计

#### 5.2.1 首页/仪表盘
- 系统状态概览卡片
- 规则统计（总数、各表规则数）
- 最近操作记录（最近5条）
- 快速操作按钮

#### 5.2.2 规则管理页面
- 筛选工具栏（表、链、搜索框）
- 规则表格（DataTables）
- 批量操作工具栏
- 分页控制

#### 5.2.3 添加/编辑规则页面
- 表单布局
- 字段分组（基本参数、高级参数）
- 实时预览生成的iptables命令
- 表单验证和错误提示

#### 5.2.4 历史记录页面
- 时间筛选器
- 操作类型筛选
- 历史记录表格
- 回滚操作按钮

### 5.3 配色方案
- 主色调：蓝色（#007bff）- 专业、可信
- 成功：绿色（#28a745）
- 警告：橙色（#ffc107）
- 危险：红色（#dc3545）
- 信息：深蓝色（#17a2b8）
- 背景色：浅灰色（#f8f9fa）
- 文字色：深灰色（#343a40）

---

## 6. API接口设计

### 6.1 规则管理API

**获取规则列表**
```
GET /api/rules
参数: table, chain, search, page, per_page
响应: {rules: [...], total: int, page: int}
```

**获取单条规则**
```
GET /api/rules/<id>
响应: {rule: {...}}
```

**添加规则**
```
POST /api/rules
请求体: {table, chain, protocol, source, destination, ...}
响应: {success: bool, message: string, rule_id: int}
```

**更新规则**
```
PUT /api/rules/<id>
请求体: {table, chain, protocol, ...}
响应: {success: bool, message: string}
```

**删除规则**
```
DELETE /api/rules/<id>
响应: {success: bool, message: string}
```

**批量删除规则**
```
POST /api/rules/batch-delete
请求体: {rule_ids: [1, 2, 3]}
响应: {success: bool, message: string, deleted_count: int}
```

### 6.2 历史记录API

**获取历史记录**
```
GET /api/history
参数: page, per_page, start_date, end_date, action_type
响应: {history: [...], total: int}
```

**回滚到指定版本**
```
POST /api/history/<id>/rollback
响应: {success: bool, message: string}
```

**导出历史记录**
```
GET /api/history/export
参数: format (json/csv), start_date, end_date
响应: 文件下载
```

### 6.3 规则模板API

**获取模板列表**
```
GET /api/templates
响应: {templates: [...]}
```

**应用模板**
```
POST /api/templates/<id>/apply
响应: {success: bool, message: string}
```

**创建模板**
```
POST /api/templates
请求体: {name, description, rule_config}
响应: {success: bool, template_id: int}
```

### 6.4 系统API

**获取系统信息**
```
GET /api/system/info
响应: {hostname, os_version, kernel_version, iptables_version, status}
```

**获取统计数据**
```
GET /api/system/stats
响应: {total_rules, table_stats: {filter: 10, nat: 5, ...}}
```

**健康检查**
```
GET /api/health
响应: {status: "ok", timestamp: "..."}
```

### 6.5 导入导出API

**导出规则**
```
GET /api/export
参数: format (iptables/json/csv), table
响应: 文件下载
```

**导入规则**
```
POST /api/import
请求体: 文件或JSON数据
响应: {success: bool, message: string, imported_count: int}
```

**预览导入**
```
POST /api/import/preview
响应: {preview: [...], conflicts: [...]}
```

---

## 7. 数据库设计

### 7.1 数据库概览
- **数据库类型**: SQLite
- **数据库文件**: iptables_web.db
- **存储内容**: 历史记录、规则模板、系统配置

### 7.2 数据表设计

**表: rule_history**（规则变更历史）
```sql
CREATE TABLE rule_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    action_type VARCHAR(20) NOT NULL,      -- 'add', 'update', 'delete'
    table_name VARCHAR(20) NOT NULL,        -- 'filter', 'nat', etc.
    chain_name VARCHAR(20) NOT NULL,        -- 'INPUT', 'OUTPUT', etc.
    rule_content TEXT NOT NULL,             -- iptables命令或规则详情
    old_rule_content TEXT,                  -- 修改前的规则（用于回滚）
    rule_number INTEGER,                    -- 规则序号
    operator_ip VARCHAR(50),                -- 操作者IP
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    notes TEXT
);
```

**表: rule_templates**（规则模板）
```sql
CREATE TABLE rule_templates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    table_name VARCHAR(20) NOT NULL,
    chain_name VARCHAR(20) NOT NULL,
    rule_config TEXT NOT NULL,              -- JSON格式的规则配置
    category VARCHAR(50),                  -- 模板分类
    is_builtin BOOLEAN DEFAULT 0,          -- 是否内置模板
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**表: system_config**（系统配置）
```sql
CREATE TABLE system_config (
    key VARCHAR(50) PRIMARY KEY,
    value TEXT,
    description TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## 8. 安全性考虑

### 8.1 命令注入防护
- 所有用户输入必须经过严格验证
- 使用shlex模块进行命令转义
- 禁止使用字符串拼接构造iptables命令
- 白名单验证：协议、端口、动作等字段

### 8.2 权限控制
- Web服务以非root用户运行
- 通过sudo调用iptables命令
- 配置sudoers文件限制可用命令
- 操作日志记录所有sudo调用

### 8.3 操作安全
- 危险操作二次确认：
  - 清空所有规则
  - 删除默认策略
  - 删除整条链
- 操作前自动备份
- 超时机制防止会话挂起
- CSRF令牌保护（如果需要扩展）

### 8.4 日志审计
- 记录所有规则变更操作
- 记录操作时间、操作者、操作内容
- 日志轮转和归档
- 日志格式标准化

---

## 9. 部署方案

### 9.1 环境要求
- **操作系统**: Linux (CentOS 7+, Ubuntu 18.04+, Debian 10+)
- **Python版本**: 3.8+
- **系统依赖**:
  - iptables
  - iptables-save
  - iptables-restore
  - sudo

### 9.2 安装步骤
1. 克隆代码仓库
2. 安装Python依赖：`pip install -r requirements.txt`
3. 初始化数据库
4. 配置sudo权限
5. 启动服务：`python app.py`
6. 配置系统服务（可选）：systemd

### 9.3 配置说明
**环境变量配置**:
- `IPTABLES_WEB_HOST`: 监听地址（默认：0.0.0.0）
- `IPTABLES_WEB_PORT`: 监听端口（默认：5000）
- `IPTABLES_WEB_DEBUG`: 调试模式（默认：False）
- `IPTABLES_WEB_LOG_LEVEL`: 日志级别（默认：INFO）

**配置文件**:
```python
# config.py
class Config:
    HOST = os.getenv('IPTABLES_WEB_HOST', '0.0.0.0')
    PORT = int(os.getenv('IPTABLES_WEB_PORT', 5000))
    DEBUG = os.getenv('IPTABLES_WEB_DEBUG', 'False').lower() == 'true'
    DATABASE = 'iptables_web.db'
    BACKUP_DIR = 'backups'
    LOG_FILE = 'logs/iptables-web.log'
    HISTORY_RETENTION_DAYS = 30
```

### 9.4 启动脚本
```bash
#!/bin/bash
# start.sh
export IPTABLES_WEB_HOST=0.0.0.0
export IPTABLES_WEB_PORT=5000
python app.py
```

### 9.5 systemd服务配置
```ini
[Unit]
Description=iptables Web Management Service
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/path/to/iptables-web
ExecStart=/usr/bin/python3 app.py
Restart=always

[Install]
WantedBy=multi-user.target
```

---

## 10. 使用流程

### 10.1 日常使用流程

**查看规则**:
1. 访问Web界面
2. 在规则管理页面查看所有规则
3. 使用筛选器查找特定规则

**添加规则**:
1. 点击"添加规则"按钮
2. 选择目标表和链
3. 配置规则条件
4. 预览生成的iptables命令
5. 确认添加

**修改规则**:
1. 在规则列表中点击"编辑"按钮
2. 修改规则参数
3. 预览变更
4. 确认修改

**回滚操作**:
1. 进入历史记录页面
2. 查找需要回滚的操作
3. 点击"回滚"按钮
4. 确认回滚

### 10.2 应急处理

**规则冲突或网络中断**:
1. 使用控制台直接访问服务器
2. 检查iptables状态：`sudo iptables -L -n`
3. 备份当前规则：`sudo iptables-save > backup.txt`
4. 恢复到备份：`sudo iptables-restore < backup.txt`
5. 检查Web服务日志

**服务无法启动**:
1. 检查端口占用：`netstat -tulpn | grep 5000`
2. 检查日志文件：`tail -f logs/iptables-web.log`
3. 验证数据库权限
4. 检查Python依赖安装

---

## 11. 验收标准

### 11.1 功能验收
- [ ] 能够查看所有iptables规则
- [ ] 能够添加新规则并立即生效
- [ ] 能够编辑现有规则
- [ ] 能够删除单条或多条规则
- [ ] 能够查看规则变更历史
- [ ] 能够回滚到历史版本
- [ ] 能够使用规则模板
- [ ] 能够导入导出规则
- [ ] 能够显示系统状态信息

### 11.2 性能验收
- [ ] 规则列表加载时间 < 2秒（规则数<1000）
- [ ] 规则操作响应时间 < 1秒
- [ ] 无内存泄漏
- [ ] 无连接泄漏

### 11.3 安全验收
- [ ] 无命令注入漏洞
- [ ] 所有操作有日志记录
- [ ] 危险操作有确认机制
- [ ] 配置安全（权限、端口等）

### 11.4 可用性验收
- [ ] 支持主流浏览器
- [ ] 响应式布局正常
- [ ] 错误提示清晰
- [ ] 帮助文档完整

---

## 12. 项目计划

### 阶段一：需求确认（本阶段）
- 生成需求文档
- 与用户确认需求
- 确定技术方案

### 阶段二：后端开发（预计1-2天）
- 项目结构搭建
- 数据库设计实现
- iptables操作封装
- API接口开发
- 单元测试

### 阶段三：前端开发（预计1-2天）
- HTML页面设计
- CSS样式编写
- JavaScript交互实现
- 响应式布局适配

### 阶段四：系统集成（预计0.5天）
- 后端与前端联调
- 系统集成测试
- 安全加固

### 阶段五：部署上线（预计0.5天）
- 生产环境部署
- 配置优化
- 监控告警配置
- 文档编写

---

## 13. 风险评估

### 13.1 高风险
- **风险**: 误操作导致服务器网络中断
- **缓解措施**:
  - 提供控制台急救指南
  - 危险操作二次确认
  - 操作前自动备份
  - 保留回滚能力

### 13.2 中风险
- **风险**: iptables命令执行失败
- **缓解措施**:
  - 命令执行前验证
  - 详细的错误信息反馈
  - 失败自动回滚

### 13.3 低风险
- **风险**: Web服务性能瓶颈
- **缓解措施**:
  - 规则列表分页
  - 异步操作
  - 缓存优化

---

## 14. 附录

### 14.1 术语表
- **Table**: iptables的表，用于区分不同功能的规则集合
- **Chain**: iptables的链，用于组织规则序列
- **Rule**: 具体的过滤规则，定义匹配条件和动作
- **Target**: 规则匹配后执行的动作（ACCEPT、DROP等）
- **Policy**: 链的默认策略，当链中没有规则匹配时执行

### 14.2 常用iptables命令参考
```bash
# 查看规则
iptables -L -n -v --line-numbers
iptables -t nat -L -n -v

# 添加规则
iptables -A INPUT -p tcp --dport 22 -j ACCEPT

# 删除规则
iptables -D INPUT 1

# 清空规则
iptables -F

# 保存规则
iptables-save > /etc/sysconfig/iptables

# 恢复规则
iptables-restore < /etc/sysconfig/iptables
```

### 14.3 参考资料
- iptables官方文档：https://www.netfilter.org/documentation/
- Flask框架文档：https://flask.palletsprojects.com/
- Bootstrap文档：https://getbootstrap.com/

---

**文档版本**: 1.0
**创建日期**: 2026-06-01
**文档状态**: 待确认
