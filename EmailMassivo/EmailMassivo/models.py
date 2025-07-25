from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relacionamento com assinatura
    subscription = db.relationship('Subscription', backref='user', uselist=False)
    
    def set_password(self, password):
        """Define hash da senha"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Verifica se a senha está correta"""
        return check_password_hash(self.password_hash, password)
    
    def has_active_subscription(self):
        """Verifica se o usuário tem uma assinatura ativa"""
        if not self.subscription:
            return False
        
        if self.subscription.status != 'ativo':
            return False
            
        # Se é vitalício, sempre ativo
        if self.subscription.plano == 'vitalicio' or self.subscription.plano == 'vip':
            return True
            
        # Verifica se não expirou
        if self.subscription.data_expiracao and self.subscription.data_expiracao < datetime.utcnow():
            return False
            
        return True
    
    def get_subscription_info(self):
        """Retorna informações da assinatura"""
        if not self.subscription:
            return {'plano': 'Nenhum', 'status': 'Inativo', 'expira_em': None}
        
        return {
            'plano': self.subscription.plano.title(),
            'status': self.subscription.status.title(),
            'expira_em': self.subscription.data_expiracao
        }
    
    def __repr__(self):
        return f'<User {self.username}>'

class Subscription(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    plano = db.Column(db.String(20), nullable=False)  # mensal, trimestral, vitalicio, vip, gratuito, pendente
    status = db.Column(db.String(20), nullable=False, default='pendente')  # pendente, ativo, expirado
    data_inicio = db.Column(db.DateTime)
    data_expiracao = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Para controle de pagamentos
    mercadopago_id = db.Column(db.String(100))
    valor_pago = db.Column(db.Float)
    
    def activate_plan(self, plano_tipo):
        """Ativa um plano específico"""
        self.plano = plano_tipo
        self.status = 'ativo'
        self.data_inicio = datetime.utcnow()
        
        # Define data de expiração baseada no plano
        if plano_tipo == 'mensal':
            self.data_expiracao = datetime.utcnow() + timedelta(days=30)
        elif plano_tipo == 'trimestral':
            self.data_expiracao = datetime.utcnow() + timedelta(days=90)
        elif plano_tipo in ['vitalicio', 'vip']:
            self.data_expiracao = None  # Nunca expira
            
        self.updated_at = datetime.utcnow()
    
    def is_expired(self):
        """Verifica se a assinatura expirou"""
        if self.plano in ['vitalicio', 'vip']:
            return False
        
        if self.data_expiracao and self.data_expiracao < datetime.utcnow():
            return True
            
        return False
    
    def days_remaining(self):
        """Retorna quantos dias restam na assinatura"""
        if self.plano in ['vitalicio', 'vip']:
            return float('inf')
        
        if not self.data_expiracao:
            return 0
            
        remaining = self.data_expiracao - datetime.utcnow()
        return max(0, remaining.days)
    
    def __repr__(self):
        return f'<Subscription {self.plano} - {self.status}>'