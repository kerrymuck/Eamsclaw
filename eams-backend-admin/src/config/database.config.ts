export default () => ({
  database: {
    type: 'sqlite',
    database: 'eams_admin.db',
    entities: [__dirname + '/../entities/*.entity{.ts,.js}'],
    synchronize: true,
    logging: false,
  },
});
