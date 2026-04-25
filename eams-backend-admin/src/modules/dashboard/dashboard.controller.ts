import { Controller, Get, Query } from '@nestjs/common';
import { ApiTags, ApiOperation } from '@nestjs/swagger';
import { DashboardService } from './dashboard.service';

@ApiTags('数据面板')
@Controller('dashboard')
export class DashboardController {
  constructor(private readonly dashboardService: DashboardService) {}

  @Get('statistics')
  @ApiOperation({ summary: '获取统计数据' })
  async getStatistics() {
    return this.dashboardService.getStatistics();
  }

  @Get('trends')
  @ApiOperation({ summary: '获取趋势数据' })
  async getTrends(@Query('days') days: number = 30) {
    return this.dashboardService.getTrends(days);
  }
}
