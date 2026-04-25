import { Controller, Get, Post, Patch, Body, Param, Query } from '@nestjs/common';
import { ApiTags, ApiOperation } from '@nestjs/swagger';
import { AuthCodeService } from './auth-code.service';
import { GenerateAuthCodeDto } from '../../dtos/auth-code.dto';

@ApiTags('授权码管理')
@Controller('auth-codes')
export class AuthCodeController {
  constructor(private readonly authCodeService: AuthCodeService) {}

  @Get()
  @ApiOperation({ summary: '获取授权码列表' })
  async findAll(
    @Query('page') page: number = 1,
    @Query('pageSize') pageSize: number = 10,
    @Query('status') status?: number,
    @Query('agentId') agentId?: number,
  ) {
    return this.authCodeService.findAll({ page, pageSize, status, agentId });
  }

  @Post('generate')
  @ApiOperation({ summary: '批量生成授权码' })
  async generate(@Body() generateDto: GenerateAuthCodeDto) {
    return this.authCodeService.generate(generateDto);
  }

  @Post('assign')
  @ApiOperation({ summary: '分配授权码给服务商' })
  async assign(
    @Body('code') code: string,
    @Body('agentId') agentId: number,
  ) {
    return this.authCodeService.assign(code, agentId);
  }

  @Patch(':code/status')
  @ApiOperation({ summary: '修改授权码状态' })
  async updateStatus(
    @Param('code') code: string,
    @Body('status') status: number,
  ) {
    return this.authCodeService.updateStatus(code, status);
  }
}
