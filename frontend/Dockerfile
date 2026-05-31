# ==========================================
# AutoChat Pro - Frontend Dockerfile
# ==========================================

FROM node:20-alpine AS builder

WORKDIR /app

# Copiar package files
COPY package.json package-lock.json* ./

# Instalar dependências
RUN npm install

# Copiar código
COPY . .

# Build da aplicação
RUN npm run build

# Imagem de produção
FROM nginx:alpine

# Copiar build para o nginx
COPY --from=builder /app/dist /usr/share/nginx/html

# Copiar configuração do nginx
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
