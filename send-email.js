const nodemailer = require('nodemailer');
const fs = require('fs');
const path = require('path');

// 读取邮件内容
const emailContent = fs.readFileSync('E:\\EAMS-Project\\email-report-2026-03-25.txt', 'utf8');
const subject = "EAMS项目工作汇报 - 2026-03-25";

// 创建邮件传输器
const transporter = nodemailer.createTransport({
  host: 'smtp.exmail.qq.com',
  port: 465,
  secure: true,
  auth: {
    user: process.env.EMAIL_USER || 'qq@595jn.com',
    pass: process.env.EMAIL_PASS || 'your-auth-code'
  }
});

// 邮件选项
const mailOptions = {
  from: '"龙猫" <' + (process.env.EMAIL_USER || 'your-qq@qq.com') + '>',
  to: 'qq@595jn.com',
  subject: subject,
  text: emailContent,
  html: `<pre style="font-family: monospace; white-space: pre-wrap;">${emailContent.replace(/</g, '&lt;').replace(/>/g, '&gt;')}</pre>`
};

// 发送邮件
transporter.sendMail(mailOptions, (error, info) => {
  if (error) {
    console.error('邮件发送失败:', error);
    process.exit(1);
  } else {
    console.log('邮件发送成功:', info.messageId);
    console.log('响应:', info.response);
    process.exit(0);
  }
});
