import os

class Config:
    HOST = os.getenv('IPTABLES_WEB_HOST', '0.0.0.0')
    PORT = int(os.getenv('IPTABLES_WEB_PORT', 5000))
    DEBUG = os.getenv('IPTABLES_WEB_DEBUG', 'False').lower() == 'true'
    DATABASE = os.getenv('IPTABLES_WEB_DATABASE', 'iptables_web.db')
    BACKUP_DIR = os.getenv('IPTABLES_WEB_BACKUP_DIR', 'backups')
    LOG_FILE = os.getenv('IPTABLES_WEB_LOG_FILE', 'logs/iptables-web.log')
    HISTORY_RETENTION_DAYS = int(os.getenv('IPTABLES_WEB_HISTORY_RETENTION', '30'))
    
    @staticmethod
    def init_app(app):
        os.makedirs(Config.BACKUP_DIR, exist_ok=True)
        os.makedirs('logs', exist_ok=True)