import {
  Entity,
  PrimaryGeneratedColumn,
  Column,
  CreateDateColumn,
} from 'typeorm';

@Entity('ai_models')
export class AiModel {
  @PrimaryGeneratedColumn()
  id: number;

  @Column({ name: 'model_code', unique: true, length: 50 })
  modelCode: string;

  @Column({ name: 'model_name', length: 100 })
  modelName: string;

  @Column({ length: 50 })
  provider: string; // openai/anthropic/ali/baidu/google

  @Column({ name: 'api_endpoint', length: 500, nullable: true })
  apiEndpoint: string;

  @Column({ name: 'api_key', length: 500, nullable: true })
  apiKey: string;

  @Column({ name: 'price_per_1k_input', type: 'decimal', precision: 18, scale: 6, default: 0 })
  pricePer1kInput: number;

  @Column({ name: 'price_per_1k_output', type: 'decimal', precision: 18, scale: 6, default: 0 })
  pricePer1kOutput: number;

  @Column({ default: 1 })
  status: number; // 0-禁用 1-启用

  @CreateDateColumn({ name: 'created_at' })
  createdAt: Date;
}
