export default () => ({
  jwt: {
    secret: process.env.JWT_SECRET || 'eams-admin-secret-key-change-in-production',
    signOptions: {
      expiresIn: process.env.JWT_EXPIRES_IN || '7d',
    },
  },
});
