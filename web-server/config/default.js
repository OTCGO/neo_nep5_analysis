module.exports = {
  app: {
    host: '0.0.0.0', // host
    port: '8001', // port
    apiPrefix: '/api/v1' // api 前缀
  },
  db: {
    url: 'mongodb://114.215.30.71/neo-otcgo',
    options: {
      useMongoClient: true
    },
    debug: true
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
        filename: 'logs/db.log',
        maxLogSize: 52428800,
        backups: 2,
        category: 'db',
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
        filename: 'logs/nep5.log',
        maxLogSize: 52428800,
        backups: 2,
        category: 'nep5',
        layout: {
          type: 'json',
          separator: ','
        }
      }
    ]
  }
}
