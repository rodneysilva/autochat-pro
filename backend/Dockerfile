# ==========================================
# AutoChat Pro - Backend Dockerfile
# ==========================================

FROM python:3.11-slim

WORKDIR /app

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements e instalar dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código da aplicação
COPY . .

# Criar diretório para logs
RUN mkdir -p /app/logs

# Expor porta
EXPOSE 8000

# Comando para executar
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
