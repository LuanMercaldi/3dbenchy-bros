from flask import Blueprint, request, jsonify
from utils.database import DatabaseManager
from utils.auth_helpers import require_auth, get_current_user

cart_bp = Blueprint('cart', __name__)
db = DatabaseManager()

@cart_bp.route('', methods=['GET'])
@require_auth
def get_cart():
    """Obter itens do carrinho do usuário logado"""
    try:
        current_user = get_current_user()
        cart_items = db.get_cart_items(current_user['user_id'])
        
        # Calcular totais
        total_items = sum(item.get('quantity', 0) for item in cart_items)
        total_price = sum(item.get('price', 0) * item.get('quantity', 0) for item in cart_items)
        
        return jsonify({
            "items": cart_items,
            "total_items": total_items,
            "total_price": round(total_price, 2),
            "currency": "BRL"
        }), 200
        
    except Exception as e:
        print(f"❌ Erro ao buscar carrinho: {e}")
        return jsonify({"error": "Erro interno do servidor"}), 500

@cart_bp.route('', methods=['POST'])
@require_auth
def add_to_cart():
    """Adicionar produto ao carrinho"""
    try:
        current_user = get_current_user()
        data = request.get_json()
        
        # Validar dados obrigatórios
        if not data or 'product_id' not in data:
            return jsonify({"error": "product_id é obrigatório"}), 400
        
        product_id = data['product_id']
        quantity = data.get('quantity', 1)
        
        # Validar tipos
        try:
            product_id = int(product_id)
            quantity = int(quantity)
            if quantity <= 0:
                return jsonify({"error": "Quantidade deve ser maior que zero"}), 400
        except (ValueError, TypeError):
            return jsonify({"error": "product_id e quantity devem ser números válidos"}), 400
        
        # Verificar se produto existe
        product = db.get_product_by_id(product_id)
        if not product:
            return jsonify({"error": "Produto não encontrado"}), 404
        
        # Adicionar ao carrinho
        result = db.add_to_cart(current_user['user_id'], product_id, quantity)
        
        if result.get('success'):
            # Retornar carrinho atualizado
            cart_items = db.get_cart_items(current_user['user_id'])
            total_items = sum(item.get('quantity', 0) for item in cart_items)
            
            return jsonify({
                "message": result.get('message', 'Produto adicionado ao carrinho'),
                "cart_total_items": total_items
            }), 200
        else:
            return jsonify({"error": result.get('error', 'Erro ao adicionar ao carrinho')}), 400
            
    except Exception as e:
        print(f"❌ Erro ao adicionar ao carrinho: {e}")
        return jsonify({"error": "Erro interno do servidor"}), 500

@cart_bp.route('/<int:cart_item_id>', methods=['DELETE'])
@require_auth
def remove_from_cart(cart_item_id):
    """Remover item específico do carrinho"""
    try:
        current_user = get_current_user()
        
        result = db.remove_from_cart(current_user['user_id'], cart_item_id)
        
        if result.get('success'):
            # Retornar carrinho atualizado
            cart_items = db.get_cart_items(current_user['user_id'])
            total_items = sum(item.get('quantity', 0) for item in cart_items)
            
            return jsonify({
                "message": result.get('message', 'Item removido do carrinho'),
                "cart_total_items": total_items
            }), 200
        else:
            return jsonify({"error": result.get('error', 'Item não encontrado')}), 404
            
    except Exception as e:
        print(f"❌ Erro ao remover do carrinho: {e}")
        return jsonify({"error": "Erro interno do servidor"}), 500

@cart_bp.route('/clear', methods=['DELETE'])
@require_auth
def clear_cart():
    """Limpar todo o carrinho do usuário"""
    try:
        current_user = get_current_user()
        
        result = db.clear_cart(current_user['user_id'])
        
        if result.get('success'):
            return jsonify({
                "message": result.get('message', 'Carrinho limpo'),
                "cart_total_items": 0
            }), 200
        else:
            return jsonify({"error": result.get('error', 'Erro ao limpar carrinho')}), 400
            
    except Exception as e:
        print(f"❌ Erro ao limpar carrinho: {e}")
        return jsonify({"error": "Erro interno do servidor"}), 500

@cart_bp.route('/count', methods=['GET'])
@require_auth
def get_cart_count():
    """Obter apenas a contagem de itens no carrinho"""
    try:
        current_user = get_current_user()
        cart_items = db.get_cart_items(current_user['user_id'])
        total_items = sum(item.get('quantity', 0) for item in cart_items)
        
        return jsonify({
            "total_items": total_items
        }), 200
        
    except Exception as e:
        print(f"❌ Erro ao contar itens do carrinho: {e}")
        return jsonify({"error": "Erro interno do servidor"}), 500
