#!/usr/bin/env python3
"""
Módulo de Banco de Dados PostgreSQL para 3DBenchy Bros
Gerencia conexões e operações com PostgreSQL
"""

import psycopg2
import psycopg2.extras
import os
import hashlib
import secrets
from datetime import datetime
from typing import Optional, Dict, Any

class DatabaseManager:
    """
    Gerenciador de banco de dados PostgreSQL
    """
    
    def __init__(self):
        self.database_url = os.environ.get('DATABASE_URL')
        if not self.database_url:
            raise ValueError("DATABASE_URL não configurada")
        
        # Inicializar tabelas
        self.init_tables()
    
    def get_connection(self):
        """
        Obter conexão com o banco de dados
        """
        return psycopg2.connect(self.database_url)
    
    def init_tables(self):
        """
        Inicializar tabelas do banco de dados
        """
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    # Tabela de usuários
                    cursor.execute("""
                        CREATE TABLE IF NOT EXISTS users (
                            id SERIAL PRIMARY KEY,
                            name VARCHAR(255) NOT NULL,
                            email VARCHAR(255) UNIQUE NOT NULL,
                            password_hash VARCHAR(255) NOT NULL,
                            salt VARCHAR(255) NOT NULL,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        )
                    """)
                    
                    # Índice para email (performance)
                    cursor.execute("""
                        CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)
                    """)
                    
                    conn.commit()
                    print("✅ Tabelas inicializadas com sucesso")
                    
        except Exception as e:
            print(f"❌ Erro ao inicializar tabelas: {e}")
            raise
    
    def hash_password(self, password: str) -> tuple:
        """
        Gerar hash seguro da senha com salt
        """
        salt = secrets.token_hex(32)
        password_hash = hashlib.pbkdf2_hmac('sha256', 
                                          password.encode('utf-8'), 
                                          salt.encode('utf-8'), 
                                          100000)
        return password_hash.hex(), salt
    
    def verify_password(self, password: str, password_hash: str, salt: str) -> bool:
        """
        Verificar senha contra hash armazenado
        """
        computed_hash = hashlib.pbkdf2_hmac('sha256',
                                          password.encode('utf-8'),
                                          salt.encode('utf-8'),
                                          100000)
        return computed_hash.hex() == password_hash
    
    def create_user(self, name: str, email: str, password: str) -> Dict[str, Any]:
        """
        Criar novo usuário
        """
        try:
            # Verificar se email já existe
            if self.get_user_by_email(email):
                return {
                    "success": False,
                    "error": "Email já cadastrado",
                    "code": "EMAIL_EXISTS"
                }
            
            # Gerar hash da senha
            password_hash, salt = self.hash_password(password)
            
            with self.get_connection() as conn:
                with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
                    cursor.execute("""
                        INSERT INTO users (name, email, password_hash, salt)
                        VALUES (%s, %s, %s, %s)
                        RETURNING id, name, email, created_at
                    """, (name, email, password_hash, salt))
                    
                    user = cursor.fetchone()
                    conn.commit()
                    
                    return {
                        "success": True,
                        "user": dict(user),
                        "message": "Usuário criado com sucesso"
                    }
                    
        except psycopg2.IntegrityError:
            return {
                "success": False,
                "error": "Email já cadastrado",
                "code": "EMAIL_EXISTS"
            }
        except Exception as e:
            print(f"❌ Erro ao criar usuário: {e}")
            return {
                "success": False,
                "error": "Erro interno do servidor",
                "code": "INTERNAL_ERROR"
            }
    
    def authenticate_user(self, email: str, password: str) -> Dict[str, Any]:
        """
        Autenticar usuário
        """
        try:
            user = self.get_user_by_email(email)
            if not user:
                return {
                    "success": False,
                    "error": "Email ou senha incorretos",
                    "code": "INVALID_CREDENTIALS"
                }
            
            # Verificar senha
            if not self.verify_password(password, user['password_hash'], user['salt']):
                return {
                    "success": False,
                    "error": "Email ou senha incorretos",
                    "code": "INVALID_CREDENTIALS"
                }
            
            # Remover dados sensíveis
            user_data = {
                "id": user['id'],
                "name": user['name'],
                "email": user['email'],
                "created_at": user['created_at'].isoformat() if user['created_at'] else None
            }
            
            return {
                "success": True,
                "user": user_data,
                "message": "Login realizado com sucesso"
            }
            
        except Exception as e:
            print(f"❌ Erro ao autenticar usuário: {e}")
            return {
                "success": False,
                "error": "Erro interno do servidor",
                "code": "INTERNAL_ERROR"
            }
    
    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """
        Buscar usuário por email
        """
        try:
            with self.get_connection() as conn:
                with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
                    cursor.execute("""
                        SELECT id, name, email, password_hash, salt, created_at, updated_at
                        FROM users 
                        WHERE email = %s
                    """, (email,))
                    
                    user = cursor.fetchone()
                    return dict(user) if user else None
                    
        except Exception as e:
            print(f"❌ Erro ao buscar usuário: {e}")
            return None
    
    def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """
        Buscar usuário por ID
        """
        try:
            with self.get_connection() as conn:
                with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
                    cursor.execute("""
                        SELECT id, name, email, created_at, updated_at
                        FROM users 
                        WHERE id = %s
                    """, (user_id,))
                    
                    user = cursor.fetchone()
                    return dict(user) if user else None
                    
        except Exception as e:
            print(f"❌ Erro ao buscar usuário: {e}")
            return None
    
    def health_check(self) -> Dict[str, Any]:
        """
        Verificar saúde do banco de dados
        """
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT 1")
                    cursor.fetchone()
                    
                    # Contar usuários
                    cursor.execute("SELECT COUNT(*) FROM users")
                    user_count = cursor.fetchone()[0]
                    
                    return {
                        "status": "healthy",
                        "database": "postgresql",
                        "users_count": user_count,
                        "timestamp": datetime.now().isoformat()
                    }
                    
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

