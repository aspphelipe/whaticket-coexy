import {
  Controller,
  Post,
  Body,
  Headers,
  Req,
  HttpCode,
  HttpStatus,
  RawBodyRequest,
} from '@nestjs/common';
import { WebhookCoexyService } from './webhook-coexy.service';
import { ApiOperation, ApiResponse, ApiTags } from '@nestjs/swagger';
import { Public } from '../../../@core/guard/auth.decorator';
import { Request } from 'express';

@Controller('v1/webhook-coexy')
@ApiTags('Webhook Coexy')
export class WebhookCoexyController {
  constructor(private readonly webhookCoexyService: WebhookCoexyService) {}

  @Public()
  @Post()
  @HttpCode(HttpStatus.OK)
  @ApiOperation({ summary: 'Receive Coexy webhook events' })
  @ApiResponse({ status: 200, description: 'Webhook processed' })
  @ApiResponse({ status: 401, description: 'Invalid signature' })
  async handleWebhook(
    @Body() body: any,
    @Headers('x-coexy-signature') signature: string,
    @Req() req: RawBodyRequest<Request>,
  ) {
    const rawBody = req.rawBody?.toString() || JSON.stringify(body);
    const isValid = this.webhookCoexyService.verifySignature(rawBody, signature);

    if (!isValid) {
      return { status: 401, message: 'Invalid signature' };
    }

    this.webhookCoexyService.processWebhook(body).catch((err) => {
      console.error('Coexy webhook processing error:', err);
    });

    return { status: 200, message: 'OK' };
  }
}
