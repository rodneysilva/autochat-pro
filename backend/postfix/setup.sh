#!/bin/bash
# Setup script for Postfix with DKIM

set -e

echo "=== Configurando Postfix para rodney.website ==="

# Gerar certificado SSL auto-assinado
if [ ! -f /etc/ssl/certs/postfix.pem ]; then
    echo "Gerando certificado SSL..."
    openssl req -new -x509 -days 365 -nodes \
        -out /etc/ssl/certs/postfix.pem \
        -keyout /etc/ssl/private/postfix.key \
        -subj "/C=BR/ST=SP/L=SP/O=AutoChat/CN=mail.rodney.website"
    chmod 600 /etc/ssl/private/postfix.key
fi

# Configurar permissões
chown -R postfix:postfix /var/spool/postfix
postfix postmap /etc/postfix/aliases 2>/dev/null || true

# Processar sasl_passwd se existir
if [ -f /etc/postfix/sasl_passwd ] && [ -s /etc/postfix/sasl_passwd ]; then
    postmap /etc/postfix/sasl_passwd
    chmod 600 /etc/postfix/sasl_passwd*
fi

echo "=== Configuração concluída ==="
echo "=== DKIM Setup ==="
echo "DKIM needs to be configured via OpenDKIM"
echo "Add these DNS records to Cloudflare:"
echo ""
echo "SPF (TXT): v=spf1 mx a ip4:SEU_IP -all"
echo ""
echo "DKIM (TXT) para selector default._domainkey:"
echo "(Obter a chave pública após gerar com opendkim-genkey)"
echo ""
echo "=== Iniciando Postfix ==="

# Iniciar Postfix
exec /usr/sbin/postfix start-fg
