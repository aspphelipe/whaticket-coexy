import { Module } from '@nestjs/common';
import { WebhookCoexyService } from './webhook-coexy.service';
import { WebhookCoexyController } from './webhook-coexy.controller';
import { PrismaService } from 'src/@core/infra/database/prisma.service';
import { RabbitMQService } from 'src/@core/infra/rabbitmq/RabbitMq.service';
import { SocketService } from 'src/@core/infra/socket/socket.service';

@Module({
  controllers: [WebhookCoexyController],
  providers: [
    WebhookCoexyService,
    PrismaService,
    RabbitMQService,
    SocketService,
  ],
  exports: [WebhookCoexyService],
})
export class WebhookCoexyModule {}
