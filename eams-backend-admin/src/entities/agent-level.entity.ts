import {
  Entity,
  PrimaryGeneratedColumn,
  Column,
  CreateDateColumn,
  OneToMany,
} from 'typeorm';
import { Agent } from './agent.entity';

@Entity('agent_levels')
export class AgentLevel {
  @PrimaryGeneratedColumn()
  id: number;

  @Column({ name: 'level_code', unique: true, length: 20 })
  levelCode: string;

  @Column({ name: 'level_name', length: 50 })
  levelName: string;

  @Column({ name: 'discount_rate', type: 'decimal', precision: 5, scale: 4, default: 1.0 })
  discountRate: number;

  @Column({ name: 'min_deposit', type: 'decimal', precision: 18, scale: 4, default: 0 })
  minDeposit: number;

  @Column({ name: 'api_rate_limit', default: 1000 })
  apiRateLimit: number;

  @CreateDateColumn({ name: 'created_at' })
  createdAt: Date;

  @OneToMany(() => Agent, (agent) => agent.level)
  agents: Agent[];
}
