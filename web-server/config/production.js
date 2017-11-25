module.exports = {
  app: {
    host: '0.0.0.0', // host
    port: '4001', // port
    apiPrefix: '/api/v1' // api 前缀
  },
  db: {
    url: 'mongodb://127.0.0.1/neo-otcgo',
    options: {
      useMongoClient: true
    },
    debug: false
  }
}
