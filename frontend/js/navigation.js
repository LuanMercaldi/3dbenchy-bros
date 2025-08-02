// Funções de navegação
class NavigationManager {
    constructor() {
        this.currentSection = 'home';
    }

    showSection(sectionName) {
        // Esconder todas as seções
        document.querySelectorAll('.section').forEach(section => {
            section.classList.remove('active');
        });
        
        // Mostrar seção selecionada
        document.getElementById(sectionName).classList.add('active');
        
        // Atualizar navegação
        document.querySelectorAll('.nav-link').forEach(link => {
            link.classList.remove('active');
        });
        
        // Marcar link ativo (se o evento existir)
        if (event && event.target) {
            event.target.classList.add('active');
        }
        
        this.currentSection = sectionName;

        // Carregar dados específicos da seção
        if (sectionName === 'admin') {
            this.loadAdminDashboard();
        } else if (sectionName === 'cart') {
            cartManager.loadCart();
        }
    }

    loadAdminDashboard() {
        // Implementar painel administrativo
        console.log('Carregando painel administrativo...');
    }
}

// Criar instância global
const navigationManager = new NavigationManager();

// Função global para compatibilidade
function showSection(sectionName) {
    navigationManager.showSection(sectionName);
}