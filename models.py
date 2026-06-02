from app import db
from datetime import datetime

class RuleHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    action_type = db.Column(db.String(20), nullable=False)
    table_name = db.Column(db.String(20), nullable=False)
    chain_name = db.Column(db.String(20), nullable=False)
    rule_content = db.Column(db.Text, nullable=False)
    old_rule_content = db.Column(db.Text)
    rule_number = db.Column(db.Integer)
    operator_ip = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.now)
    notes = db.Column(db.Text)

class RuleTemplate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    table_name = db.Column(db.String(20), nullable=False)
    chain_name = db.Column(db.String(20), nullable=False)
    rule_config = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50))
    is_builtin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now)

class SystemConfig(db.Model):
    key = db.Column(db.String(50), primary_key=True)
    value = db.Column(db.Text)
    description = db.Column(db.Text)
    updated_at = db.Column(db.DateTime, default=datetime.now)