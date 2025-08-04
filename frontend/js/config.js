// Configurações da aplicação
const CONFIG = {
    // URL base da API - detecta automaticamente o ambiente
    API_BASE_URL: window.location.hostname === 'localhost' 
        ? 'http://localhost:5000' 
        : 'https://seu-backend-render.onrender.com',
    
    // Nome da aplicação
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
        DEBUG: window.location.hostname === 'localhost'
    }
};

// Tornar CONFIG disponível globalmente
window.CONFIG = CONFIG;
window.APP_NAME = CONFIG.APP_NAME;
