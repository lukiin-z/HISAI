"""
Arquivo de configuração do banco de dados
Gerencia usuários, sessões e histórico de uploads
"""

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

# Inicializa o SQLAlchemy (será configurado no app.py)
db = SQLAlchemy()

# ========== MODELO DE USUÁRIO ==========
class User(UserMixin, db.Model):
    """
    Modelo de usuário para o sistema
    UserMixin adiciona métodos necessários para Flask-Login
    """
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime, nullable=True)
    
    # Relacionamento: um usuário pode ter vários uploads
    uploads = db.relationship('UploadHistory', backref='user', lazy=True)
    
    def set_password(self, password):
        """Define a senha do usuário (criptografada)"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Verifica se a senha está correta"""
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'

# ========== MODELO DE HISTÓRICO DE UPLOADS ==========
class UploadHistory(db.Model):
    """
    Armazena histórico de planilhas processadas
    """
    __tablename__ = 'upload_history'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Estatísticas do processamento
    total_empresas = db.Column(db.Integer, default=0)
    empresas_encontradas = db.Column(db.Integer, default=0)
    empresas_nao_encontradas = db.Column(db.Integer, default=0)
    
    # Custo estimado da API (em dólares)
    api_cost = db.Column(db.Float, default=0.0)
    
    def __repr__(self):
        return f'<Upload {self.filename} por User {self.user_id}>'

# ========== FUNÇÕES AUXILIARES ==========

def init_db(app):
    """
    Inicializa o banco de dados e cria as tabelas
    """
    db.init_app(app)
    with app.app_context():
        db.create_all()
        
        # Cria usuário admin padrão se não existir
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(
                username='admin',
                email='admin@hislogistica.com.br',
                is_admin=True
            )
            admin.set_password('admin123')  # MUDE ESSA SENHA DEPOIS!
            db.session.add(admin)
            db.session.commit()
            print("✅ Usuário admin criado! Login: admin | Senha: admin123")
        
        print("✅ Banco de dados inicializado!")

def get_user_count():
    """
    Retorna o número total de usuários ativos (não admin)
    """
    return User.query.filter_by(is_active=True, is_admin=False).count()

def can_add_user():
    """
    Verifica se pode adicionar mais usuários (limite de 10)
    """
    return get_user_count() < 10

def get_all_uploads():
    """
    Retorna todos os uploads ordenados por data
    """
    return UploadHistory.query.order_by(UploadHistory.upload_date.desc()).all()

def get_user_uploads(user_id):
    """
    Retorna uploads de um usuário específico
    """
    return UploadHistory.query.filter_by(user_id=user_id).order_by(
        UploadHistory.upload_date.desc()
    ).all()

def get_total_api_cost():
    """
    Calcula o custo total gasto com a API
    """
    total = db.session.query(db.func.sum(UploadHistory.api_cost)).scalar()
    return total or 0.0

def get_total_empresas_processadas():
    """
    Retorna o total de empresas processadas no sistema
    """
    total = db.session.query(db.func.sum(UploadHistory.total_empresas)).scalar()
    return total or 0