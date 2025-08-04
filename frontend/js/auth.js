// Funções relacionadas à autenticação
class AuthManager {
    constructor() {
        this.currentUser = null;
        this.accessToken = localStorage.getItem('access_token');
        this.refreshToken = localStorage.getItem('refresh_token');
    }

    async register(name, email, password) {
        // Validar dados no frontend primeiro
        const nameValidation = this.validateName(name);
        if (!nameValidation.valid) {
            alert(nameValidation.errors.join('\n'));
            return;
        }

        const emailValidation = this.validateEmail(email);
        if (!emailValidation.valid) {
            alert(emailValidation.errors.join('\n'));
            return;
        }

        const passwordValidation = securityManager.validatePassword(password);
        if (!passwordValidation.valid) {
            alert(passwordValidation.errors.join('\n'));
            return;
        }

        // Rate limiting no frontend
        const clientId = this.getClientId();
        if (!registerRateLimiter(clientId)) {
            alert('Muitas tentativas de cadastro. Tente novamente em alguns minutos.');
            return;
        }

        try {
            const response = await fetch(`${CONFIG.API_BASE_URL}/auth/register`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    name: securityManager.sanitizeInput(name),
                    email: securityManager.sanitizeInput(email),
                    password: password
                })
            });

            const data = await response.json();

            if (response.ok) {
                this.saveTokens(data.tokens);
                this.currentUser = data.user;
                this.updateUserInterface();
                alert('Cadastro realizado com sucesso!');
            } else {
                alert(data.error || 'Erro no cadastro');
            }
        } catch (error) {
            console.error('Erro no cadastro:', error);
            alert('Erro de conexão. Tente novamente.');
        }
    }

    validateName(name) {
        const result = { valid: true, errors: [] };

        if (!name || typeof name !== 'string') {
            result.valid = false;
            result.errors.push('Nome é obrigatório');
            return result;
        }

        name = name.trim();

        if (name.length < 2) {
            result.valid = false;
            result.errors.push('Nome deve ter pelo menos 2 caracteres');
        }

        if (name.length > 100) {
            result.valid = false;
            result.errors.push('Nome muito longo');
        }

        if (/[<>"']/.test(name)) {
            result.valid = false;
            result.errors.push('Nome contém caracteres inválidos');
        }

        return result;
    }

    validateEmail(email) {
        const result = { valid: true, errors: [] };

        if (!securityManager.validateEmail(email)) {
            result.valid = false;
            result.errors.push('Email inválido');
        }

        return result;
    }

    getClientId() {
        // Gerar ID único do cliente para rate limiting
        let clientId = localStorage.getItem('client_id');
        if (!clientId) {
            clientId = 'client_' + Math.random().toString(36).substr(2, 9);
            localStorage.setItem('client_id', clientId);
        }
        return clientId;
    
    }
    async checkAuthStatus() {
        try {
            // Verificar se existe token armazenado
            const token = localStorage.getItem('access_token');
            if (!token) {
                this.currentUser = null;
                return false;
            }
    
            // Validar token com o backend
            const response = await fetch(`${CONFIG.API_BASE_URL}/api/auth/verify`, {
                method: 'GET',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                }
            });
    
            if (response.ok) {
                const userData = await response.json();
                this.currentUser = userData.user;
                this.updateUIForLoggedInUser();
                return true;
            } else {
                // Token inválido, limpar armazenamento
                this.logout();
                return false;
            }
        } catch (error) {
            console.error('Erro ao verificar status de autenticação:', error);
            return false;
        }
    }
    
    updateUIForLoggedInUser() {
        const loginBtn = document.getElementById('loginBtn');
        const adminBtn = document.getElementById('adminBtn');
        
        if (loginBtn) {
            loginBtn.textContent = 'LOGOUT';
            loginBtn.onclick = () => this.logout();
        }
        
        if (adminBtn && this.currentUser?.role === 'admin') {
            adminBtn.style.display = 'block';
        }
    }
    
}

// Criar instância global

const authManager = new AuthManager();
