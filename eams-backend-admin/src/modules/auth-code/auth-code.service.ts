import { Injectable, NotFoundException } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository } from 'typeorm';
import { AuthCode } from '../../entities/auth-code.entity';
import { Agent } from '../../entities/agent.entity';
import { GenerateAuthCodeDto } from '../../dtos/auth-code.dto';
import * as crypto from 'crypto';

@Injectable()
export class AuthCodeService {
  constructor(
    @InjectRepository(AuthCode)
    private authCodeRepository: Repository<AuthCode>,
    @InjectRepository(Agent)
    private agentRepository: Repository<Agent>,
  ) {}

  async findAll(params: {
    page: number;
    pageSize: number;
    status?: number;
    agentId?: number;
  }) {
    const { page, pageSize, status, agentId } = params;
    const where: any = {};

    if (status !== undefined) {
      where.status = status;
    }
    if (agentId !== undefined) {
      where.agentId = agentId;
    }

    const [list, total] = await this.authCodeRepository.findAndCount({
      where,
      relations: ['agent'],
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

  async generate(generateDto: GenerateAuthCodeDto) {
    const { agentId, type, count, validDays } = generateDto;
    const codes: AuthCode[] = [];

    // 获取服务商信息
    let agent: Agent | null = null;
    if (agentId) {
      agent = await this.agentRepository.findOne({ where: { id: agentId } });
    }

    for (let i = 0; i < count; i++) {
      const code = this.generateCode(agent?.agentCode, type);
      const authCode = this.authCodeRepository.create({
        code,
        agentId,
        type,
        status: 0, // 未激活
        validDays,
      });
      codes.push(authCode);
    }

    return this.authCodeRepository.save(codes);
  }

  async assign(code: string, agentId: number) {
    const authCode = await this.authCodeRepository.findOne({
      where: { code },
    });

    if (!authCode) {
      throw new NotFoundException('授权码不存在');
    }

    const agent = await this.agentRepository.findOne({
      where: { id: agentId },
    });

    if (!agent) {
      throw new NotFoundException('服务商不存在');
    }

    authCode.agentId = agentId;
    return this.authCodeRepository.save(authCode);
  }

  async updateStatus(code: string, status: number) {
    const authCode = await this.authCodeRepository.findOne({
      where: { code },
    });

    if (!authCode) {
      throw new NotFoundException('授权码不存在');
    }

    authCode.status = status;
    return this.authCodeRepository.save(authCode);
  }

  private generateCode(agentCode?: string, type?: number): string {
    const prefix = 'EAMS';
    const agentPart = agentCode || 'TEMP';
    const typeMap = { 1: 'STD', 2: 'PRO', 3: 'ENT' };
    const typePart = typeMap[type as keyof typeof typeMap] || 'STD';
    const random = crypto.randomBytes(3).toString('hex').toUpperCase();
    const checksum = crypto.randomBytes(1).toString('hex').toUpperCase().slice(0, 2);
    return `${prefix}-${agentPart}-${typePart}-${random}-${checksum}`;
  }
}
