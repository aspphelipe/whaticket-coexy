import {
  Controller,
  Post,
  Body,
  Param,
  UseInterceptors,
  UploadedFile,
} from '@nestjs/common';
import { SendMessageCoexyService } from './send-message-coexy.service';
import { ApiOperation, ApiResponse, ApiTags } from '@nestjs/swagger';
import { FileInterceptor } from '@nestjs/platform-express';
import { Public } from '../../../@core/guard/auth.decorator';

@Controller('v1/send-message-coexy')
@ApiTags('Send Message Coexy')
export class SendMessageCoexyController {
  constructor(private readonly service: SendMessageCoexyService) {}

  @Post(':token')
  @Public()
  @ApiOperation({ summary: 'Send message via Coexy meta-proxy' })
  @ApiResponse({ status: 200, description: 'Message sent successfully' })
  @ApiResponse({ status: 404, description: 'Coexy connection not found' })
  @UseInterceptors(FileInterceptor('file'))
  sendMessage(
    @Param('token') token: string,
    @Body() body: any,
    @UploadedFile() file: Express.Multer.File,
  ) {
    const data = body?.data ?? body?.dados_mensagem ?? body;
    return this.service.createMessage(token, data, file);
  }
}
