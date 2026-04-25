import { Module } from '@nestjs/common';
import { TypeOrmModule } from '@nestjs/typeorm';
import { DashboardController } from './dashboard.controller';
import { DashboardService } from './dashboard.service';
import { Agent } from '../../entities/agent.entity';
import { AuthCode } from '../../entities/auth-code.entity';

@Module({
  imports: [TypeOrmModule.forFeature([Agent, AuthCode])],
  controllers: [DashboardController],
  providers: [DashboardService],
})
export class DashboardModule {}
