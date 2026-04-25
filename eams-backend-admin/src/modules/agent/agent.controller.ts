import {
  Controller,
  Get,
  Post,
  Put,
  Patch,
  Body,
  Param,
  Query,
  ParseIntPipe,
} from '@nestjs/common';
import { ApiTags, ApiOperation } from '@nestjs/swagger';
import { AgentService } from './agent.service';
import { CreateAgentDto, UpdateAgentDto } from '../../dtos/agent.dto';

@ApiTags('服务商管理')
@Controller('agents')
export class AgentController {
  constructor(private readonly agentService: AgentService) {}

  @Get()
  @ApiOperation({ summary: '获取服务商列表' })
  async findAll(
    @Query('page') page: number = 1,
    @Query('pageSize') pageSize: number = 10,
    @Query('keyword') keyword?: string,
    @Query('status') status?: number,
  ) {
    return this.agentService.findAll({ page, pageSize, keyword, status });
  }

  @Get(':id')
  @ApiOperation({ summary: '获取服务商详情' })
  async findOne(@Param('id', ParseIntPipe) id: number) {
    return this.agentService.findOne(id);
  }

  @Post()
  @ApiOperation({ summary: '创建服务商' })
  async create(@Body() createAgentDto: CreateAgentDto) {
    return this.agentService.create(createAgentDto);
  }

  @Put(':id')
  @ApiOperation({ summary: '更新服务商' })
  async update(
    @Param('id', ParseIntPipe) id: number,
    @Body() updateAgentDto: UpdateAgentDto,
  ) {
    return this.agentService.update(id, updateAgentDto);
  }

  @Patch(':id/status')
  @ApiOperation({ summary: '修改服务商状态' })
  async updateStatus(
    @Param('id', ParseIntPipe) id: number,
    @Body('status') status: number,
  ) {
    return this.agentService.updateStatus(id, status);
  }

  @Post(':id/recharge')
  @ApiOperation({ summary: '服务商充值' })
  async recharge(
    @Param('id', ParseIntPipe) id: number,
    @Body('amount') amount: number,
    @Body('remark') remark?: string,
  ) {
    return this.agentService.recharge(id, amount, remark);
  }
}
