import * as mongoose from 'mongoose'
import * as bluebird from 'bluebird'
import * as log4js from 'log4js'
import * as config from 'config'



const logger = log4js.getLogger('db')
mongoose.Promise = bluebird
mongoose.set('debug', config.get('db.debug'))

const connectionStr = config.get('db.url')

mongoose.connect(connectionStr, config.get('db.options'))



mongoose.connection.on('connected', function () {
    logger.info('mongodb connection: ' + connectionStr)
})

/**
 * 连接异常
 */
mongoose.connection.on('error', function (err) {
    console.log('Mongoose connection error: ' + err)
    logger.info('Mongoose connection error: ' + err)
})

/**
 * 连接断开
 */
mongoose.connection.on('disconnected', function () {
    console.log('Mongoose connection disconnected')
    logger.info('Mongoose connection disconnected')
})

logger.info('mongodb connection: ' + connectionStr)


export  { mongoose }