import {
  Entity,
  PrimaryGeneratedColumn,
  Column,
  CreateDateColumn,
  ManyToOne,
  JoinColumn,
} from 'typeorm';
import { Agent } from './agent.entity';

@Entity('auth_codes')
export class AuthCode {
  @PrimaryGeneratedColumn()
  id: number;

  @Column({ unique: true, length: 64 })
  code: string;

  @Column({ name: 'agent_id', nullable: true })
  agentId: number;

  @ManyToOne(() => Agent)
  @JoinColumn({ name: 'agent_id' })
  agent: Agent;

  @Column({ name: 'merchant_id', nullable: true })
  merchantId: number;

  @Column({ default: 1 })
  type: number; // 1-标准版 2-专业版 3-企业版

  @Column({ default: 0 })
  status: number; // 0-未激活 1-已激活 2-已过期 3-已禁用

  @Column({ name: 'valid_days', default: 365 })
  validDays: number;

  @Column({ name: 'activated_at', nullable: true })
  activatedAt: Date;

  @Column({ name: 'expired_at', nullable: true })
  expiredAt: Date;

  @CreateDateColumn({ name: 'created_at' })
  createdAt: Date;

  @Column({ name: 'created_by', nullable: true })
  createdBy: number;
}
