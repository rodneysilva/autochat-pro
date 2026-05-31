FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

# Instalar Postfix e dependências
RUN apt-get update && apt-get install -y \
    postfix \
    opendkim \
    opendkim-tools \
    mailutils \
    openssl \
    rsyslog \
    && rm -rf /var/lib/apt/lists/*

# Criar diretórios necessários
RUN mkdir -p /var/spool/postfix /var/spool/postfix/pid /var/run/opendkim

# Copiar configurações
COPY main.cf /etc/postfix/main.cf
COPY aliases /etc/postfix/aliases
COPY setup.sh /usr/local/bin/setup.sh
COPY sasl_passwd /etc/postfix/sasl_passwd 2>/dev/null || true

RUN chmod +x /usr/local/bin/setup.sh

# Expor porta SMTP
EXPOSE 25 587

# Executar setup e iniciar
CMD ["/usr/local/bin/setup.sh"]
