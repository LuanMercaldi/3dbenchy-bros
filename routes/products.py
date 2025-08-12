from flask import Blueprint, request, jsonify
from utils.database import DatabaseManager

products_bp = Blueprint('products', __name__)
db = DatabaseManager()

@products_bp.route('', methods=['GET'])
def get_products():
    """Listar todos os produtos"""
    try:
        products = db.get_products()
        
        return jsonify({
            "products": products,
            "total": len(products)
        }), 200
        
    except Exception as e:
        print(f"❌ Erro ao buscar produtos: {e}")
        return jsonify({"error": "Erro interno do servidor"}), 500

@products_bp.route('/featured', methods=['GET'])
def get_featured_products():
    """Listar produtos em destaque"""
    try:
        products = db.get_products()
        featured = [p for p in products if p.get('is_featured')]
        
        return jsonify(featured), 200
        
    except Exception as e:
        print(f"❌ Erro ao buscar produtos em destaque: {e}")
        return jsonify({"error": "Erro interno do servidor"}), 500

@products_bp.route('/<int:product_id>', methods=['GET'])
def get_product(product_id):
    """Buscar produto específico por ID"""
    try:
        product = db.get_product_by_id(product_id)
        
        if product:
            return jsonify(product), 200
        else:
            return jsonify({"error": "Produto não encontrado"}), 404
            
    except Exception as e:
        print(f"❌ Erro ao buscar produto: {e}")
        return jsonify({"error": "Erro interno do servidor"}), 500

@products_bp.route('/categories', methods=['GET'])
def get_categories():
    """Listar todas as categorias disponíveis"""
    try:
        categories = [
            {"id": "aeronaves", "name": "Aeronaves", "description": "Aviões, helicópteros e aeronaves militares"},
            {"id": "terrestres", "name": "Terrestres", "description": "Tanques, veículos militares e terrestres"},
            {"id": "navais", "name": "Navais", "description": "Navios, submarinos e embarcações"},
            {"id": "ficção", "name": "Ficção Científica", "description": "Naves espaciais e veículos de ficção"},
            {"id": "automotivos", "name": "Automotivos", "description": "Carros esportivos e veículos civis"}
        ]
        
        return jsonify({"categories": categories}), 200
        
    except Exception as e:
        print(f"❌ Erro ao buscar categorias: {e}")
        return jsonify({"error": "Erro interno do servidor"}), 500
