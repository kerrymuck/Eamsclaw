import { Injectable, UnauthorizedException } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository } from 'typeorm';
import { JwtService } from '@nestjs/jwt';
import * as bcrypt from 'bcrypt';
import { AdminUser } from '../../entities/admin-user.entity';
import { LoginDto } from '../../dtos/login.dto';

@Injectable()
export class AuthService {
  constructor(
    @InjectRepository(AdminUser)
    private adminUserRepository: Repository<AdminUser>,
    private jwtService: JwtService,
  ) {}

  async login(loginDto: LoginDto) {
    const { username, password } = loginDto;

    const user = await this.adminUserRepository.findOne({
      where: { username },
    });

    if (!user) {
      throw new UnauthorizedException('用户名或密码错误');
    }

    const isPasswordValid = await bcrypt.compare(password, user.password);
    if (!isPasswordValid) {
      throw new UnauthorizedException('用户名或密码错误');
    }

    if (user.status !== 1) {
      throw new UnauthorizedException('账号已被禁用');
    }

    const payload = {
      sub: user.id,
      username: user.username,
      role: user.role,
    };

    const token = this.jwtService.sign(payload);

    return {
      token,
      userInfo: {
        id: user.id,
        username: user.username,
        nickname: user.nickname,
        avatar: user.avatar,
        role: user.role,
        permissions: user.permissions || [],
      },
    };
  }

  async getProfile() {
    // TODO: 从JWT中获取用户ID并返回详细信息
    return { message: '获取成功' };
  }

  // 初始化超级管理员
  async initSuperAdmin() {
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
}
