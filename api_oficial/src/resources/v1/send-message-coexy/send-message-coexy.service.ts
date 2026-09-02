import { Injectable, Logger } from '@nestjs/common';
import { PrismaService } from 'src/@core/infra/database/prisma.service';
import { AppError } from 'src/@core/infra/errors/app.error';
import axios from 'axios';

const COEXY_PROXY_BASE = 'https://api.coexy.com.br/functions/v1/meta-proxy';

@Injectable()
export class SendMessageCoexyService {
  private logger: Logger = new Logger(SendMessageCoexyService.name);

  constructor(private readonly prisma: PrismaService) {}

  async createMessage(
    token: string,
    data: any,
    file?: Express.Multer.File,
  ): Promise<any> {
    const connection = await this.prisma.coexyConnection.findUnique({
      where: { token_mult100: token },
    });

    if (!connection) {
      throw new AppError('Conexão Coexy não encontrada', 404);
    }

    const { phone_number_id, channel_token } = connection;

    const payload: any = {
      messaging_product: 'whatsapp',
      to: data.to,
      type: data.type || 'text',
    };

    const typeField = data.type || 'text';
    if (data[typeField]) {
      payload[typeField] = data[typeField];
    }

    if (file) {
      this.logger.log(`File upload via Coexy: ${file.originalname}`);
    }

    try {
      const res = await axios.post(
        `${COEXY_PROXY_BASE}/${phone_number_id}/messages`,
        payload,
        {
          headers: {
            Authorization: `Bearer ${channel_token}`,
            'Content-Type': 'application/json',
          },
          timeout: 30000,
        },
      );

      return { meta_response: res.data };
    } catch (error) {
      this.logger.error(
        `sendCoexyMessage error: ${error.response?.data ? JSON.stringify(error.response.data) : error.message}`,
      );
      throw new AppError(
        `Erro ao enviar mensagem via Coexy: ${error.message}`,
        error.response?.status || 500,
      );
    }
  }
}
