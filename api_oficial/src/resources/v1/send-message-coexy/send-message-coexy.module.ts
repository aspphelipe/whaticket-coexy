import { Module } from '@nestjs/common';
import { SendMessageCoexyService } from './send-message-coexy.service';
import { SendMessageCoexyController } from './send-message-coexy.controller';
import { PrismaService } from 'src/@core/infra/database/prisma.service';

@Module({
  controllers: [SendMessageCoexyController],
  providers: [SendMessageCoexyService, PrismaService],
})
export class SendMessageCoexyModule {}
