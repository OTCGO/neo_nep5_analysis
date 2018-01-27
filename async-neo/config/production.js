module.exports = {
    config: {
      network: 'mainnet',
      storage: {
        model: 'mongoDB',
        connectOnInit: true,
        connectionString: 'mongodb://otcgo:u3fhhrPr@127.0.0.1:27017/neo-main?authSource=admin',
        collectionNames: {
          blocks: 'b_neo_m_blocks',
          transactions: 'b_neo_m_transactions',
          addresses: 'b_neo_m_addresses',
          assets: 'b_neo_m_assets'
        }
      }
    }
  }
  