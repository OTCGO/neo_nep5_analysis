module.exports = {
  app: {
    host: '0.0.0.0', // host
    port: '5001', // port
    apiPrefix: '/api/v1' // api 前缀
  },
  rpc: 'http://127.0.0.1:10332',
  dbNep5: {
    options: {
      host: '127.0.0.1.71',
      user: 'otcgo',
      pass: 'u3fhhrPr'
    },
    isAuthSource: 'admin',
    db: 'neo-otcgo'
  },
  dbGlobal: {
    options: {
      host: '127.0.0.1.71',
      user: 'otcgo',
      pass: 'u3fhhrPr'
    },
    isAuthSource: 'admin',
    db: 'neo-main'
  }
}
