import { Injectable, OnModuleInit } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository } from 'typeorm';
import * as bcrypt from 'bcrypt';
import { AdminUser } from './entities/admin-user.entity';
import { AgentLevel } from './entities/agent-level.entity';
import { SystemConfig } from './entities/system-config.entity';

@Injectable()
export class DatabaseSeedService implements OnModuleInit {
  constructor(
    @InjectRepository(AdminUser)
    private adminUserRepository: Repository<AdminUser>,
    @InjectRepository(AgentLevel)
    private agentLevelRepository: Repository<AgentLevel>,
    @InjectRepository(SystemConfig)
    private systemConfigRepository: Repository<SystemConfig>,
  ) {}

  async onModuleInit() {
    await this.seedAdminUser();
    await this.seedAgentLevels();
    await this.seedSystemConfigs();
    console.log('数据库初始化完成');
  }

  // 初始化超级管理员
  private async seedAdminUser() {
    const existingAdmin = await this.adminUserRepository.findOne({
      where: { username: 'admin' },
    });

    if (!existingAdmin) {
      const hashedPassword = await bcrypt.hash('admin123', 10);
      const superAdmin = this.adminUserRepository.create({
        username: 'admin',
        password: hashedPassword,
        nickname: '超级管理员',
        role: 'super',
        permissions: ['*'],
        status: 1,
      });
      await this.adminUserRepository.save(superAdmin);
      console.log('超级管理员已创建: admin / admin123');
    }
  }

  // 初始化服务商等级
  private async seedAgentLevels() {
    const levels = [
      { levelCode: 'NORMAL', levelName: '普通代理', discountRate: 1.0, minDeposit: 0, apiRateLimit: 1000 },
      { levelCode: 'SILVER', levelName: '银牌代理', discountRate: 0.95, minDeposit: 5000, apiRateLimit: 3000 },
      { levelCode: 'GOLD', levelName: '金牌代理', discountRate: 0.9, minDeposit: 20000, apiRateLimit: 10000 },
      { levelCode: 'PLATINUM', levelName: '白金代理', discountRate: 0.85, minDeposit: 50000, apiRateLimit: 50000 },
    ];

    for (const level of levels) {
      const existing = await this.agentLevelRepository.findOne({
        where: { levelCode: level.levelCode },
      });
      if (!existing) {
        await this.agentLevelRepository.save(this.agentLevelRepository.create(level));
      }
    }
    console.log('服务商等级已初始化');
  }

  // 初始化系统配置
  private async seedSystemConfigs() {
    const configs = [
      { configKey: 'system.name', configValue: 'EAMS超级管理后台', configType: 'string', description: '系统名称' },
      { configKey: 'system.version', configValue: '1.0.0', configType: 'string', description: '系统版本' },
      { configKey: 'authCode.prefix', configValue: 'EAMS', configType: 'string', description: '授权码前缀' },
      { configKey: 'authCode.defaultValidDays', configValue: '365', configType: 'number', description: '授权码默认有效期(天)' },
    ];

    for (const config of configs) {
      const existing = await this.systemConfigRepository.findOne({
        where: { configKey: config.configKey },
      });
      if (!existing) {
        await this.systemConfigRepository.save(this.systemConfigRepository.create(config));
      }
    }
    console.log('系统配置已初始化');
  }
}
