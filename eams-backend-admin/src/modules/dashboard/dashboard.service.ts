import { Injectable } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository } from 'typeorm';
import { Agent } from '../../entities/agent.entity';
import { AuthCode } from '../../entities/auth-code.entity';

@Injectable()
export class DashboardService {
  constructor(
    @InjectRepository(Agent)
    private agentRepository: Repository<Agent>,
    @InjectRepository(AuthCode)
    private authCodeRepository: Repository<AuthCode>,
  ) {}

  async getStatistics() {
    const totalAgents = await this.agentRepository.count();
    const totalAuthCodes = await this.authCodeRepository.count();
    const activatedAuthCodes = await this.authCodeRepository.count({
      where: { status: 1 },
    });

    // TODO: 从财务模块获取今日充值金额
    const todayRecharge = 12500;

    return {
      totalAgents,
      totalAuthCodes,
      activatedAuthCodes,
      todayRecharge,
    };
  }

  async getTrends(days: number) {
    // TODO: 实现趋势数据查询
    return {
      activationTrend: [],
      newAgents: [],
      newAuthCodes: [],
    };
  }
}
