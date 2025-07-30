#!/usr/bin/env python3
"""
Servidor Proxy para 3DBenchy Bros
Resolve problemas de CORS intermediando requisições entre frontend e backend
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

app = Flask(__name__)

# Configurar CORS para produção
cors_origins = ["https://3dbenchybros.com.br", "https://luanmercaldi.github.io"]
if os.environ.get('FLASK_ENV') == 'development':
    cors_origins.append("*")

CORS(app, origins=cors_origins, supports_credentials=True)

# URL do backend original
BACKEND_URL = "https://0vhlizcklvgn.manus.space/api"

@app.route('/api/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'])
def proxy(path):
    """
    Proxy para todas as requisições da API
    """
    try:
        # URL completa do backend
        url = f"{BACKEND_URL}/{path}"
        
        # Preparar headers (remover headers problemáticos)
        headers = {}
        for key, value in request.headers:
            if key.lower() not in ['host', 'content-length']:
                headers[key] = value
        
        # Fazer requisição para o backend original
        if request.method == 'GET':
            response = requests.get(url, headers=headers, params=request.args)
        elif request.method == 'POST':
            response = requests.post(url, headers=headers, json=request.get_json(), params=request.args)
        elif request.method == 'PUT':
            response = requests.put(url, headers=headers, json=request.get_json(), params=request.args)
        elif request.method == 'DELETE':
            response = requests.delete(url, headers=headers, params=request.args)
        elif request.method == 'OPTIONS':
            # Responder diretamente para requisições OPTIONS (preflight)
            return '', 200
        
        # Retornar resposta do backend
        try:
            # Tentar retornar como JSON
            json_data = response.json()
            return jsonify(json_data), response.status_code
        except ValueError:
            # Se não for JSON válido, retornar como texto
            return response.text, response.status_code, {'Content-Type': 'text/plain'}
        except Exception as e:
            print(f"Erro ao processar resposta: {e}")
            print(f"Content-Type: {response.headers.get('content-type')}")
            print(f"Status: {response.status_code}")
            print(f"Raw content: {response.content[:100]}")
            return jsonify({"error": "Erro ao processar resposta do backend"}), 500
            
    except requests.exceptions.RequestException as e:
        print(f"Erro na requisição: {e}")
        return jsonify({"error": "Erro de conexão com o backend"}), 500
    except Exception as e:
        print(f"Erro interno: {e}")
        return jsonify({"error": "Erro interno do servidor"}), 500

@app.route('/health', methods=['GET'])
def health():
    """
    Endpoint de saúde do proxy
    """
    return jsonify({
        "status": "ok",
        "message": "Proxy server is running",
        "backend_url": BACKEND_URL
    })

@app.route('/', methods=['GET'])
def index():
    """
    Página inicial do proxy
    """
    return jsonify({
        "message": "3DBenchy Bros Proxy Server",
        "version": "1.0.0",
        "endpoints": {
            "/api/*": "Proxy para backend API",
            "/health": "Status do servidor"
        }
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    
    print(f"🚀 Iniciando servidor proxy na porta {port}")
    print(f"🔗 Backend URL: {BACKEND_URL}")
    print(f"🌐 CORS configurado para: https://3dbenchybros.com.br")
    
    app.run(host='0.0.0.0', port=port, debug=debug)

