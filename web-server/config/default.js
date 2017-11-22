module.exports = {
  app: {
    host: '0.0.0.0', // host
    port: '8001', // port
    apiPrefix: '/api/v1' // api 前缀
  },
  log: {
    appenders: [ // 日志
      {
        type: 'console'
      }, // 控制台输出
      {
        type: 'file',
        filename: 'logs/http.log',
        maxLogSize: 20480,
        backups: 1,
        category: 'http',
        layout: {
          type: 'json',
          separator: ','
        }
      },
      {
        type: 'file',
        filename: 'logs/init.log',
        maxLogSize: 20480,
        backups: 1,
        category: 'init',
        layout: {
          type: 'json',
          separator: ','
        }
      },
      {
        type: 'file',
        filename: 'logs/rpx.log',
        maxLogSize: 52428800,
        backups: 2,
        category: 'rpx',
        layout: {
          type: 'json',
          separator: ','
        }
      }
    ]
  }
}
