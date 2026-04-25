import { Injectable } from '@nestjs/common';

@Injectable()
export class FinanceService {
  async getRecords(page: number, pageSize: number) {
    // TODO: 实现收支明细查询
    return {
      list: [],
      total: 0,
      page,
      pageSize,
    };
  }

  async getRecharges(page: number, pageSize: number) {
    // TODO: 实现充值明细查询
    return {
      list: [],
      total: 0,
      page,
      pageSize,
    };
  }

  async createRecharge(data: any) {
    // TODO: 实现充值订单创建
    return data;
  }
}
