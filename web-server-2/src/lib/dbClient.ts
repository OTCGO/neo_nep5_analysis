const MongoClient = require('mongodb').MongoClient
const _ = require('lodash')
import * as log4js from 'log4js'
import * as config from 'config'

const logger = log4js.getLogger('db')

class DBClient {
  private MongoUrl

  constructor (dbConfig) {
      const { options, db } = dbConfig
      const isReplset = dbConfig.isReplset || ['staging', 'production'].indexOf(process.env.NODE_ENV) > -1
      const isAuthSource = dbConfig.isAuthSource || ['staging', 'production'].indexOf(process.env.NODE_ENV) > -1

      const auth = options.user ? `${options.user}:${options.pass}@` : ''
      const replset = isReplset ? '?replicaSet=rs1' : ''
      const authSource = isReplset ? (isAuthSource ? `&authSource=${isAuthSource}` : '') : (isAuthSource ? `?authSource=${isAuthSource}` : '')
      this.MongoUrl = `mongodb://${auth}${options.host}/${db}${replset}${authSource}`
    // this.MongoUrl = `mongodb://otcgo:u3fhhrPr@114.215.30.71:27017/neo-otcgo?authSource=admin`
      // mongodb:// otcgo:u3fhhrPr@127.0.0.1:27017/?authSource=admin&replicaSet=rs1
      logger.info(`dbClient - dbconfig: ${JSON.stringify(dbConfig)}`)
  }

  async connection() {
    try {
      const dbClient = {}

      const client = await MongoClient.connect(this.MongoUrl)
      logger.info(`mongo connection: ${this.MongoUrl}`)
      const collections = await client.listCollections().toArray()
      _.map(collections, (collection) => {
        const collectionName = collection.name
        dbClient[collection.name] = client.collection(collectionName)
      })
      return dbClient
    } catch (error) {
      logger.info('dbClient connection: ' + error)
    }
  }
}

export { DBClient }
