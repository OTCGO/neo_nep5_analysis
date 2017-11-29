"use strict";
/**
 * Filename: g:\project\airplake\mdc-v4\src\app.ts
 * Path: g:\project\airplake\mdc-v4
 * Created Date: Tuesday, August 29th 2017, 10:35:34 am
 * Author: Wy
 *
 * Copyright (c) 2017 Your Company
 */
Object.defineProperty(exports, "__esModule", { value: true });
const bodyParser = require("body-parser");
const cors = require("cors");
const express = require("express");
const methodOverride = require("method-override");
const config = require("config");
const log4js = require("log4js");
// import { RPX } from './boot'
const router_1 = require("./router");
const middlewares_1 = require("./middlewares");
// log config
log4js.layouts.addLayout('json', function (config) {
    return function (logEvent) { return JSON.stringify(logEvent) + config.separator; };
});
log4js.configure(config.get('log'));
const logger = log4js.getLogger('http');
const app = express();
app.use(log4js.connectLogger(logger, { level: log4js.levels.INFO }));
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: true }));
app.use(cors({
    origin: true,
    credentials: true,
}));
// add put delete method
app.use(methodOverride());
app.use(middlewares_1.APIOutputMiddleware);
app.use(config.get('app.apiPrefix'), router_1.default);
// root /
app.get('/', function (req, res) {
    return res.send({ started: new Date() });
});
// 所有路由都未匹配（404）
app.use('*', function (req, res) {
    return res.sendStatus(404);
});
if (!module.parent) {
    logger.info(`config,${JSON.stringify(config)}`);
    app.listen(config.get('app.port') || 4000, config.get('app.host') || '127.0.0.1', () => {
        logger.info(`服务器启动，${config.get('app.host')}:${config.get('app.port')}`);
    });
}
exports.default = app;
//# sourceMappingURL=app.js.map