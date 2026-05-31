# Configuração DNS para Email (rodney.website)

## Registros DNS necessários no Cloudflare

Adicione os seguintes registros na zona `rodney.website`:

### 1. Registro A para mail
```
Tipo: A
Nome: mail
Endereço IPv4: SEU_IP_PUBLICO
Proxy: Desativado (DNS only)
TTL: Auto
```

### 2. Registro MX
```
Tipo: MX
Nome: rodney.website
Servidor: mail.rodney.website
Prioridade: 10
Proxy: Desativado
```

### 3. Registro TXT - SPF
```
Tipo: TXT
Nome: rodney.website
Conteúdo: v=spf1 mx a ip4:SEU_IP_PUBLICO -all
Proxy: Desativado
```

### 4. Registro TXT - DKIM
```
Tipo: TXT
Nome: default._domainkey
Conteúdo: (Gerar chave DKIM - ver abaixo)
Proxy: Desativado
```

## Gerar chave DKIM

Dentro do container Postfix:

```bash
# Entrar no container
docker exec -it autochat-postfix bash

# Gerar chaves DKIM
opendkim-genkey -s default -d rodney.website

# A chave pública está em default.txt
cat /etc/opendkim/keys/default.txt
```

Copie o conteúdo do arquivo `default.txt` e adicione como registro TXT DKIM acima.

## Verificar configuração

Após configurar os registros DNS (pode levar até 24h para propagar):

```bash
# Verificar SPF
dig rodney.website TXT

# Verificar MX
dig rodney.website MX

# Verificar DKIM
dig default._domainkey.rodney.website TXT
```

## Testar envio de email

```bash
# Dentro do container backend
docker exec -it autochat-backend bash

# Teste Python
python -c "
import smtplib
from email.message import EmailMessage

msg = EmailMessage()
msg['From'] = 'noreply@rodney.website'
msg['To'] = 'seu@email.com'
msg['Subject'] = 'Teste SMTP'
msg.set_content('Funcionou!')

server = smtplib('postfix', 25)
server.send_message(msg)
print('Email enviado!')
"
```

## Solução de problemas

### Emails não chegam
1. Verifique se a porta 25 está aberta no firewall
2. Verifique os registros DNS com `dig`
3. Verifique logs: `docker logs autochat-postfix`

### Gmail/Gsuite não aceita
- Use IP público com boa reputação
- Configure DKIM corretamente
- Configure DMARC: `_dmarc.rodney.website` TXT: `v=DMARC1; p=none`

### Porta 25 bloqueada pelo provedor
- Muitos VPS bloqueiam porta 25
- Considere usar relay SMTP externo (SendGrid, SMTP2GO)
