import { Injectable, NotFoundException } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository } from 'typeorm';
import { AiModel } from '../../entities/ai-model.entity';

@Injectable()
export class AiService {
  constructor(
    @InjectRepository(AiModel)
    private aiModelRepository: Repository<AiModel>,
  ) {}

  async findAll() {
    return this.aiModelRepository.find({
      order: { createdAt: 'DESC' },
    });
  }

  async create(data: Partial<AiModel>) {
    const model = this.aiModelRepository.create(data);
    return this.aiModelRepository.save(model);
  }

  async update(id: number, data: Partial<AiModel>) {
    const model = await this.aiModelRepository.findOne({ where: { id } });
    if (!model) {
      throw new NotFoundException('模型不存在');
    }
    Object.assign(model, data);
    return this.aiModelRepository.save(model);
  }

  async updateStatus(id: number, status: number) {
    const model = await this.aiModelRepository.findOne({ where: { id } });
    if (!model) {
      throw new NotFoundException('模型不存在');
    }
    model.status = status;
    return this.aiModelRepository.save(model);
  }

  async updatePricing(id: number, pricing: { pricePer1kInput?: number; pricePer1kOutput?: number }) {
    const model = await this.aiModelRepository.findOne({ where: { id } });
    if (!model) {
      throw new NotFoundException('模型不存在');
    }
    if (pricing.pricePer1kInput !== undefined) {
      model.pricePer1kInput = pricing.pricePer1kInput;
    }
    if (pricing.pricePer1kOutput !== undefined) {
      model.pricePer1kOutput = pricing.pricePer1kOutput;
    }
    return this.aiModelRepository.save(model);
  }
}
