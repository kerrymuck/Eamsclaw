import { Controller, Get, Put, Body, Param } from '@nestjs/common';
import { ApiTags, ApiOperation } from '@nestjs/swagger';
import { SystemService } from './system.service';

@ApiTags('系统设置')
@Controller('settings')
export class SystemController {
  constructor(private readonly systemService: SystemService) {}

  @Get()
  @ApiOperation({ summary: '获取所有配置' })
  async findAll() {
    return this.systemService.findAll();
  }

  @Get(':key')
  @ApiOperation({ summary: '获取单个配置' })
  async findOne(@Param('key') key: string) {
    return this.systemService.findOne(key);
  }

  @Put(':key')
  @ApiOperation({ summary: '更新配置' })
  async update(@Param('key') key: string, @Body('value') value: string) {
    return this.systemService.update(key, value);
  }

  @Get('version/info')
  @ApiOperation({ summary: '获取版本信息' })
  async getVersion() {
    return this.systemService.getVersion();
  }
}
