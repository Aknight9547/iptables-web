#!/bin/bash

IPTABLES_WEB_DIR="/opt/iptables-web"
IPTABLES_WEB_PORT=5000
IPTABLES_WEB_USER="www-data"
PACKAGE_FILE=""
SOURCE_DIR=""

show_help() {
    echo "iptables-web 一键部署脚本"
    echo "用法: $0 [选项]"
    echo ""
    echo "选项:"
    echo "  -h, --help          显示帮助信息"
    echo "  -i, --install       执行安装部署"
    echo "  -u, --uninstall     执行卸载"
    echo "  -s, --start         启动服务"
    echo "  -k, --stop          停止服务"
    echo "  -r, --restart       重启服务"
    echo "  -p, --port          指定服务端口（默认5000）"
    echo "  -d, --dir           指定安装目录（默认/opt/iptables-web）"
    echo "  -f, --file          指定安装包路径（自动查找当前目录下的tar.gz）"
    echo "  -s, --source        指定源码目录（跳过解压，直接复制）"
}

check_root() {
    if [ "$(id -u)" != "0" ]; then
        echo "错误: 请以root用户执行此脚本"
        exit 1
    fi
}

check_python() {
    if ! command -v python3 &> /dev/null; then
        echo "错误: 未找到Python3，请先安装Python3.8+"
        exit 1
    fi
    
    PYTHON_VERSION=$(python3 --version | awk '{print $2}' | cut -d. -f1,2)
    REQUIRED_VERSION="3.8"
    
    if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
        echo "错误: Python版本需要3.8+，当前版本: $PYTHON_VERSION"
        exit 1
    fi
}

check_iptables() {
    if ! command -v iptables &> /dev/null; then
        echo "错误: 未找到iptables，请先安装iptables"
        exit 1
    fi
}

check_systemd() {
    if ! command -v systemctl &> /dev/null; then
        echo "警告: 系统不支持systemd，服务管理功能受限"
        return 1
    fi
    return 0
}

check_port() {
    if lsof -Pi :$IPTABLES_WEB_PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo "错误: 端口 $IPTABLES_WEB_PORT 已被占用"
        exit 1
    fi
}

detect_source_dir() {
    if [ -n "$SOURCE_DIR" ]; then
        if [ -d "$SOURCE_DIR" ] && [ -f "$SOURCE_DIR/app.py" ]; then
            echo "使用指定的源码目录: $SOURCE_DIR"
            return 0
        else
            echo "错误: 指定的源码目录不存在或不完整: $SOURCE_DIR"
            exit 1
        fi
    fi
    
    if [ -f "app.py" ] && [ -f "requirements.txt" ] && [ -d "templates" ]; then
        SOURCE_DIR=$(pwd)
        echo "检测到当前目录已是源码目录，直接使用"
        return 0
    fi
    
    return 1
}

find_package() {
    if [ -n "$PACKAGE_FILE" ]; then
        if [ -f "$PACKAGE_FILE" ]; then
            return 0
        else
            echo "错误: 指定的安装包不存在: $PACKAGE_FILE"
            exit 1
        fi
    fi
    
    local packages=($(ls iptables-web*.tar.gz 2>/dev/null))
    if [ ${#packages[@]} -eq 0 ]; then
        packages=($(ls *.tar.gz 2>/dev/null))
    fi
    
    if [ ${#packages[@]} -eq 0 ]; then
        return 1
    elif [ ${#packages[@]} -gt 1 ]; then
        echo "发现多个安装包，使用第一个: ${packages[0]}"
    fi
    
    PACKAGE_FILE="${packages[0]}"
    echo "找到安装包: $PACKAGE_FILE"
    return 0
}

install_system_deps() {
    echo "安装系统依赖..."
    
    if command -v apt-get &> /dev/null; then
        apt-get update
        apt-get install -y python3 python3-venv iptables sudo tar gzip curl
    elif command -v yum &> /dev/null; then
        yum install -y python3 python3-venv iptables sudo tar gzip curl
    elif command -v dnf &> /dev/null; then
        dnf install -y python3 python3-venv iptables sudo tar gzip curl
    else
        echo "警告: 无法自动安装依赖，请手动安装"
    fi
    
    echo "系统依赖安装完成"
}

create_user() {
    if ! id "$IPTABLES_WEB_USER" &>/dev/null; then
        echo "创建用户 $IPTABLES_WEB_USER..."
        useradd -r -s /sbin/nologin "$IPTABLES_WEB_USER"
    fi
}

configure_sudo() {
    echo "配置sudo权限..."
    
    SUDOERS_FILE="/etc/sudoers.d/iptables-web"
    
    cat > "$SUDOERS_FILE" << EOF
$IPTABLES_WEB_USER ALL=(ALL) NOPASSWD: /sbin/iptables
$IPTABLES_WEB_USER ALL=(ALL) NOPASSWD: /sbin/iptables-save
$IPTABLES_WEB_USER ALL=(ALL) NOPASSWD: /sbin/iptables-restore
EOF
    
    chmod 0440 "$SUDOERS_FILE"
    echo "sudo权限配置完成"
}

create_venv() {
    echo "创建Python虚拟环境..."
    python3 -m venv "$IPTABLES_WEB_DIR/venv"
    echo "虚拟环境创建完成"
}

install_python_deps() {
    echo "安装Python依赖..."
    
    VENV_PIP="$IPTABLES_WEB_DIR/venv/bin/pip"
    
    if [ ! -f "$IPTABLES_WEB_DIR/requirements.txt" ]; then
        echo "错误: 未找到 requirements.txt"
        echo "请检查安装包是否正确解压"
        exit 1
    fi
    
    if [ -d "$IPTABLES_WEB_DIR/deps" ] && [ "$(ls -A "$IPTABLES_WEB_DIR/deps")" ]; then
        echo "从本地依赖安装..."
        "$VENV_PIP" install --no-index --find-links="$IPTABLES_WEB_DIR/deps" -r "$IPTABLES_WEB_DIR/requirements.txt"
    else
        echo "从PyPI安装..."
        "$VENV_PIP" install -r "$IPTABLES_WEB_DIR/requirements.txt"
    fi
    
    echo "Python依赖安装完成"
}

create_systemd_service() {
    echo "创建systemd服务..."
    
    SERVICE_FILE="/etc/systemd/system/iptables-web.service"
    cat > "$SERVICE_FILE" << EOF
[Unit]
Description=iptables Web Management Service
After=network.target

[Service]
Type=simple
User=$IPTABLES_WEB_USER
WorkingDirectory=$IPTABLES_WEB_DIR
ExecStart=$IPTABLES_WEB_DIR/venv/bin/python $IPTABLES_WEB_DIR/app.py
Restart=always
RestartSec=5
Environment="IPTABLES_WEB_HOST=0.0.0.0"
Environment="IPTABLES_WEB_PORT=$IPTABLES_WEB_PORT"
Environment="IPTABLES_WEB_BACKUP_DIR=$IPTABLES_WEB_DIR/backups"
Environment="IPTABLES_WEB_DATABASE=$IPTABLES_WEB_DIR/iptables_web.db"
Environment="IPTABLES_WEB_LOG_FILE=$IPTABLES_WEB_DIR/logs/iptables-web.log"

[Install]
WantedBy=multi-user.target
EOF
    
    systemctl daemon-reload
    systemctl enable iptables-web
    echo "systemd服务创建完成"
}

start_service() {
    echo "启动服务..."
    systemctl start iptables-web
    sleep 2
    
    if systemctl is-active --quiet iptables-web; then
        echo "服务启动成功"
        health_check
    else
        echo "服务启动失败"
        echo "查看日志: journalctl -u iptables-web"
        exit 1
    fi
}

health_check() {
    echo "执行健康检查..."
    
    for i in {1..5}; do
        if curl -s "http://localhost:$IPTABLES_WEB_PORT/api/health" | grep -q "ok"; then
            echo "健康检查通过"
            echo ""
            echo "部署完成！"
            echo "访问地址: http://$(hostname -I | awk '{print $1}'):$IPTABLES_WEB_PORT"
            return 0
        fi
        sleep 1
    done
    
    echo "警告: 健康检查未通过，请检查日志"
    echo "查看日志: journalctl -u iptables-web"
    return 1
}

copy_source_files() {
    echo "复制源码文件..."
    mkdir -p "$IPTABLES_WEB_DIR"
    
    local files=("app.py" "config.py" "requirements.txt" "iptables_manager.py" "models.py")
    local dirs=("routes" "templates" "static")
    
    for file in "${files[@]}"; do
        if [ -f "$SOURCE_DIR/$file" ]; then
            cp "$SOURCE_DIR/$file" "$IPTABLES_WEB_DIR/"
        else
            echo "警告: 缺少文件: $file"
        fi
    done
    
    for dir in "${dirs[@]}"; do
        if [ -d "$SOURCE_DIR/$dir" ]; then
            cp -r "$SOURCE_DIR/$dir" "$IPTABLES_WEB_DIR/"
        else
            echo "警告: 缺少目录: $dir"
        fi
    done
    
    mkdir -p "$IPTABLES_WEB_DIR/backups"
    mkdir -p "$IPTABLES_WEB_DIR/logs"
    chown -R "$IPTABLES_WEB_USER:$IPTABLES_WEB_USER" "$IPTABLES_WEB_DIR"
    echo "源码文件复制完成"
}

install() {
    echo "开始安装 iptables-web..."
    echo ""
    
    check_root
    check_python
    check_iptables
    check_systemd
    check_port
    
    echo "步骤1/7: 安装系统依赖..."
    install_system_deps
    
    echo ""
    echo "步骤2/7: 创建运行用户..."
    create_user
    
    echo ""
    echo "步骤3/7: 准备安装文件..."
    
    if detect_source_dir; then
        echo "步骤4/7: 复制源码文件..."
        copy_source_files
    elif find_package; then
        echo "步骤4/7: 解压安装包..."
        mkdir -p "$IPTABLES_WEB_DIR"
        if ! tar -xzf "$PACKAGE_FILE" --strip-components=1 -C "$IPTABLES_WEB_DIR"; then
            echo "错误: 解压安装包失败"
            exit 1
        fi
        echo "安装包解压完成"
    else
        echo "错误: 未找到安装包或源码目录"
        echo "请确保安装包(.tar.gz)在当前目录，或当前目录已是解压后的源码目录"
        echo "或使用 -f 参数指定安装包，或 -s 参数指定源码目录"
        exit 1
    fi
    
    echo ""
    echo "步骤5/7: 配置系统..."
    configure_sudo
    create_venv
    
    echo ""
    echo "步骤6/7: 安装Python依赖..."
    install_python_deps
    
    echo ""
    echo "步骤7/7: 创建服务并启动..."
    create_systemd_service
    start_service
    
    echo ""
    echo "安装完成！"
}

uninstall() {
    echo "开始卸载 iptables-web..."
    
    check_root
    
    echo "停止服务..."
    systemctl stop iptables-web 2>/dev/null
    
    echo "禁用服务..."
    systemctl disable iptables-web 2>/dev/null
    
    echo "删除服务文件..."
    rm -f "/etc/systemd/system/iptables-web.service"
    systemctl daemon-reload
    
    echo "删除sudo配置..."
    rm -f "/etc/sudoers.d/iptables-web"
    
    echo "删除安装目录..."
    rm -rf "$IPTABLES_WEB_DIR"
    
    echo "卸载完成！"
}

stop_service() {
    echo "停止服务..."
    if systemctl stop iptables-web; then
        echo "服务已停止"
    else
        echo "服务停止失败"
        exit 1
    fi
}

restart_service() {
    echo "重启服务..."
    if systemctl restart iptables-web; then
        echo "服务已重启"
        health_check
    else
        echo "服务重启失败"
        exit 1
    fi
}

while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            exit 0
            ;;
        -i|--install)
            install
            exit 0
            ;;
        -u|--uninstall)
            uninstall
            exit 0
            ;;
        -s|--start)
            start_service
            exit 0
            ;;
        -k|--stop)
            stop_service
            exit 0
            ;;
        -r|--restart)
            restart_service
            exit 0
            ;;
        -p|--port)
            IPTABLES_WEB_PORT="$2"
            shift
            ;;
        -d|--dir)
            IPTABLES_WEB_DIR="$2"
            shift
            ;;
        -f|--file)
            PACKAGE_FILE="$2"
            shift
            ;;
        --source)
            SOURCE_DIR="$2"
            shift
            ;;
        *)
            echo "未知选项: $1"
            show_help
            exit 1
            ;;
    esac
    shift
done

show_help
exit 1