// Configurações da aplicação
const CONFIG = {
    // URL base da API - detecta automaticamente o ambiente
    API_BASE_URL: (() => {
        const hostname = window.location.hostname;
        
        if (hostname === 'localhost' || hostname === '127.0.0.1') {
            return 'http://localhost:5000';
        } else if (hostname.includes('github.io')) {
            return 'https://seu-backend-render.onrender.com';
        } else {
            return 'https://seu-backend-render.onrender.com';
        }
    })(),
};

// Tornar CONFIG disponível globalmente
window.CONFIG = CONFIG;
window.APP_NAME = CONFIG.APP_NAME;

