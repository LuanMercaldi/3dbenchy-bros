// Melhorias de acessibilidade
class AccessibilityManager {
    constructor() {
        this.init();
    }

    init() {
        this.setupKeyboardNavigation();
        this.setupFocusManagement();
        this.setupScreenReaderSupport();
    }

    setupKeyboardNavigation() {
        // Navegação por Tab e Enter
        document.addEventListener('keydown', (event) => {
            // Fechar modal com Escape
            if (event.key === 'Escape') {
                const modal = document.getElementById('loginModal');
                if (modal && modal.style.display === 'block') {
                    authManager.closeModal();
                }
            }

            // Ativar botões com Enter ou Space
            if (event.key === 'Enter' || event.key === ' ') {
                const target = event.target;
                if (target.classList.contains('nav-link')) {
                    event.preventDefault();
                    target.click();
                }
            }
        });
    }

    setupFocusManagement() {
        // Gerenciar foco em modais
        const modal = document.getElementById('loginModal');
        if (modal) {
            modal.addEventListener('show', () => {
                const firstButton = modal.querySelector('button');
                if (firstButton) {
                    firstButton.focus();
                }
            });
        }
    }

    setupScreenReaderSupport() {
        // Anunciar mudanças de seção para leitores de tela
        const originalShowSection = navigationManager.showSection;
        navigationManager.showSection = function(sectionName) {
            originalShowSection.call(this, sectionName);
            
            // Anunciar mudança para leitores de tela
            const announcement = document.createElement('div');
            announcement.setAttribute('aria-live', 'polite');
            announcement.setAttribute('aria-atomic', 'true');
            announcement.className = 'sr-only';
            announcement.textContent = `Navegou para a seção ${sectionName}`;
            
            document.body.appendChild(announcement);
            
            // Remover após anúncio
            setTimeout(() => {
                document.body.removeChild(announcement);
            }, 1000);
        };
    }
}

// Inicializar gerenciador de acessibilidade
const accessibilityManager = new AccessibilityManager();