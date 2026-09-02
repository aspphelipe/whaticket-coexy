import { Injectable, Logger } from '@nestjs/common';
import { PrismaService } from 'src/@core/infra/database/prisma.service';
import { RabbitMQService } from 'src/@core/infra/rabbitmq/RabbitMq.service';
import { SocketService } from 'src/@core/infra/socket/socket.service';
import * as crypto from 'crypto';

@Injectable()
export class WebhookCoexyService {
  private logger: Logger = new Logger(WebhookCoexyService.name);

  constructor(
    private readonly prisma: PrismaService,
    private readonly rabbit: RabbitMQService,
    private readonly socket: SocketService,
  ) {}

  verifySignature(rawBody: string, signatureHeader: string): boolean {
    const hmacSecret = process.env.COEXY_HMAC_SECRET;
    if (!hmacSecret) {
      this.logger.error('COEXY_HMAC_SECRET not configured');
      return false;
    }

    if (!signatureHeader || !signatureHeader.startsWith('sha256=')) {
      return false;
    }

    const expectedHex = signatureHeader.slice(7);
    const computed = crypto
      .createHmac('sha256', hmacSecret)
      .update(rawBody)
      .digest('hex');

    return crypto.timingSafeEqual(
      Buffer.from(computed, 'hex'),
      Buffer.from(expectedHex, 'hex'),
    );
  }

  async processWebhook(data: any): Promise<boolean> {
    try {
      const entries = data?.entry ?? [];

      for (const entry of entries) {
        const changes = entry?.changes ?? [];

        for (const change of changes) {
          const value = change?.value;
          if (!value) continue;

          const phoneNumberId = value?.metadata?.phone_number_id;
          if (!phoneNumberId) {
            this.logger.warn('Webhook without phone_number_id, skipping');
            continue;
          }

          const connection = await this.prisma.coexyConnection.findUnique({
            where: { phone_number_id: phoneNumberId },
          });

          if (!connection) {
            this.logger.warn(
              `No coexy connection found for phone_number_id: ${phoneNumberId}`,
            );
            continue;
          }

          const company = await this.prisma.company.findFirst({
            where: { id: connection.companyId },
          });

          if (!company) {
            this.logger.warn(
              `Company not found for coexy connection: ${connection.id}`,
            );
            continue;
          }

          const messages = value?.messages ?? [];
          const statuses = value?.statuses ?? [];

          if (messages.length > 0 || statuses.length > 0) {
            const payload = {
              type: 'coexy_webhook',
              companyId: connection.companyId,
              whatsappId: connection.whatsappId,
              token_mult100: connection.token_mult100,
              phone_number_id: phoneNumberId,
              data: value,
            };

            if (connection.use_rabbitmq) {
              await this.rabbit.publish(
                `wpp_oficial_${company.idEmpresaMult100}`,
                JSON.stringify(payload),
              );
            }

            this.socket.sendMessage(payload as any);
          }
        }
      }

      return true;
    } catch (error: any) {
      this.logger.error(`processWebhook error: ${error.message}`, error.stack);
      return false;
    }
  }
}
