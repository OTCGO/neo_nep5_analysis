module.exports = {
  app: {
    host: '0.0.0.0', // host
    port: '4001', // port
    apiPrefix: '/api/v1' // api 前缀
  },
  rpc: 'http://seed2.neo.org:10332',
  db: {
    url: 'mongodb://127.0.0.1:27017/neo-otcgo?replicaSet=rs1',
    options: {
      useMongoClient: true,
      user: 'otcgo',
      pass: 'u3fhhrPr',
      auth: {
        authdb: 'admin'
      }
    },
    dbNep5: {
      options: {
        host: '114.215.30.71',
        user: 'otcgo',
        pass: 'u3fhhrPr'
      },
      isReplset: 'rs1',
      db: 'neo-otcgo'
    },
    debug: false
  }
}
