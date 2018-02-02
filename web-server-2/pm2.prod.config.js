module.exports = {
    /**
     * Application configuration section
     * http://pm2.keymetrics.io/docs/usage/application-declaration/
     */
  apps: [
    {
      name: 'neo-api',
      script: './dist/app.js',
      env: {   // all environment
        'NODE_ENV': 'production'
      },
      'instances': 'max',   // 如果是fork, 不用配置
      'exec_mode': 'cluster'  // cluster or fork
    }
  ]
}
