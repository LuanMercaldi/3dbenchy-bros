/**
 * Biblioteca de segurança para sanitização de dados
 */
class SecurityManager {
    constructor() {
        this.init();
    }

    init() {
        // Configurar CSP via JavaScript se não estiver no servidor
        this.setupCSP();
    }

    /**
     * Sanitizar HTML para prevenir XSS
     * @param {string} html - HTML a ser sanitizado
     * @returns {string} - HTML sanitizado
     */
    sanitizeHTML(html) {
        if (typeof html !== 'string') {
            return '';
        }

        // Criar elemento temporário para sanitização
        const temp = document.createElement('div');
        temp.textContent = html;
        
        // Lista de tags permitidas (whitelist)
        const allowedTags = ['b', 'i', 'em', 'strong', 'span', 'p', 'br'];
        const allowedAttributes = ['class', 'id'];
        
        // Converter texto para HTML seguro
        let sanitized = temp.innerHTML;
        
        // Remover scripts e outros elementos perigosos
        sanitized = sanitized.replace(/<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi, '');
        sanitized = sanitized.replace(/<iframe\b[^<]*(?:(?!<\/iframe>)<[^<]*)*<\/iframe>/gi, '');
        sanitized = sanitized.replace(/<object\b[^<]*(?:(?!<\/object>)<[^<]*)*<\/object>/gi, '');
        sanitized = sanitized.replace(/<embed\b[^<]*(?:(?!<\/embed>)<[^<]*)*<\/embed>/gi, '');
        sanitized = sanitized.replace(/<link\b[^<]*>/gi, '');
        sanitized = sanitized.replace(/<meta\b[^<]*>/gi, '');
        
        // Remover atributos perigosos
        sanitized = sanitized.replace(/\son\w+\s*=\s*["'][^"']*["']/gi, ''); // onclick, onload, etc.
        sanitized = sanitized.replace(/\sjavascript\s*:/gi, '');
        sanitized = sanitized.replace(/\svbscript\s*:/gi, '');
        sanitized = sanitized.replace(/\sdata\s*:/gi, '');
        
        return sanitized;
    }

    /**
     * Escapar texto para uso seguro em HTML
     * @param {string} text - Texto a ser escapado
     * @returns {string} - Texto escapado
     */
    escapeHTML(text) {
        if (typeof text !== 'string') {
            return '';
        }

        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    /**
     * Sanitizar dados de entrada de formulários
     * @param {string} input - Entrada do usuário
     * @returns {string} - Entrada sanitizada
     */
    sanitizeInput(input) {
        if (typeof input !== 'string') {
            return '';
        }

        // Remover caracteres perigosos
        return input
            .trim()
            .replace(/[<>]/g, '') // Remover < e >
            .replace(/javascript:/gi, '') // Remover javascript:
            .replace(/vbscript:/gi, '') // Remover vbscript:
            .replace(/on\w+=/gi, '') // Remover event handlers
            .substring(0, 1000); // Limitar tamanho
    }

    /**
     * Validar email
     * @param {string} email - Email a ser validado
     * @returns {boolean} - Se o email é válido
     */
    validateEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email) && email.length <= 254;
    }

    /**
     * Validar senha forte
     * @param {string} password - Senha a ser validada
     * @returns {object} - Resultado da validação
     */
    validatePassword(password) {
        const result = {
            valid: true,
            errors: []
        };

        if (password.length < 8) {
            result.valid = false;
            result.errors.push('Senha deve ter pelo menos 8 caracteres');
        }

        if (!/[A-Z]/.test(password)) {
            result.valid = false;
            result.errors.push('Senha deve conter pelo menos uma letra maiúscula');
        }

        if (!/[a-z]/.test(password)) {
            result.valid = false;
            result.errors.push('Senha deve conter pelo menos uma letra minúscula');
        }

        if (!/[0-9]/.test(password)) {
            result.valid = false;
            result.errors.push('Senha deve conter pelo menos um número');
        }

        if (!/[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]/.test(password)) {
            result.valid = false;
            result.errors.push('Senha deve conter pelo menos um caractere especial');
        }

        return result;
    }

    /**
     * Configurar Content Security Policy básico
     */
    setupCSP() {
        // Apenas se CSP não estiver configurado no servidor
        if (!document.querySelector('meta[http-equiv="Content-Security-Policy"]')) {
            const meta = document.createElement('meta');
            meta.httpEquiv = 'Content-Security-Policy';
            meta.content = "default-src 'self'; script-src 'self' 'unsafe-inline' https://fonts.googleapis.com; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src 'self' https://fonts.gstatic.com; img-src 'self' data: https:; connect-src 'self' https://api.github.com https://accounts.google.com;";
            document.head.appendChild(meta);
        }
    }

    /**
     * Gerar nonce para scripts inline seguros
     * @returns {string} - Nonce único
     */
    generateNonce() {
        const array = new Uint8Array(16);
        crypto.getRandomValues(array);
        return Array.from(array, byte => byte.toString(16).padStart(2, '0')).join('');
    }

    /**
     * Rate limiting simples no frontend
     */
    createRateLimiter(maxRequests = 10, windowMs = 60000) {
        const requests = new Map();

        return function(identifier) {
            const now = Date.now();
            const windowStart = now - windowMs;

            // Limpar requisições antigas
            for (const [key, timestamps] of requests.entries()) {
                requests.set(key, timestamps.filter(time => time > windowStart));
                if (requests.get(key).length === 0) {
                    requests.delete(key);
                }
            }

            // Verificar limite para este identificador
            const userRequests = requests.get(identifier) || [];
            
            if (userRequests.length >= maxRequests) {
                return false; // Rate limit excedido
            }

            // Adicionar nova requisição
            userRequests.push(now);
            requests.set(identifier, userRequests);
            
            return true; // Permitido
        };
    }
}

// Criar instância global
const securityManager = new SecurityManager();

// Rate limiter para login (máximo 5 tentativas por minuto)
const loginRateLimiter = securityManager.createRateLimiter(5, 60000);

// Rate limiter para cadastro (máximo 3 tentativas por minuto)
const registerRateLimiter = securityManager.createRateLimiter(3, 60000);