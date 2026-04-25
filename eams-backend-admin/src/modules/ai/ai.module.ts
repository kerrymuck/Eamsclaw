import { Module } from '@nestjs/common';
import { TypeOrmModule } from '@nestjs/typeorm';
import { AiController } from './ai.controller';
import { AiService } from './ai.service';
import { AiModel } from '../../entities/ai-model.entity';

@Module({
  imports: [TypeOrmModule.forFeature([AiModel])],
  controllers: [AiController],
  providers: [AiService],
})
export class AiModule {}
