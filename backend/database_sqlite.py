import sqlite3
import hashlib
import os
from datetime import datetime

class DatabaseManager:
    def __init__(self):
        # Usar diretório persistente no Render
        db_dir = os.environ.get('RENDER_SERVICE_ID', '/tmp')
        self.db_path = os.path.join('/opt/render/project/src', 'users.db')
        self.init_database()
    
    def init_database(self):
        """Inicializa o banco de dados SQLite e cria tabelas"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Criar tabela de usuários
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
            conn.close()
            print(f"✅ Banco SQLite inicializado: {self.db_path}")
            
        except Exception as e:
            print(f"❌ Erro ao inicializar banco SQLite: {e}")
    
    def hash_password(self, password):
        """Gera hash seguro da senha"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def create_user(self, name, email, password):
        """Cria um novo usuário"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Verificar se email já existe
            cursor.execute('SELECT id FROM users WHERE email = ?', (email,))
            if cursor.fetchone():
                conn.close()
                return {'success': False, 'message': 'Email já cadastrado'}
            
            # Criar usuário
            password_hash = self.hash_password(password)
            cursor.execute('''
                INSERT INTO users (name, email, password_hash)
                VALUES (?, ?, ?)
            ''', (name, email, password_hash))
            
            user_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            print(f"✅ Usuário criado: {email} (ID: {user_id})")
            return {'success': True, 'message': 'Usuário criado com sucesso', 'user_id': user_id}
            
        except Exception as e:
            print(f"❌ Erro ao criar usuário: {e}")
            return {'success': False, 'message': 'Erro interno do servidor'}
    
    def authenticate_user(self, email, password):
        """Autentica usuário"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            password_hash = self.hash_password(password)
            cursor.execute('''
                SELECT id, name, email FROM users 
                WHERE email = ? AND password_hash = ?
            ''', (email, password_hash))
            
            user = cursor.fetchone()
            conn.close()
            
            if user:
                print(f"✅ Login bem-sucedido: {email}")
                return {
                    'success': True, 
                    'user': {
                        'id': user[0],
                        'name': user[1],
                        'email': user[2]
                    }
                }
            else:
                print(f"❌ Login falhou: {email}")
                return {'success': False, 'message': 'Email ou senha incorretos'}
                
        except Exception as e:
            print(f"❌ Erro na autenticação: {e}")
            return {'success': False, 'message': 'Erro interno do servidor'}
    
    def get_user_count(self):
        """Retorna número total de usuários"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM users')
            count = cursor.fetchone()[0]
            conn.close()
            return count
        except Exception as e:
            print(f"❌ Erro ao contar usuários: {e}")
            return 0

