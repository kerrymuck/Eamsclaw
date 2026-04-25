import { Controller, Get, Post, Body, Query } from '@nestjs/common';
import { ApiTags, ApiOperation } from '@nestjs/swagger';
import { FinanceService } from './finance.service';

@ApiTags('财务管理')
@Controller('finance')
export class FinanceController {
  constructor(private readonly financeService: FinanceService) {}

  @Get('records')
  @ApiOperation({ summary: '获取收支明细' })
  async getRecords(
    @Query('page') page: number = 1,
    @Query('pageSize') pageSize: number = 10,
  ) {
    return this.financeService.getRecords(page, pageSize);
  }

  @Get('recharges')
  @ApiOperation({ summary: '获取充值明细' })
  async getRecharges(
    @Query('page') page: number = 1,
    @Query('pageSize') pageSize: number = 10,
  ) {
    return this.financeService.getRecharges(page, pageSize);
  }

  @Post('recharges')
  @ApiOperation({ summary: '创建充值订单' })
  async createRecharge(@Body() data: any) {
    return this.financeService.createRecharge(data);
  }
}
