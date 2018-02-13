module.exports = {
  app: {
    host: '0.0.0.0', // host
    port: '5001', // port
    apiPrefix: '/api/v1' // api 前缀
  },
  // db: {
  //   url: 'mongodb://114.215.30.71:27017/neo-otcgo?authSource=admin',
  //   options: {
  //     useMongoClient: true,
  //     user: 'otcgo',
  //     pass: 'u3fhhrPr',
  //     auth: {
  //       authdb: 'admin'
  //     }
  //   },
  //   debug: true
  // },
  rpc: 'http://seed2.neo.org:10332',
  dbNep5: {
    options: {
      host: '127.0.0.1'
      // user: 'otcgo',
      // pass: 'u3fhhrPr'
    },
    // isAuthSource: 'admin',
    db: 'neo-otcgo'
  },
  dbGlobal: {
    options: {
      host: '127.0.0.1'
      // user: 'otcgo',
      // pass: 'u3fhhrPr'
    },
    // isAuthSource: 'admin',
    db: 'neo-main'
  },
  asserts: {
    '0xc56f33fc6ecfcd0c225c4ab356fee59390af8560be0e930faebe74a6daff7c9b': 'NEO',           // NEO
    '0x602c79718b16e442de58778e148d0b1084e3b2dffd5de6b7b16cee7969282de7': 'GAS',           // GAS
    '0x7f48028c38117ac9e42c8e1f6f06ae027cdbb904eaf1a0bdc30c9d81694e045c': '无忧宝',         // 无忧宝
    '0xa52e3e99b6c2dd2312a94c635c050b4c2bc2485fcb924eecb615852bd534a63f': '申一币',         // 申一币
    '0x025d82f7b00a9ff1cfe709abe3c4741a105d067178e645bc3ebad9bc79af47d4': 'TestCoin',      // TestCoin
    '0x07de511668e6ecc90973d713451c831d625eca229242d34debf16afa12efc1c1': '开拍学园币（KAC）', // 开拍学园币（KAC）
    '0x0ab0032ade19975183c4ac90854f1f3c3fc535199831e7d8f018dabb2f35081f': '量子积分',         // 量子积分
    '0x1b504c5fb070aaca3d57c42b5297d811fe6f5a0c5d4cd4496261417cf99013a5': '量子股份',         // 量子股份
    '0x459ef82138f528c5ff79dd67dcfe293e6a348e447ed8f6bce5b79dded2e63409': '赏金（SJ-Money)',  // 赏金（SJ-Money)
    '0x30e9636bc249f288139651d60f67c110c3ca4c3dd30ddfa3cbcec7bb13f14fd4': '申一股份',         // 申一股份
    '0x439af8273fbe25fec2f5f2066679e82314fe0776d52a8c1c87e863bd831ced7d': 'Hello AntShares Mainnet',         // Hello AntShares Mainnet
    '0x7ed4d563277f54a1535f4406e4826882287fb74d06a1a53e76d3d94d9b3b946a': '宝贝评级',         // 宝贝评级
    '0xdd977e41a4e9d5166003578271f191aae9de5fc2de90e966c8d19286e37fa1e1': '橙诺',         // 橙诺
    '0x9b63fa15ed58e93339483619175064ecadbbe953436a22c31c0053dedca99833': '未来研究院',         // 未来研究院
    '0x308b0b336e2ed3d718ef92693b70d30b4fe20821265e8e76aecd04a643d0d7fa': '明星资本',         // 明星资本
    '0x6161af8875eb78654e385a33e7334a473a2a0519281d33c06780ff3c8bce15ea': '量子人民币',         // 量子人民币
    '0xcb453a56856a236cbae8b8f937db308a15421daada4ba6ce78123b59bfb7253c': '人民币CNY',         // 人民币CNY
    '0xc0b3c094efd1849c125618519ae733e3b63c976d60fc7e3d0e88af86a65047e3': '开拍学园',         // 开拍学园
    '0x3ff74cf84869a7df96ede132de9fa62e13aa3ac8a6548e546ad316f4bda6460c': '币区势',         // 币区势
    '0xc39631b351c1f385afc1eafcc0ff365977b59f4aa4a09a0b7b1f5705241457b7': '花季股'         // 花季股
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
        filename: 'logs/mainnet.log',
        maxLogSize: 52428800,
        backups: 2,
        category: 'mainnet',
        layout: {
          type: 'json',
          separator: ','
        }
      }
    ]
  }
}
