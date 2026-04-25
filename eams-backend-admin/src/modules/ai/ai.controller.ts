import { Controller, Get, Post, Put, Patch, Body, Param, Query } from '@nestjs/common';
import { ApiTags, ApiOperation } from '@nestjs/swagger';
import { AiService } from './ai.service';

@ApiTags('AI算力管理')
@Controller('ai-models')
export class AiController {
  constructor(private readonly aiService: AiService) {}

  @Get()
  @ApiOperation({ summary: '获取AI模型列表' })
  async findAll() {
    return this.aiService.findAll();
  }

  @Post()
  @ApiOperation({ summary: '新增AI模型' })
  async create(@Body() data: any) {
    return this.aiService.create(data);
  }

  @Put(':id')
  @ApiOperation({ summary: '更新AI模型' })
  async update(@Param('id') id: number, @Body() data: any) {
    return this.aiService.update(id, data);
  }

  @Patch(':id/status')
  @ApiOperation({ summary: '修改模型状态' })
  async updateStatus(@Param('id') id: number, @Body('status') status: number) {
    return this.aiService.updateStatus(id, status);
  }

  @Put(':id/pricing')
  @ApiOperation({ summary: '更新模型定价' })
  async updatePricing(@Param('id') id: number, @Body() pricing: any) {
    return this.aiService.updatePricing(id, pricing);
  }
}
