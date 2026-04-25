import { Module } from '@nestjs/common';
import { TypeOrmModule } from '@nestjs/typeorm';
import { AgentController } from './agent.controller';
import { AgentService } from './agent.service';
import { Agent } from '../../entities/agent.entity';
import { AgentLevel } from '../../entities/agent-level.entity';

@Module({
  imports: [TypeOrmModule.forFeature([Agent, AgentLevel])],
  controllers: [AgentController],
  providers: [AgentService],
  exports: [AgentService],
})
export class AgentModule {}
