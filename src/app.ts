/**
 * Filename: g:\project\airplake\mdc-v4\src\app.ts
 * Path: g:\project\airplake\mdc-v4
 * Created Date: Tuesday, August 29th 2017, 10:35:34 am
 * Author: Wy
 *
 * Copyright (c) 2017 Your Company
 */

import * as bodyParser from "body-parser"
import * as cors from "cors"
import * as express from "express"
import * as methodOverride from "method-override"
import * as config from "config"
import * as log4js from "log4js"
// import { * } from "./boot"
import router from "./router"
import { APIOutputMiddleware } from "./middlewares"

// log config
log4js.layouts.addLayout("json", function (config) {
  return function (logEvent) { return JSON.stringify(logEvent) + config.separator }
})
log4js.configure(config.get("log"))
const logger = log4js.getLogger("http")

const app = express()

app.use(log4js.connectLogger(logger, { level: log4js.levels.INFO }))
app.use(bodyParser.json())
app.use(bodyParser.urlencoded({ extended: true }))
app.use(cors({
  origin: true,
  credentials: true,
}))
// add put delete method
app.use(methodOverride())
app.use(APIOutputMiddleware)

app.use(config.get("app.apiPrefix"), router)

// root /
app.get("/", function(req, res) {
  return res.send({started: new Date()})
})

// 所有路由都未匹配（404）
app.use("*", function(req, res) {
  return res.sendStatus(404)
})

if (!module.parent) {
  logger.info(`node:env`, process.env.NODE_ENV)
  logger.info(`config,${JSON.stringify(config)}`)
  app.listen(config.get("app.port") || 4000, config.get("app.host") || "127.0.0.1", () => {
    logger.info(`服务器启动，${config.get("app.host")}:${config.get("app.port")}`)
  })
}

export default app
