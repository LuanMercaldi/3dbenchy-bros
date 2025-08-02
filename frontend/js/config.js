// Configurações da aplicação
const CONFIG = {
    // URL base da API
    API_BASE_URL: 'http://localhost:5000',
    
    // Nome da aplicação (para os testes )
    APP_NAME: '3DBenchy Bros',
    
    // Endpoints da API
    API_ENDPOINTS: {
        auth: '/api/auth',
        products: '/api/products',
        cart: '/api/cart'
    },
    
    // Configurações de segurança
    SECURITY: {
        JWT_STORAGE_KEY: '3dbenchy_token',
        REFRESH_TOKEN_KEY: '3dbenchy_refresh'
    },
    
    // Configurações da aplicação
    APP: {
        NAME: '3DBenchy Bros',
        VERSION: '1.0.0',
        DEBUG: true
    }
};

// Tornar CONFIG disponível globalmente
window.CONFIG = CONFIG;

// Também disponibilizar APP_NAME diretamente (para compatibilidade com testes)
window.APP_NAME = CONFIG.APP_NAME;

