import { Module } from '@nestjs/common';
import { TypeOrmModule } from '@nestjs/typeorm';
import { AuthCodeController } from './auth-code.controller';
import { AuthCodeService } from './auth-code.service';
import { AuthCode } from '../../entities/auth-code.entity';
import { Agent } from '../../entities/agent.entity';

@Module({
  imports: [TypeOrmModule.forFeature([AuthCode, Agent])],
  controllers: [AuthCodeController],
  providers: [AuthCodeService],
})
export class AuthCodeModule {}
