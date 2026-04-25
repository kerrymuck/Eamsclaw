import { Injectable, NotFoundException } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository, Like } from 'typeorm';
import { Agent } from '../../entities/agent.entity';
import { AgentLevel } from '../../entities/agent-level.entity';
import { CreateAgentDto, UpdateAgentDto } from '../../dtos/agent.dto';

@Injectable()
export class AgentService {
  constructor(
    @InjectRepository(Agent)
    private agentRepository: Repository<Agent>,
    @InjectRepository(AgentLevel)
    private agentLevelRepository: Repository<AgentLevel>,
  ) {}

  async findAll(params: {
    page: number;
    pageSize: number;
    keyword?: string;
    status?: number;
  }) {
    const { page, pageSize, keyword, status } = params;
    const where: any = {};

    if (keyword) {
      where.name = Like(`%${keyword}%`);
    }
    if (status !== undefined) {
      where.status = status;
    }

    const [list, total] = await this.agentRepository.findAndCount({
      where,
      relations: ['level'],
      skip: (page - 1) * pageSize,
      take: pageSize,
      order: { createdAt: 'DESC' },
    });

    return {
      list,
      total,
      page,
      pageSize,
    };
  }

  async findOne(id: number) {
    const agent = await this.agentRepository.findOne({
      where: { id },
      relations: ['level'],
    });

    if (!agent) {
      throw new NotFoundException('服务商不存在');
    }

    return agent;
  }

  async create(createAgentDto: CreateAgentDto) {
    // 生成服务商编码
    const agentCode = await this.generateAgentCode();

    const agent = this.agentRepository.create({
      ...createAgentDto,
      agentCode,
      status: 2, // 待审核状态
    });

    return this.agentRepository.save(agent);
  }

  async update(id: number, updateAgentDto: UpdateAgentDto) {
    const agent = await this.findOne(id);
    Object.assign(agent, updateAgentDto);
    return this.agentRepository.save(agent);
  }

  async updateStatus(id: number, status: number) {
    const agent = await this.findOne(id);
    agent.status = status;
    return this.agentRepository.save(agent);
  }

  async recharge(id: number, amount: number, remark?: string) {
    const agent = await this.findOne(id);
    agent.balance = parseFloat(agent.balance.toString()) + amount;
    // TODO: 记录财务流水
    return this.agentRepository.save(agent);
  }

  private async generateAgentCode(): Promise<string> {
    const prefix = 'AGT';
    const count = await this.agentRepository.count();
    const sequence = (count + 1).toString().padStart(3, '0');
    return `${prefix}${sequence}`;
  }
}
