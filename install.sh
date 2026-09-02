#!/usr/bin/env bash
# ============================================================
#  Instalador Modulo Coexy v1.0.0
#  Copia arquivos e aplica patches em uma instalacao Whaticket
# ============================================================
set -euo pipefail

# ---- cores ----
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

ok()   { echo -e "${GREEN}[OK]${NC}   $1"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
err()  { echo -e "${RED}[ERR]${NC}  $1"; }
info() { echo -e "${CYAN}[INFO]${NC} $1"; }

# ---- diretorio do modulo (onde esta este script) ----
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# ---- banner ----
echo ""
echo -e "${BOLD}${CYAN}================================================${NC}"
echo -e "${BOLD}${CYAN}   Instalador Modulo Coexy v1.0.0${NC}"
echo -e "${BOLD}${CYAN}================================================${NC}"
echo ""

# ---- diretorio do projeto alvo ----
DEFAULT_DIR="/home/deploy/empresa01"

if [ -n "${1:-}" ]; then
  PROJECT_DIR="$1"
else
  read -rp "Diretorio do projeto Whaticket [$DEFAULT_DIR]: " PROJECT_DIR
  PROJECT_DIR="${PROJECT_DIR:-$DEFAULT_DIR}"
fi

# ---- validar estrutura ----
info "Validando estrutura em ${PROJECT_DIR} ..."

MISSING=0
for subdir in backend api_oficial frontend; do
  if [ ! -d "${PROJECT_DIR}/${subdir}" ]; then
    err "Diretorio nao encontrado: ${PROJECT_DIR}/${subdir}"
    MISSING=1
  fi
done

if [ "$MISSING" -eq 1 ]; then
  err "A estrutura do projeto esta incompleta. Abortando."
  exit 1
fi

ok "Estrutura validada: backend/, api_oficial/, frontend/"

# ---- backup ----
BACKUP_TS="$(date +%Y%m%d_%H%M%S)"
BACKUP_DIR="${PROJECT_DIR}/.coexy_backup_${BACKUP_TS}"
mkdir -p "$BACKUP_DIR"

info "Criando backup em ${BACKUP_DIR} ..."

# Lista de arquivos existentes que serao modificados
PATCH_FILES=(
  "backend/src/models/Whatsapp.ts"
  "backend/src/controllers/MessageController.ts"
  "backend/src/helpers/SetTicketMessagesAsRead.ts"
  "backend/src/queues.ts"
  "backend/src/controllers/WhatsAppController.ts"
  "backend/src/routes/whatsappRoutes.ts"
  "api_oficial/src/app.module.ts"
  "api_oficial/prisma/schema.prisma"
  "frontend/src/pages/Connections/index.js"
)

for f in "${PATCH_FILES[@]}"; do
  SRC="${PROJECT_DIR}/${f}"
  if [ -f "$SRC" ]; then
    DEST_DIR="${BACKUP_DIR}/$(dirname "$f")"
    mkdir -p "$DEST_DIR"
    cp "$SRC" "${DEST_DIR}/$(basename "$f")"
  else
    warn "Arquivo nao encontrado para backup: ${f}"
  fi
done

ok "Backup criado com ${#PATCH_FILES[@]} arquivos"

# ============================================================
#  FASE 1 - Copiar novos arquivos do modulo
# ============================================================
info "Copiando novos arquivos do modulo ..."

# Backend - CoexyServices
mkdir -p "${PROJECT_DIR}/backend/src/services/CoexyServices"
cp -v "${SCRIPT_DIR}/backend/src/services/CoexyServices/"*.ts \
      "${PROJECT_DIR}/backend/src/services/CoexyServices/" 2>/dev/null && \
  ok "CoexyServices copiado" || warn "CoexyServices - nenhum arquivo encontrado no modulo"

# Backend - libs/coexy
mkdir -p "${PROJECT_DIR}/backend/src/libs/coexy"
cp -v "${SCRIPT_DIR}/backend/src/libs/coexy/"*.ts \
      "${PROJECT_DIR}/backend/src/libs/coexy/" 2>/dev/null && \
  ok "libs/coexy copiado" || warn "libs/coexy - nenhum arquivo encontrado no modulo"

# Backend - migration
mkdir -p "${PROJECT_DIR}/backend/src/database/migrations"
if [ -f "${SCRIPT_DIR}/backend/src/database/migrations/20260902000000-add-coexy-fields-to-whatsapp.ts" ]; then
  cp -v "${SCRIPT_DIR}/backend/src/database/migrations/20260902000000-add-coexy-fields-to-whatsapp.ts" \
        "${PROJECT_DIR}/backend/src/database/migrations/"
  ok "Migration copiada"
fi

# API Oficial - webhook-coexy
mkdir -p "${PROJECT_DIR}/api_oficial/src/resources/v1/webhook-coexy"
cp -v "${SCRIPT_DIR}/api_oficial/src/resources/v1/webhook-coexy/"*.ts \
      "${PROJECT_DIR}/api_oficial/src/resources/v1/webhook-coexy/" 2>/dev/null && \
  ok "webhook-coexy copiado" || warn "webhook-coexy - nenhum arquivo encontrado no modulo"

# API Oficial - send-message-coexy
mkdir -p "${PROJECT_DIR}/api_oficial/src/resources/v1/send-message-coexy"
cp -v "${SCRIPT_DIR}/api_oficial/src/resources/v1/send-message-coexy/"*.ts \
      "${PROJECT_DIR}/api_oficial/src/resources/v1/send-message-coexy/" 2>/dev/null && \
  ok "send-message-coexy copiado" || warn "send-message-coexy - nenhum arquivo encontrado no modulo"

# Frontend - CoexyModal
mkdir -p "${PROJECT_DIR}/frontend/src/components/CoexyModal"
cp -v "${SCRIPT_DIR}/frontend/src/components/CoexyModal/"* \
      "${PROJECT_DIR}/frontend/src/components/CoexyModal/" 2>/dev/null && \
  ok "CoexyModal copiado" || warn "CoexyModal - nenhum arquivo encontrado no modulo"

# Frontend - CoexyStatusModal
mkdir -p "${PROJECT_DIR}/frontend/src/components/CoexyStatusModal"
cp -v "${SCRIPT_DIR}/frontend/src/components/CoexyStatusModal/"* \
      "${PROJECT_DIR}/frontend/src/components/CoexyStatusModal/" 2>/dev/null && \
  ok "CoexyStatusModal copiado" || warn "CoexyStatusModal - nenhum arquivo encontrado no modulo"

# ============================================================
#  FASE 2 - Patches com sed (idempotentes)
# ============================================================
info "Aplicando patches ..."

# Funcao auxiliar: aplica sed somente se o marcador nao existir
# Uso: patch_file <arquivo> <grep_check> <sed_command> <descricao>
patch_file() {
  local FILE="$1"
  local GREP_CHECK="$2"
  local SED_CMD="$3"
  local DESC="$4"

  if [ ! -f "$FILE" ]; then
    warn "${DESC} - arquivo nao encontrado: ${FILE}"
    return 0
  fi

  if grep -q "$GREP_CHECK" "$FILE" 2>/dev/null; then
    ok "${DESC} - ja aplicado, pulando"
  else
    if eval "$SED_CMD"; then
      ok "${DESC} - aplicado com sucesso"
    else
      warn "${DESC} - sed falhou, revise manualmente"
    fi
  fi
}

# ---- 2.1  Whatsapp.ts model: adicionar colunas coexy apos officialHealthDetails ----
patch_file \
  "${PROJECT_DIR}/backend/src/models/Whatsapp.ts" \
  "coexy_channel_id" \
  "sed -i '/officialHealthDetails: string;/a\\
\\
  @Column\\
  coexy_channel_id: string;\\
\\
  @Column\\
  coexy_channel_token: string;\\
\\
  @Column(DataType.TEXT)\\
  coexy_connect_url: string;\\
\\
  @Column\\
  coexy_status: string;' '${PROJECT_DIR}/backend/src/models/Whatsapp.ts'" \
  "Whatsapp.ts - colunas coexy"

# ---- 2.2  MessageController.ts: adicionar whatsapp_coexy nos channel checks ----
MC_FILE="${PROJECT_DIR}/backend/src/controllers/MessageController.ts"

# Patch: SetTicketMessagesAsRead channel check
patch_file "$MC_FILE" \
  'whatsapp_coexy.*ticket.channel' \
  "sed -i 's/\[\"whatsapp\", \"whatsapp_oficial\", \"telegram\"\]\.includes(ticket\.channel)/[\"whatsapp\", \"whatsapp_oficial\", \"whatsapp_coexy\", \"telegram\"].includes(ticket.channel)/g' '${MC_FILE}'" \
  "MessageController - channel array includes"

# Patch: adicionar whatsapp_coexy nas comparacoes === whatsapp_oficial
patch_file "$MC_FILE" \
  'whatsapp_coexy' \
  "sed -i 's/ticket\.channel === \"whatsapp_oficial\"/ticket.channel === \"whatsapp_oficial\" || ticket.channel === \"whatsapp_coexy\"/g; s/ticket\.channel == \"whatsapp_oficial\"/ticket.channel == \"whatsapp_oficial\" || ticket.channel == \"whatsapp_coexy\"/g' '${MC_FILE}'" \
  "MessageController - comparacoes canal coexy"

# ---- 2.3  SetTicketMessagesAsRead.ts: adicionar whatsapp_coexy ----
patch_file \
  "${PROJECT_DIR}/backend/src/helpers/SetTicketMessagesAsRead.ts" \
  "whatsapp_coexy" \
  "sed -i 's/ticket\.channel === \"whatsapp_oficial\"/ticket.channel === \"whatsapp_oficial\" || ticket.channel === \"whatsapp_coexy\"/g' '${PROJECT_DIR}/backend/src/helpers/SetTicketMessagesAsRead.ts'" \
  "SetTicketMessagesAsRead - canal coexy"

# ---- 2.4  queues.ts: adicionar whatsapp_coexy ----
patch_file \
  "${PROJECT_DIR}/backend/src/queues.ts" \
  "whatsapp_coexy" \
  "sed -i 's/campaign\.whatsapp\.channel === \"whatsapp_oficial\"/campaign.whatsapp.channel === \"whatsapp_oficial\" || campaign.whatsapp.channel === \"whatsapp_coexy\"/g; s/ticketUpdate\.channel === \"whatsapp_oficial\"/ticketUpdate.channel === \"whatsapp_oficial\" || ticketUpdate.channel === \"whatsapp_coexy\"/g' '${PROJECT_DIR}/backend/src/queues.ts'" \
  "queues.ts - canal coexy"

# ---- 2.5  WhatsAppController.ts: import + coexyStatus + store block ----
WC_FILE="${PROJECT_DIR}/backend/src/controllers/WhatsAppController.ts"

# Adicionar imports (no topo do arquivo, antes do primeiro import existente)
if ! grep -q "StartCoexySession" "$WC_FILE" 2>/dev/null; then
  sed -i '1s/^/import StartCoexySession from "..\/services\/CoexyServices\/StartCoexySession";\nimport { getCoexyChannel } from "..\/libs\/coexy\/coexy.service";\n/' "$WC_FILE"
  ok "WhatsAppController - imports coexy - aplicado com sucesso"
else
  ok "WhatsAppController - imports coexy - ja aplicado, pulando"
fi

# Adicionar funcao coexyStatus (no final, antes do ultimo export)
if ! grep -q "coexyStatus" "$WC_FILE" 2>/dev/null; then
  # Insere a funcao coexyStatus antes da ultima linha (que presumivelmente nao e export default)
  cat >> "$WC_FILE" << 'COEXY_STATUS_EOF'

export const coexyStatus = async (
  req: Request,
  res: Response
): Promise<Response> => {
  const { whatsappId } = req.params;
  const { companyId } = req.user;

  const whatsapp = await Whatsapp.findOne({
    where: { id: whatsappId, companyId }
  });

  if (!whatsapp || !whatsapp.coexy_channel_id) {
    return res.status(404).json({ error: "Conexao Coexy nao encontrada" });
  }

  try {
    const channel = await getCoexyChannel(whatsapp.coexy_channel_id);

    const updates: any = {
      coexy_status: channel.status
    };

    if (channel.phone_number_id && !whatsapp.number) {
      updates.number = channel.display_phone_number?.replace(/\D/g, "");
    }

    await whatsapp.update(updates);

    return res.json({
      coexy_status: channel.status,
      connect_url: whatsapp.coexy_connect_url,
      phone_number_id: channel.phone_number_id,
      display_phone_number: channel.display_phone_number
    });
  } catch (error) {
    return res.status(500).json({ error: "Erro ao consultar status Coexy" });
  }
};
COEXY_STATUS_EOF
  ok "WhatsAppController - coexyStatus adicionado"
else
  ok "WhatsAppController - coexyStatus ja existe, pulando"
fi

warn "WhatsAppController.store: revise manualmente o bloco de inicializacao da sessao Coexy"

# ---- 2.6  whatsappRoutes.ts: adicionar rota coexy-status ----
patch_file \
  "${PROJECT_DIR}/backend/src/routes/whatsappRoutes.ts" \
  "coexy-status" \
  "sed -i '/export default whatsappRoutes/i\\
whatsappRoutes.get(\\
  \"/whatsapp/:whatsappId/coexy-status\",\\
  isAuth,\\
  WhatsAppController.coexyStatus\\
);\\
' '${PROJECT_DIR}/backend/src/routes/whatsappRoutes.ts'" \
  "whatsappRoutes - rota coexy-status"

# ---- 2.7  app.module.ts (api_oficial): adicionar imports coexy ----
AM_FILE="${PROJECT_DIR}/api_oficial/src/app.module.ts"

patch_file "$AM_FILE" \
  "WebhookCoexyModule" \
  "sed -i \"/import.*TemplatesWhatsappModule/a\\
import { WebhookCoexyModule } from './resources/v1/webhook-coexy/webhook-coexy.module';\\
import { SendMessageCoexyModule } from './resources/v1/send-message-coexy/send-message-coexy.module';\" '${AM_FILE}'" \
  "app.module.ts - imports coexy"

# Adicionar modulos no array imports
patch_file "$AM_FILE" \
  "SendMessageCoexyModule" \
  "sed -i '/TemplatesWhatsappModule,/a\\
    WebhookCoexyModule,\\
    SendMessageCoexyModule,' '${AM_FILE}'" \
  "app.module.ts - modulos no array"

# ---- 2.8  schema.prisma: adicionar model coexyConnection ----
patch_file \
  "${PROJECT_DIR}/api_oficial/prisma/schema.prisma" \
  "coexyConnection" \
  "cat >> '${PROJECT_DIR}/api_oficial/prisma/schema.prisma' << 'PRISMA_EOF'

model coexyConnection {
  id               Int       @id @default(autoincrement())
  create_at        DateTime? @default(now())
  update_at        DateTime? @updatedAt()
  deleted_at       DateTime?
  phone_number_id  String    @unique
  channel_token    String
  coexy_channel_id String    @unique
  companyId        Int
  whatsappId       Int
  token_mult100    String    @unique
  use_rabbitmq     Boolean   @default(true)
}
PRISMA_EOF" \
  "schema.prisma - model coexyConnection"

# ---- 2.9  Frontend patches (Connections + Options) via Python ----
info "Aplicando patches frontend (Connections + Options) via patch.py ..."
python3 "${SCRIPT_DIR}/patch.py" "${PROJECT_DIR}" && \
  ok "Frontend patches aplicados" || \
  warn "Frontend patches falharam - execute manualmente: python3 patch.py ${PROJECT_DIR}"

echo ""
info "Patches concluidos."

# ============================================================
#  FASE 3 - Migrations
# ============================================================
echo ""
info "Executando migrations ..."

# Sequelize (backend)
if [ -f "${PROJECT_DIR}/backend/package.json" ]; then
  info "Rodando sequelize db:migrate (backend) ..."
  (cd "${PROJECT_DIR}/backend" && npx sequelize db:migrate 2>&1) && \
    ok "Sequelize migrations executadas" || \
    warn "Sequelize migration falhou - execute manualmente: cd ${PROJECT_DIR}/backend && npx sequelize db:migrate"

  # Seed Coexy settings
  info "Inserindo configuracoes Coexy na tabela Settings ..."
  BACKEND_ENV="${PROJECT_DIR}/backend/.env"
  if [ -f "$BACKEND_ENV" ]; then
    DB_NAME=$(grep -oP 'DB_NAME=\K.*' "$BACKEND_ENV" 2>/dev/null || echo "")
    DB_USER=$(grep -oP 'DB_USER=\K.*' "$BACKEND_ENV" 2>/dev/null || echo "")
    DB_PASS=$(grep -oP 'DB_PASS=\K.*' "$BACKEND_ENV" 2>/dev/null || echo "")
    DB_HOST=$(grep -oP 'DB_HOST=\K.*' "$BACKEND_ENV" 2>/dev/null || echo "localhost")
    DB_PORT=$(grep -oP 'DB_PORT=\K.*' "$BACKEND_ENV" 2>/dev/null || echo "5432")

    if [ -n "$DB_NAME" ] && [ -n "$DB_USER" ]; then
      PGPASSWORD="$DB_PASS" psql -h "$DB_HOST" -p "${DB_PORT:-5432}" -U "$DB_USER" -d "$DB_NAME" -c "
        INSERT INTO \"Settings\" (key, value, \"companyId\", \"createdAt\", \"updatedAt\")
        VALUES ('coexyApiKey', '', 1, NOW(), NOW()),
               ('coexyHmacSecret', '', 1, NOW(), NOW()),
               ('coexyWebhookDomain', '', 1, NOW(), NOW())
        ON CONFLICT DO NOTHING;
      " 2>&1 && ok "Settings Coexy inseridas" || warn "Seed Settings falhou - insira manualmente"
    else
      warn "Variaveis de banco nao encontradas no .env"
    fi
  else
    warn ".env do backend nao encontrado - insira as Settings manualmente"
  fi
fi

# Prisma (api_oficial)
if [ -f "${PROJECT_DIR}/api_oficial/prisma/schema.prisma" ]; then
  info "Rodando prisma migrate deploy (api_oficial) ..."
  (cd "${PROJECT_DIR}/api_oficial" && npx prisma migrate deploy 2>&1) && \
    ok "Prisma migrations executadas" || \
    warn "Prisma migration falhou - execute manualmente: cd ${PROJECT_DIR}/api_oficial && npx prisma migrate deploy"

  info "Gerando Prisma client ..."
  (cd "${PROJECT_DIR}/api_oficial" && npx prisma generate 2>&1) && \
    ok "Prisma client gerado" || \
    warn "Prisma generate falhou - execute manualmente"
fi

# ============================================================
#  FASE 4 - Build Backend + API Oficial + Frontend
# ============================================================
echo ""
info "Compilando backend (TypeScript) ..."
if [ -f "${PROJECT_DIR}/backend/package.json" ]; then
  (cd "${PROJECT_DIR}/backend" && npx tsc 2>&1) && \
    ok "Backend compilado" || \
    warn "Build do backend falhou - execute manualmente: cd ${PROJECT_DIR}/backend && npx tsc"
fi

info "Compilando api_oficial (NestJS) ..."
if [ -f "${PROJECT_DIR}/api_oficial/package.json" ]; then
  (cd "${PROJECT_DIR}/api_oficial" && npm run build 2>&1) && \
    ok "API Oficial compilada" || \
    warn "Build do api_oficial falhou - execute manualmente: cd ${PROJECT_DIR}/api_oficial && npm run build"
fi

info "Reconstruindo frontend ..."
if [ -f "${PROJECT_DIR}/frontend/package.json" ]; then
  (cd "${PROJECT_DIR}/frontend" && npm install --legacy-peer-deps 2>&1 && npm run build 2>&1) && \
    ok "Frontend reconstruido" || \
    warn "Build do frontend falhou - execute manualmente: cd ${PROJECT_DIR}/frontend && npm install --legacy-peer-deps && npm run build"
fi

# ============================================================
#  FASE 5 - Reiniciar PM2
# ============================================================
echo ""
info "Reiniciando servicos via PM2 ..."

if command -v pm2 &>/dev/null; then
  pm2 restart all 2>&1 && ok "PM2 reiniciado" || warn "PM2 restart falhou"
else
  warn "PM2 nao encontrado no PATH - reinicie manualmente"
fi

# ============================================================
#  PRONTO!
# ============================================================
echo ""
echo -e "${BOLD}${GREEN}================================================${NC}"
echo -e "${BOLD}${GREEN}   Modulo Coexy instalado com sucesso!${NC}"
echo -e "${BOLD}${GREEN}================================================${NC}"
echo ""
echo -e "${YELLOW}Proximos passos:${NC}"
echo -e "  1. Acesse o painel > ${CYAN}Configuracoes${NC}"
echo -e "     Preencha os campos ${CYAN}Coexy API Key${NC} e ${CYAN}Coexy HMAC Secret${NC}"
echo ""
echo -e "  2. Reinicie os servicos:"
echo -e "     ${CYAN}pm2 restart all${NC}"
echo ""
echo -e "  3. Acesse ${CYAN}Conexoes${NC} > ${CYAN}Nova Conexao${NC} > ${CYAN}Coexy - API Oficial${NC}"
echo ""
echo -e "  Backup salvo em: ${CYAN}${BACKUP_DIR}${NC}"
echo ""
