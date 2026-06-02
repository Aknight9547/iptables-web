# iptables-web 用户手册

## 版本信息
**版本**: 1.0.11  
**更新日期**: 2026年6月  
**作者**: iptables-web 开发团队

---

## 目录
1. 项目概述
2. 功能特性
3. 安装部署
4. 使用说明
5. API接口
6. 项目结构
7. 配置说明
8. 常见问题

---

## 1. 项目概述

iptables-web 是一个基于 Flask 的 iptables Web 管理服务，提供可视化的规则管理界面，支持规则的查看、添加、编辑、删除和回滚操作。

### 主要特点
- 基于 Web 的可视化管理界面
- 支持多种 iptables 表（filter、nat、mangle、raw）
- 支持 DNAT/SNAT 端口转发规则
- 完整的操作历史记录和回滚功能
- 预置常用规则模板
- 支持规则导入导出
- 离线打包和一键部署

---

## 2. 功能特性

| 功能模块 | 描述 |
|----------|------|
| 规则管理 | 查看、添加、编辑、删除 iptables 规则 |
| 多表支持 | 支持 filter、nat、mangle、raw 表 |
| DNAT/SNAT | 支持端口转发规则配置 |
| 历史记录 | 记录所有操作，支持回滚 |
| 规则模板 | 预置常用规则模板 |
| 导入导出 | 支持多种格式规则导入导出 |
| 离线部署 | 支持离线打包和一键部署 |
| 系统监控 | 查看系统状态和统计信息 |

---

## 3. 安装部署

### 3.1 环境要求
- Linux 操作系统（推荐 Ubuntu 20.04+）
- Python 3.8 或更高版本
- iptables 工具
- sudo 权限

### 3.2 一键部署

```bash
# 解压安装包
tar -xzf iptables-web-1.0.11.tar.gz
cd iptables-web-1.0.11

# 执行安装（指定端口和目录）
./deploy.sh -i -p 5000 -d /opt/iptables-web
```

### 3.3 服务管理命令

```bash
# 启动服务
./deploy.sh -s

# 停止服务
./deploy.sh -k

# 重启服务
./deploy.sh -r

# 卸载服务
./deploy.sh -u

# 查看帮助
./deploy.sh -h
```

### 3.4 开发模式运行

```bash
# 安装依赖
pip install -r requirements.txt

# 启动服务
python3 app.py
```

---

## 4. 使用说明

### 4.1 访问服务

打开浏览器访问: `http://<服务器IP>:5000`

### 4.2 添加规则

1. 点击左侧菜单"规则管理"
2. 点击"添加规则"按钮
3. 填写规则参数：
   - **表**: filter / nat / mangle / raw
   - **链**: INPUT / OUTPUT / FORWARD / PREROUTING / POSTROUTING
   - **协议**: TCP / UDP / ICMP
   - **源地址/目标地址**: IP地址或网段（如 192.168.1.0/24）
   - **端口**: 源端口/目标端口
   - **动作**: ACCEPT / DROP / REJECT / DNAT / SNAT 等
4. 点击"确认添加"

### 4.3 DNAT 规则示例

**需求**: 将访问 10.103.1.220:8081 的流量转发到 10.104.1.116:22

**命令行方式**:
```bash
iptables -t nat -A PREROUTING -s 172.16.254.233 -d 10.103.1.220 -p tcp --dport 8081 -j DNAT --to-destination 10.104.1.116:22
```

**Web界面填写**:
| 字段 | 值 |
|------|-----|
| 表 | nat |
| 链 | PREROUTING |
| 协议 | TCP |
| 源地址 | 172.16.254.233 |
| 目标地址 | 10.103.1.220 |
| 目标端口 | 8081 |
| 动作 | DNAT |
| DNAT目标地址 | 10.104.1.116:22 |

### 4.4 编辑规则

1. 在规则列表中找到要编辑的规则
2. 点击"编辑"按钮
3. 修改规则参数
4. 点击"保存修改"

### 4.5 删除规则

1. 在规则列表中找到要删除的规则
2. 点击"删除"按钮
3. 在确认对话框中点击"确认"

### 4.6 历史记录与回滚

1. 点击左侧菜单"历史记录"
2. 选择要回滚的操作记录
3. 点击"回滚"按钮
4. 在确认对话框中点击"确认"

### 4.7 规则模板

1. 点击左侧菜单"规则模板"
2. 选择一个模板
3. 点击"应用模板"
4. 修改参数后点击"确认添加"

### 4.8 导入导出

1. 点击左侧菜单"导入导出"
2. **导出规则**: 选择导出格式，点击"导出"
3. **导入规则**: 选择文件，点击"导入"

---

## 5. API 接口

### 5.1 规则管理

| 接口 | 方法 | 描述 |
|------|------|------|
| `/api/rules` | GET | 获取规则列表 |
| `/api/rules` | POST | 添加规则 |
| `/api/rules/<table>/<chain>/<int:rule_number>` | PUT | 更新规则 |
| `/api/rules/<table>/<chain>/<int:rule_number>` | DELETE | 删除规则 |

### 5.2 历史记录

| 接口 | 方法 | 描述 |
|------|------|------|
| `/api/history` | GET | 获取历史记录 |
| `/api/history/<int:history_id>/rollback` | POST | 回滚操作 |

### 5.3 规则模板

| 接口 | 方法 | 描述 |
|------|------|------|
| `/api/templates` | GET | 获取模板列表 |
| `/api/templates/<int:template_id>/apply` | POST | 应用模板 |

### 5.4 系统信息

| 接口 | 方法 | 描述 |
|------|------|------|
| `/api/system/info` | GET | 获取系统信息 |
| `/api/system/stats` | GET | 获取系统统计 |
| `/api/health` | GET | 健康检查 |

### 5.5 导入导出

| 接口 | 方法 | 描述 |
|------|------|------|
| `/api/export` | GET | 导出规则 |
| `/api/import` | POST | 导入规则 |

---

## 6. 项目结构

```
iptables-web/
├── app.py                 # Flask应用主文件
├── config.py              # 配置文件
├── requirements.txt       # Python依赖列表
├── iptables_manager.py    # iptables操作封装
├── models.py              # 数据库模型
├── build.py               # 打包脚本
├── deploy.sh              # 一键部署脚本
├── routes/                # API路由模块
│   ├── rules.py           # 规则管理API
│   ├── history.py         # 历史记录API
│   ├── templates.py       # 规则模板API
│   ├── system.py          # 系统信息API
│   ├── import_export.py   # 导入导出API
│   └── __init__.py
├── templates/             # HTML模板
│   └── index.html         # 主页面
├── static/                # 静态资源
│   ├── css/               # 样式文件
│   └── js/                # JavaScript文件
└── dist/                  # 打包输出目录
    └── iptables-web-1.0.11.tar.gz
```

---

## 7. 配置说明

### 7.1 环境变量配置

| 环境变量 | 默认值 | 描述 |
|----------|--------|------|
| `IPTABLES_WEB_HOST` | 0.0.0.0 | 服务监听地址 |
| `IPTABLES_WEB_PORT` | 5000 | 服务监听端口 |
| `IPTABLES_WEB_DEBUG` | false | 调试模式开关 |

### 7.2 配置文件

配置文件位于 `config.py`，包含以下主要配置项：

```python
class Config:
    HOST = '0.0.0.0'
    PORT = 5000
    DEBUG = False
    DATABASE_PATH = 'iptables_web.db'
    BACKUP_DIR = 'backups'
    LOG_DIR = 'logs'
```

---

## 8. 常见问题

### 8.1 服务启动失败

**问题现象**: 服务无法启动，查看日志显示错误

**解决方案**:
1. 检查端口是否被占用：`netstat -tlnp | grep 5000`
2. 确保运行用户有 sudo 权限
3. 查看系统日志：`journalctl -u iptables-web`

### 8.2 添加规则报错

**问题现象**: 点击"确认添加"后显示错误

**解决方案**:
1. 检查是否填写了必填字段
2. DNAT/SNAT 规则需要填写目标地址
3. 检查协议和端口是否匹配

### 8.3 规则不生效

**问题现象**: 添加规则后没有生效

**解决方案**:
1. 检查 iptables 服务状态：`systemctl status iptables`
2. 确保规则添加到正确的表和链
3. 检查规则顺序是否正确

### 8.4 回滚失败

**问题现象**: 点击回滚后显示错误

**解决方案**:
1. 检查历史记录中的规则配置是否完整
2. 确认要回滚的规则是否仍然存在
3. 检查 iptables 命令执行权限

### 8.5 无法访问 Web 界面

**问题现象**: 浏览器无法访问服务

**解决方案**:
1. 检查防火墙规则是否允许访问端口
2. 确认服务正在运行：`systemctl status iptables-web`
3. 检查网络连接是否正常

---

## 附录

### A. 常用 iptables 命令

```bash
# 查看所有规则
iptables -L -n

# 查看 nat 表规则
iptables -t nat -L -n

# 查看规则编号
iptables -L -n --line-numbers

# 保存规则
iptables-save > /etc/iptables/rules.v4

# 恢复规则
iptables-restore < /etc/iptables/rules.v4
```

### B. 端口转发示例

**DNAT（目标地址转换）**:
```bash
iptables -t nat -A PREROUTING -d 公网IP -p tcp --dport 80 -j DNAT --to-destination 内网IP:80
```

**SNAT（源地址转换）**:
```bash
iptables -t nat -A POSTROUTING -s 内网网段 -j SNAT --to-source 公网IP
```

**MASQUERADE（动态SNAT）**:
```bash
iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
```

---

**文档版本**: v1.0.11  
**文档日期**: 2026年6月