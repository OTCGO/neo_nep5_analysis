"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const mongoose = require("mongoose");
exports.mongoose = mongoose;
const bluebird = require("bluebird");
const log4js = require("log4js");
const config = require("config");
const logger = log4js.getLogger('db');
mongoose.Promise = bluebird;
mongoose.set('debug', config.get('db.debug'));
const connectionStr = config.get('db.url');
mongoose.connect(connectionStr, config.get('db.options'));
mongoose.connection.on('connected', function () {
    logger.info('mongodb connection: ' + connectionStr);
});
/**
 * 连接异常
 */
mongoose.connection.on('error', function (err) {
    console.log('Mongoose connection error: ' + err);
    logger.info('Mongoose connection error: ' + err);
});
/**
 * 连接断开
 */
mongoose.connection.on('disconnected', function () {
    console.log('Mongoose connection disconnected');
    logger.info('Mongoose connection disconnected');
});
logger.info('mongodb connection: ' + connectionStr);
//# sourceMappingURL=db.js.map