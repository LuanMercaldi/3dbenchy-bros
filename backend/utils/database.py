import sqlite3
import psycopg
from psycopg.rows import dict_row
import hashlib
import secrets
import jwt
import os
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from urllib.parse import urlparse

class DatabaseManager:
    """Gerenciador de banco de dados SQLite com funcionalidades completas"""
    
    def __init__(self, db_path=None):
        """Inicializar gerenciador de banco de dados"""
        # Detectar tipo de banco baseado na URL
        database_url = os.environ.get('DATABASE_URL')
        
        if database_url:
            # PostgreSQL (produção no Render)
            if database_url.startswith('postgres://'):
                database_url = database_url.replace('postgres://', 'postgresql://', 1)
            
            self.db_type = 'postgresql'
            self.database_url = database_url
            print(f"🐘 Usando PostgreSQL: {database_url[:50]}...")
        else:
            # SQLite (desenvolvimento local)
            self.db_type = 'sqlite'
            self.db_path = db_path or "3dbenchy.db"
            print(f"📁 Usando SQLite: {self.db_path}")
        
        self.init_database()

    def get_connection(self):
        """Obter conexão com o banco de dados"""
        if self.db_type == 'postgresql':
            conn = psycopg.connect(self.database_url, row_factory=dict_row)
            return conn
        else:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            return conn

    def get_cursor(self, conn):
        """Obter cursor apropriado para o tipo de banco"""
        if self.db_type == 'postgresql':
            return conn.cursor()
        else:
            return conn.cursor()
    
    def init_database(self):
        """Inicializar todas as tabelas do banco de dados"""
        try:
            with self.get_connection() as conn:
                cursor = self.get_cursor(conn)
                
                if self.db_type == 'postgresql':
                    self._create_postgresql_tables(cursor)
                else:
                    self._create_sqlite_tables(cursor)
                
                conn.commit()
                print("✅ Banco de dados inicializado com sucesso")
                
                # Inserir produtos de exemplo se não existirem
                self._insert_sample_products(cursor)
                conn.commit()
                
        except Exception as e:
            print(f"❌ Erro ao inicializar banco de dados: {e}")
            raise
    
    def _create_postgresql_tables(self, cursor):
        """Criar tabelas para PostgreSQL"""
        # Tabela de usuários
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                email VARCHAR(255) UNIQUE NOT NULL,
                password_hash VARCHAR(255),
                salt VARCHAR(255),
                oauth_provider VARCHAR(50),
                oauth_id VARCHAR(255),
                avatar_url TEXT,
                is_admin BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabela de produtos
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                description TEXT,
                price DECIMAL(10,2) NOT NULL,
                category VARCHAR(100),
                image_url TEXT,
                is_featured BOOLEAN DEFAULT FALSE,
                is_active BOOLEAN DEFAULT TRUE,
                stock_quantity INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabela de carrinho
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cart_items (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL,
                product_id INTEGER NOT NULL,
                quantity INTEGER NOT NULL DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (product_id) REFERENCES products (id),
                UNIQUE(user_id, product_id)
            )
        ''')
        
        # Tabela de tokens JWT
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS jwt_tokens (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL,
                token_hash VARCHAR(255) NOT NULL,
                expires_at TIMESTAMP NOT NULL,
                is_revoked BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Índices para PostgreSQL
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_products_category ON products(category)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_products_featured ON products(is_featured)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_cart_user ON cart_items(user_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_jwt_tokens_user ON jwt_tokens(user_id)')
    
    def _create_sqlite_tables(self, cursor):
        """Criar tabelas para SQLite (código original)"""
        # Tabela de usuários
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT,
                salt TEXT,
                oauth_provider TEXT,
                oauth_id TEXT,
                avatar_url TEXT,
                is_admin BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabela de produtos
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                price DECIMAL(10,2) NOT NULL,
                category TEXT,
                image_url TEXT,
                is_featured BOOLEAN DEFAULT FALSE,
                is_active BOOLEAN DEFAULT TRUE,
                stock_quantity INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabela de carrinho
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cart_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                product_id INTEGER NOT NULL,
                quantity INTEGER NOT NULL DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (product_id) REFERENCES products (id),
                UNIQUE(user_id, product_id)
            )
        ''')
        
        # Tabela de tokens JWT
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS jwt_tokens (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                token_hash TEXT NOT NULL,
                expires_at TIMESTAMP NOT NULL,
                is_revoked BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Índices para SQLite
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_products_category ON products(category)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_products_featured ON products(is_featured)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_cart_user ON cart_items(user_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_jwt_tokens_user ON jwt_tokens(user_id)')
    
    def _insert_sample_products(self, cursor):
        """Inserir produtos de exemplo"""
        cursor.execute('SELECT COUNT(*) FROM products')
        count = cursor.fetchone()
        
        # Acessar o valor baseado no tipo de banco
        if self.db_type == 'postgresql':
            product_count = count['count'] if isinstance(count, dict) else count[0]
        else:
            product_count = count[0]
        
        if product_count == 0:
            sample_products = [
                ("Apache AH-64 Helicopter", "Modelo detalhado do helicóptero de combate Apache AH-64. Perfeito para colecionadores e entusiastas de aviação militar.", 89.90, "aeronaves", None, True, True, 10),
                ("F-22 Raptor Fighter Jet", "Caça stealth F-22 Raptor em escala detalhada. Inclui detalhes internos e externos precisos.", 129.90, "aeronaves", None, True, True, 8),
                ("M1A2 Abrams Tank", "Tanque de guerra americano M1A2 Abrams com detalhes realistas e alta qualidade de impressão.", 149.90, "terrestres", None, True, True, 5),
                ("USS Enterprise Aircraft Carrier", "Porta-aviões nuclear USS Enterprise em escala reduzida com detalhes impressionantes.", 299.90, "navais", None, True, True, 3),
                ("Millennium Falcon", "Nave espacial icônica de Star Wars com todos os detalhes externos e internos.", 199.90, "ficção", None, False, True, 7),
                ("Lamborghini Aventador", "Superesportivo italiano em escala perfeita com detalhes automotivos precisos.", 179.90, "automotivos", None, False, True, 6)
            ]
            
            if self.db_type == 'postgresql':
                cursor.executemany('''
                    INSERT INTO products (name, description, price, category, image_url, is_featured, is_active, stock_quantity)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ''', sample_products)
            else:
                cursor.executemany('''
                    INSERT INTO products (name, description, price, category, image_url, is_featured, is_active, stock_quantity)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', sample_products)
            
            print("✅ Produtos de exemplo inseridos")

    # Métodos para usuários (adaptados para ambos os bancos)
    def hash_password(self, password: str) -> tuple:
        """Gerar hash seguro da senha com salt"""
        salt = secrets.token_hex(32)
        password_hash = hashlib.pbkdf2_hmac('sha256', 
                                          password.encode('utf-8'), 
                                          salt.encode('utf-8'), 
                                          100000)
        return password_hash.hex(), salt
    
    def verify_password(self, password: str, password_hash: str, salt: str) -> bool:
        """Verificar senha contra hash armazenado"""
        computed_hash = hashlib.pbkdf2_hmac('sha256',
                                          password.encode('utf-8'),
                                          salt.encode('utf-8'),
                                          100000)
        return computed_hash.hex() == password_hash
    
    def create_user(self, name: str, email: str, password: str = None, 
                   oauth_provider: str = None, oauth_id: str = None, 
                   avatar_url: str = None) -> Dict[str, Any]:
        """Criar novo usuário"""
        try:
            with self.get_connection() as conn:
                cursor = self.get_cursor(conn)
                
                # Verificar se email já existe
                if self.db_type == 'postgresql':
                    cursor.execute('SELECT id FROM users WHERE email = %s', (email,))
                else:
                    cursor.execute('SELECT id FROM users WHERE email = ?', (email,))
                
                if cursor.fetchone():
                    return {
                        'success': False, 
                        'error': 'Email já cadastrado', 
                        'code': 'EMAIL_EXISTS'
                    }
                
                # Preparar dados do usuário
                if password:
                    password_hash, salt = self.hash_password(password)
                else:
                    password_hash, salt = None, None
                
                # Inserir usuário
                if self.db_type == 'postgresql':
                    cursor.execute('''
                        INSERT INTO users (name, email, password_hash, salt, oauth_provider, oauth_id, avatar_url)
                        VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING id
                    ''', (name, email, password_hash, salt, oauth_provider, oauth_id, avatar_url))
                    user_id = cursor.fetchone()['id']
                else:
                    cursor.execute('''
                        INSERT INTO users (name, email, password_hash, salt, oauth_provider, oauth_id, avatar_url)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (name, email, password_hash, salt, oauth_provider, oauth_id, avatar_url))
                    user_id = cursor.lastrowid
                
                conn.commit()
                
                print(f"✅ Usuário criado: {email} (ID: {user_id})")
                return {
                    'success': True,
                    'message': 'Usuário criado com sucesso',
                    'user': {
                        'id': user_id,
                        'name': name,
                        'email': email,
                        'avatar_url': avatar_url,
                        'is_admin': False
                    }
                }
                
        except Exception as e:
            print(f"❌ Erro ao criar usuário: {e}")
            return {'success': False, 'error': 'Erro interno do servidor'}
    
    def authenticate_user(self, email: str, password: str) -> Dict[str, Any]:
        """Autenticar usuário com email e senha"""
        try:
            with self.get_connection() as conn:
                cursor = self.get_cursor(conn)
                
                if self.db_type == 'postgresql':
                    cursor.execute('''
                        SELECT id, name, email, password_hash, salt, avatar_url, is_admin 
                        FROM users 
                        WHERE email = %s AND password_hash IS NOT NULL
                    ''', (email,))
                else:
                    cursor.execute('''
                        SELECT id, name, email, password_hash, salt, avatar_url, is_admin 
                        FROM users 
                        WHERE email = ? AND password_hash IS NOT NULL
                    ''', (email,))
                
                user = cursor.fetchone()
                
                if user and self.verify_password(password, user['password_hash'], user['salt']):
                    print(f"✅ Login bem-sucedido: {email}")
                    return {
                        'success': True,
                        'message': 'Login realizado com sucesso',
                        'user': {
                            'id': user['id'],
                            'name': user['name'],
                            'email': user['email'],
                            'avatar_url': user['avatar_url'],
                            'is_admin': bool(user['is_admin'])
                        }
                    }
                else:
                    return {
                        'success': False,
                        'error': 'Email ou senha incorretos'
                    }
                    
        except Exception as e:
            print(f"❌ Erro na autenticação: {e}")
            return {'success': False, 'error': 'Erro interno do servidor'}

    def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Buscar usuário por ID"""
        try:
            with self.get_connection() as conn:
                cursor = self.get_cursor(conn)
                
                if self.db_type == 'postgresql':
                    cursor.execute('''
                        SELECT id, name, email, avatar_url, is_admin, created_at
                        FROM users 
                        WHERE id = %s
                    ''', (user_id,))
                else:
                    cursor.execute('''
                        SELECT id, name, email, avatar_url, is_admin, created_at
                        FROM users 
                        WHERE id = ?
                    ''', (user_id,))
                
                user = cursor.fetchone()
                
                if user:
                    return {
                        'id': user['id'],
                        'name': user['name'],
                        'email': user['email'],
                        'avatar_url': user['avatar_url'],
                        'is_admin': bool(user['is_admin']),
                        'created_at': user['created_at']
                    }
                return None
                
        except Exception as e:
            print(f"❌ Erro ao buscar usuário: {e}")
            return None

    def get_products(self, category: str = None, featured_only: bool = False) -> List[Dict[str, Any]]:
        """Buscar produtos com filtros opcionais"""
        try:
            with self.get_connection() as conn:
                cursor = self.get_cursor(conn)
                
                query = 'SELECT * FROM products WHERE is_active = TRUE'
                params = []
                
                if category:
                    if self.db_type == 'postgresql':
                        query += ' AND category = %s'
                    else:
                        query += ' AND category = ?'
                    params.append(category)
                
                if featured_only:
                    query += ' AND is_featured = TRUE'
                
                query += ' ORDER BY created_at DESC'
                
                cursor.execute(query, params)
                products = cursor.fetchall()
                
                return [dict(product) for product in products]
                
        except Exception as e:
            print(f"❌ Erro ao buscar produtos: {e}")
            return []

    # Adicionar outros métodos conforme necessário...

