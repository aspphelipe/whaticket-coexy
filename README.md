# Whaticket Coexy Module

Módulo plugável que adiciona a [Coexy](https://coexy.com.br) como opção de conexão WhatsApp em sistemas baseados no Whaticket.

A Coexy é um relay transparente para a Meta WhatsApp Cloud API — gerencia tokens automaticamente, simplifica o onboarding via Embedded Signup, e mantém compatibilidade total com o formato de payloads da Meta.

## Funcionalidades

- Novo channel `whatsapp_coexy` no sistema
- Modal de criação de conexão com link de onboarding (connect_url)
- Polling automático de status da conexão
- Envio e recepção de mensagens via Coexy meta-proxy
- Webhook com validação HMAC-SHA256
- Badge "COEXY" roxo na página de conexões
- Scripts de instalação e desinstalação

## Pré-requisitos

- Sistema Whaticket funcionando (backend + api_oficial + frontend)
- Conta na [Coexy](https://coexy.com.br) com API Key
- Node.js, PM2, PostgreSQL configurados

## Instalação

```bash
# 1. Clone o repositório
git clone https://github.com/aspphelipe/whaticket-coexy.git
cd whaticket-coexy

# 2. Execute o instalador (na VPS onde o Whaticket está instalado)
bash install.sh
```

O instalador vai:
1. Detectar o diretório do Whaticket (padrão: `/home/deploy/empresa01`)
2. Criar backup dos arquivos que serão modificados
3. Copiar os arquivos do módulo
4. Aplicar as modificações necessárias nos arquivos existentes
5. Rodar as migrations do banco de dados
6. Rebuildar o frontend
7. Reiniciar os serviços via PM2

## Configuração

Após a instalação, configure as variáveis de ambiente:

```bash
# No .env do backend e/ou api_oficial
COEXY_API_KEY=crt_pk_sua_api_key_aqui
COEXY_HMAC_SECRET=seu_hmac_secret_aqui
```

- **COEXY_API_KEY**: Encontrada em Coexy Dashboard > Configurações > API Keys
- **COEXY_HMAC_SECRET**: Retornado ao criar o webhook na Coexy (salve imediatamente, não é recuperável)

Reinicie os serviços após configurar:

```bash
pm2 restart all
```

## Uso

1. Acesse o painel do Whaticket > Conexões
2. Clique no botão **"+ Coexy"**
3. Informe um nome para a conexão e selecione as filas
4. O sistema gera um **link de conexão** (connect_url)
5. Compartilhe o link com o dono do número WhatsApp
6. O dono acessa o link e autoriza via Meta Embedded Signup
7. A conexão fica ativa automaticamente

## Desinstalação

```bash
bash uninstall.sh
```

O desinstalador restaura os backups criados na instalação. As migrations do banco NÃO são revertidas automaticamente.

## Estrutura do Módulo

```
whaticket-coexy/
├── install.sh                          # Instalador
├── uninstall.sh                        # Desinstalador
├── backend/
│   ├── src/libs/coexy/                 # Client HTTP para API Coexy
│   ├── src/services/CoexyServices/     # Services de sessão e envio
│   └── src/database/migrations/        # Migration Sequelize
├── api_oficial/
│   ├── src/resources/v1/webhook-coexy/ # Receptor de webhooks
│   ├── src/resources/v1/send-message-coexy/ # Envio via meta-proxy
│   └── prisma/migrations/             # Migration Prisma
└── frontend/
    └── src/components/
        ├── CoexyModal/                 # Modal de criação
        └── CoexyStatusModal/           # Modal de status/polling
```

## Arquitetura

```
Envio:  Frontend → Backend → api_oficial → Coexy meta-proxy → Meta → WhatsApp
Recepção: WhatsApp → Meta → Coexy → webhook api_oficial → RabbitMQ → Backend → Frontend
```

- Os payloads são idênticos ao Meta Cloud API
- Um webhook global recebe todos os eventos e roteia por `phone_number_id`
- Tokens são gerenciados automaticamente pela Coexy

## Licença

MIT
