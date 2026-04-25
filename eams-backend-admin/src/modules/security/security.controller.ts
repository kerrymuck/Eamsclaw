import { Controller, Get, Put, Body, Query } from '@nestjs/common';
import { ApiTags, ApiOperation } from '@nestjs/swagger';
import { SecurityService } from './security.service';

@ApiTags('安全管理')
@Controller('security')
export class SecurityController {
  constructor(private readonly securityService: SecurityService) {}

  @Get('logs')
  @ApiOperation({ summary: '获取操作日志' })
  async getLogs(
    @Query('page') page: number = 1,
    @Query('pageSize') pageSize: number = 10,
  ) {
    return this.securityService.getLogs(page, pageSize);
  }

  @Get('ecode-rules')
  @ApiOperation({ summary: '获取Ecode规则' })
  async getEcodeRules() {
    return this.securityService.getEcodeRules();
  }

  @Put('ecode-rules')
  @ApiOperation({ summary: '更新Ecode规则' })
  async updateEcodeRules(@Body() rules: any) {
    return this.securityService.updateEcodeRules(rules);
  }
}
