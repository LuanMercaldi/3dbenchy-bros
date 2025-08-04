# 3DBenchy Bros - E-commerce de Modelos 3D

![3DBenchy Bros Logo](logo.png)

> E-commerce de produtos de impressão 3D com design único inspirado nos jogos retrô dos anos 80.

## 🎮 Sobre o Projeto

O 3DBenchy Bros é uma plataforma de e-commerce especializada em modelos 3D para impressão, oferecendo uma experiência única com estética pixelizada dos anos 80. O projeto combina tecnologia moderna com design nostálgico para criar uma experiência de compra memorável.

### ✨ Características Principais

- **Design Retrô**: Interface pixelizada inspirada nos anos 80
- **Cores Neon**: Paleta vibrante com ciano, magenta, verde e amarelo
- **E-commerce Completo**: Sistema de produtos, carrinho e autenticação
- **Responsivo**: Funciona perfeitamente em desktop, tablet e mobile
- **Seguro**: Implementação robusta de segurança web
- **API RESTful**: Backend moderno com documentação completa

## 🚀 Tecnologias Utilizadas

### Frontend
- **HTML5**: Estrutura semântica moderna
- **CSS3**: Animações e efeitos visuais avançados
- **JavaScript ES6+**: Funcionalidades interativas
- **Responsive Design**: Compatível com todos os dispositivos

### Backend
- **Python 3.11+**: Linguagem principal
- **Flask**: Framework web minimalista e poderoso
- **SQLite**: Banco de dados para desenvolvimento
- **JWT**: Autenticação segura com tokens
- **bcrypt**: Hash seguro de senhas

### Segurança
- **Content Security Policy (CSP)**: Proteção contra XSS
- **Rate Limiting**: Proteção contra ataques de força bruta
- **Validação Robusta**: Sanitização de dados de entrada
- **Headers de Segurança**: Proteção abrangente

## 🚀 Deploy

Este projeto está configurado para deploy automático:

- **Frontend**: GitHub Pages
- **Backend**: Render.com
- **Base de Dados**: PostgreSQL (Render.com)

### Deploy do Frontend

O frontend é automaticamente deployado via GitHub Pages sempre que há push para a branch main.

### Deploy do Backend

O backend é deployado no Render.com com as seguintes variáveis de ambiente:
- `DATABASE_URL`: URL da base de dados PostgreSQL
- `JWT_SECRET_KEY`: Chave secreta para tokens JWT
- `SECRET_KEY`: Chave secreta da aplicação Flask
