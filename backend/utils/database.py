import sqlite3
import psycopg2
import psycopg2.extras
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
        if db_path is None:
            self.db_path = "3dbenchy.db"
        else:
            self.db_path = db_path
        
        print(f"📁 Tentando criar banco em: {self.db_path}")
        self.init_database()

    
    def get_connection(self):
        """Obter conexão com o banco de dados"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Permite acesso por nome da coluna
        return conn
    
    def init_database(self):
        """Inicializar todas as tabelas do banco de dados"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
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
                
                # Tabela de tokens JWT (para logout/blacklist)
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
                
                # Índices para performance
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_products_category ON products(category)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_products_featured ON products(is_featured)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_cart_user ON cart_items(user_id)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_jwt_tokens_user ON jwt_tokens(user_id)')
                
                conn.commit()
                print("✅ Banco de dados inicializado com sucesso")
                
                # Inserir produtos de exemplo se não existirem
                self._insert_sample_products(cursor)
                conn.commit()
                
        except Exception as e:
            print(f"❌ Erro ao inicializar banco de dados: {e}")
            raise
    
    def _insert_sample_products(self, cursor):
        """Inserir produtos de exemplo"""
        cursor.execute('SELECT COUNT(*) FROM products')
        if cursor.fetchone()[0] == 0:
            sample_products = [
                ("Apache AH-64 Helicopter", "Modelo detalhado do helicóptero de combate Apache AH-64. Perfeito para colecionadores e entusiastas de aviação militar.", 89.90, "aeronaves", None, True, True, 10),
                ("F-22 Raptor Fighter Jet", "Caça stealth F-22 Raptor em escala detalhada. Inclui detalhes internos e externos precisos.", 129.90, "aeronaves", None, True, True, 8),
                ("M1A2 Abrams Tank", "Tanque de guerra americano M1A2 Abrams com detalhes realistas e alta qualidade de impressão.", 149.90, "terrestres", None, True, True, 5),
                ("USS Enterprise Aircraft Carrier", "Porta-aviões nuclear USS Enterprise em escala reduzida com detalhes impressionantes.", 299.90, "navais", None, True, True, 3),
                ("Millennium Falcon", "Nave espacial icônica de Star Wars com todos os detalhes externos e internos.", 199.90, "ficção", None, False, True, 7),
                ("Lamborghini Aventador", "Superesportivo italiano em escala perfeita com detalhes automotivos precisos.", 179.90, "automotivos", None, False, True, 6)
            ]
            
            cursor.executemany('''
                INSERT INTO products (name, description, price, category, image_url, is_featured, is_active, stock_quantity)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', sample_products)
            
            print("✅ Produtos de exemplo inseridos")
    
    # Métodos para usuários
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
                cursor = conn.cursor()
                
                # Verificar se email já existe
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
                cursor = conn.cursor()
                
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
                cursor = conn.cursor()
                
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
    
    def get_user_by_oauth(self, oauth_provider: str, oauth_id: str) -> Optional[Dict[str, Any]]:
        """Buscar usuário por OAuth"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT id, name, email, avatar_url, is_admin
                    FROM users 
                    WHERE oauth_provider = ? AND oauth_id = ?
                ''', (oauth_provider, oauth_id))
                
                user = cursor.fetchone()
                
                if user:
                    return {
                        'id': user['id'],
                        'name': user['name'],
                        'email': user['email'],
                        'avatar_url': user['avatar_url'],
                        'is_admin': bool(user['is_admin'])
                    }
                return None
                
        except Exception as e:
            print(f"❌ Erro ao buscar usuário OAuth: {e}")
            return None
    
    # Métodos para produtos
    def get_products(self, category: str = None, featured_only: bool = False) -> List[Dict[str, Any]]:
        """Buscar produtos com filtros opcionais"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                query = 'SELECT * FROM products WHERE is_active = TRUE'
                params = []
                
                if category:
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
    
    def get_product_by_id(self, product_id: int) -> Optional[Dict[str, Any]]:
        """Buscar produto por ID"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute('SELECT * FROM products WHERE id = ? AND is_active = TRUE', (product_id,))
                product = cursor.fetchone()
                
                return dict(product) if product else None
                
        except Exception as e:
            print(f"❌ Erro ao buscar produto: {e}")
            return None
    
    def create_product(self, name: str, description: str, price: float, 
                      category: str, image_url: str = None, is_featured: bool = False,
                      stock_quantity: int = 0) -> Dict[str, Any]:
        """Criar novo produto"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO products (name, description, price, category, image_url, is_featured, stock_quantity)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (name, description, price, category, image_url, is_featured, stock_quantity))
                
                product_id = cursor.lastrowid
                conn.commit()
                
                return {
                    'success': True,
                    'message': 'Produto criado com sucesso',
                    'product_id': product_id
                }
                
        except Exception as e:
            print(f"❌ Erro ao criar produto: {e}")
            return {'success': False, 'error': 'Erro interno do servidor'}
    
    # Métodos para carrinho
    def add_to_cart(self, user_id: int, product_id: int, quantity: int = 1) -> Dict[str, Any]:
        """Adicionar produto ao carrinho"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Verificar se produto existe
                cursor.execute('SELECT id, stock_quantity FROM products WHERE id = ? AND is_active = TRUE', (product_id,))
                product = cursor.fetchone()
                
                if not product:
                    return {'success': False, 'error': 'Produto não encontrado'}
                
                if product['stock_quantity'] < quantity:
                    return {'success': False, 'error': 'Estoque insuficiente'}
                
                # Verificar se item já está no carrinho
                cursor.execute('SELECT id, quantity FROM cart_items WHERE user_id = ? AND product_id = ?', 
                             (user_id, product_id))
                existing_item = cursor.fetchone()
                
                if existing_item:
                    # Atualizar quantidade
                    new_quantity = existing_item['quantity'] + quantity
                    cursor.execute('''
                        UPDATE cart_items 
                        SET quantity = ?, updated_at = CURRENT_TIMESTAMP 
                        WHERE id = ?
                    ''', (new_quantity, existing_item['id']))
                else:
                    # Adicionar novo item
                    cursor.execute('''
                        INSERT INTO cart_items (user_id, product_id, quantity)
                        VALUES (?, ?, ?)
                    ''', (user_id, product_id, quantity))
                
                conn.commit()
                
                return {
                    'success': True,
                    'message': 'Produto adicionado ao carrinho'
                }
                
        except Exception as e:
            print(f"❌ Erro ao adicionar ao carrinho: {e}")
            return {'success': False, 'error': 'Erro interno do servidor'}
    
    def get_cart_items(self, user_id: int) -> List[Dict[str, Any]]:
        """Buscar itens do carrinho do usuário"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT 
                        ci.id,
                        ci.quantity,
                        ci.created_at,
                        p.id as product_id,
                        p.name as product_name,
                        p.price,
                        p.image_url
                    FROM cart_items ci
                    JOIN products p ON ci.product_id = p.id
                    WHERE ci.user_id = ? AND p.is_active = TRUE
                    ORDER BY ci.created_at DESC
                ''', (user_id,))
                
                items = cursor.fetchall()
                return [dict(item) for item in items]
                
        except Exception as e:
            print(f"❌ Erro ao buscar carrinho: {e}")
            return []
    
    def remove_from_cart(self, user_id: int, cart_item_id: int) -> Dict[str, Any]:
        """Remover item do carrinho"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute('DELETE FROM cart_items WHERE id = ? AND user_id = ?', 
                             (cart_item_id, user_id))
                
                if cursor.rowcount > 0:
                    conn.commit()
                    return {'success': True, 'message': 'Item removido do carrinho'}
                else:
                    return {'success': False, 'error': 'Item não encontrado'}
                
        except Exception as e:
            print(f"❌ Erro ao remover do carrinho: {e}")
            return {'success': False, 'error': 'Erro interno do servidor'}
    
    def clear_cart(self, user_id: int) -> Dict[str, Any]:
        """Limpar carrinho do usuário"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute('DELETE FROM cart_items WHERE user_id = ?', (user_id,))
                conn.commit()
                
                return {'success': True, 'message': 'Carrinho limpo'}
                
        except Exception as e:
            print(f"❌ Erro ao limpar carrinho: {e}")
            return {'success': False, 'error': 'Erro interno do servidor'}
    
    # Métodos para JWT
    def save_jwt_token(self, user_id: int, token: str, expires_at: datetime) -> bool:
        """Salvar token JWT no banco"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                token_hash = hashlib.sha256(token.encode()).hexdigest()
                
                cursor.execute('''
                    INSERT INTO jwt_tokens (user_id, token_hash, expires_at)
                    VALUES (?, ?, ?)
                ''', (user_id, token_hash, expires_at))
                
                conn.commit()
                return True
                
        except Exception as e:
            print(f"❌ Erro ao salvar token: {e}")
            return False
    
    def is_token_revoked(self, token: str) -> bool:
        """Verificar se token foi revogado"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                token_hash = hashlib.sha256(token.encode()).hexdigest()
                
                cursor.execute('''
                    SELECT is_revoked FROM jwt_tokens 
                    WHERE token_hash = ? AND expires_at > CURRENT_TIMESTAMP
                ''', (token_hash,))
                
                result = cursor.fetchone()
                return result['is_revoked'] if result else True
                
        except Exception as e:
            print(f"❌ Erro ao verificar token: {e}")
            return True
    
    def revoke_user_tokens(self, user_id: int) -> bool:
        """Revogar todos os tokens de um usuário"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    UPDATE jwt_tokens 
                    SET is_revoked = TRUE 
                    WHERE user_id = ?
                ''', (user_id,))
                
                conn.commit()
                return True
                
        except Exception as e:
            print(f"❌ Erro ao revogar tokens: {e}")
            return False
    
    def health_check(self) -> Dict[str, Any]:
        """Verificar saúde do banco de dados"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT COUNT(*) as user_count FROM users')
                user_count = cursor.fetchone()['user_count']
                
                cursor.execute('SELECT COUNT(*) as product_count FROM products WHERE is_active = TRUE')
                product_count = cursor.fetchone()['product_count']
                
                return {
                    'status': 'healthy',
                    'users': user_count,
                    'products': product_count,
                    'database': 'sqlite'
                }
                
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e),
                'database': 'sqlite'

            }
