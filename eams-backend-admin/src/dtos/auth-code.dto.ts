import { IsNumber, IsNotEmpty, IsOptional, Min } from 'class-validator';

export class GenerateAuthCodeDto {
  @IsNumber()
  @IsOptional()
  agentId?: number;

  @IsNumber()
  @IsNotEmpty({ message: '授权类型不能为空' })
  type: number;

  @IsNumber()
  @Min(1, { message: '生成数量至少为1' })
  count: number;

  @IsNumber()
  @IsNotEmpty({ message: '有效天数不能为空' })
  validDays: number;
}
