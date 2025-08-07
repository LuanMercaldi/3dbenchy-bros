# Instruções de Deploy - 3DBenchy Bros Backend

## ✅ Código Corrigido e Pronto para Deploy

O código backend foi auditado e corrigido com sucesso. Todas as configurações estão prontas para deploy no Render.com.

## 🔧 Correções Realizadas

- ✅ Removido código duplicado no `app.py`
- ✅ Corrigida variável `debug` não definida
- ✅ Adicionado import `request` necessário
- ✅ Limpas dependências duplicadas no `requirements.txt`
- ✅ Removido `package.json` desnecessário (projeto é Python)
- ✅ Atualizado CORS para incluir `https://luanmercaldi.github.io`

## 🚀 Deploy Manual no Render.com

### Passo 1: Criar Conta no Render
1. Acesse https://render.com
2. Clique em "Get Started for Free"
3. Faça login via GitHub (recomendado)

### Passo 2: Criar Banco de Dados PostgreSQL
1. No dashboard do Render, clique em "New +"
2. Selecione "PostgreSQL"
3. Configure:
   - **Name**: `3dbenchy-bros-db`
   - **Database Name**: `3dbenchy_db`
   - **User**: `3dbenchy_user`
   - **Plan**: Free
4. Clique em "Create Database"
5. **IMPORTANTE**: Copie a "Internal Connection String" que será gerada

### Passo 3: Criar Web Service (Backend)
1. No dashboard, clique em "New +"
2. Selecione "Web Service"
3. Conecte ao repositório `LuanMercaldi/3dbenchy-bros`
4. Configure:
   - **Name**: `3dbenchy-bros-api`
   - **Root Directory**: `backend`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn --bind 0.0.0.0:$PORT app:app`
   - **Instance Type**: Free

### Passo 4: Configurar Variáveis de Ambiente
Na seção "Environment Variables", adicione:

```
DATABASE_URL = [Cole aqui a Internal Connection String do banco]
FLASK_ENV = production
JWT_SECRET_KEY = [Gere uma chave secura aleatória]
SECRET_KEY = [Gere uma chave secura aleatória]
```

**Para gerar chaves seguras**, use:
```python
import secrets
print(secrets.token_urlsafe(32))
```

### Passo 5: Deploy
1. Clique em "Create Web Service"
2. Aguarde o build e deploy (pode levar alguns minutos)
3. Monitore os logs para verificar se tudo está funcionando

## 🔗 URLs Importantes

Após o deploy bem-sucedido:
- **API URL**: `https://3dbenchy-bros-api.onrender.com`
- **Health Check**: `https://3dbenchy-bros-api.onrender.com/health`
- **API Documentation**: `https://3dbenchy-bros-api.onrender.com/`

## 🔄 Próximo Passo

Após o deploy do backend, você precisará atualizar a URL da API no frontend:
1. Edite o arquivo `frontend/config.js` ou `frontend/script.js`
2. Substitua a URL da API pela nova URL do Render
3. Faça commit e push das alterações

## 🆘 Troubleshooting

### Se o deploy falhar:
1. Verifique os logs no dashboard do Render
2. Confirme que todas as variáveis de ambiente estão configuradas
3. Verifique se a Internal Connection String do banco está correta

### Se a API não responder:
1. Acesse `/health` para verificar o status
2. Verifique se o banco de dados está funcionando
3. Confirme que o CORS está configurado corretamente

## 📞 Suporte

Se encontrar problemas, verifique:
- Logs do serviço no dashboard do Render
- Status do banco de dados
- Configuração das variáveis de ambiente

