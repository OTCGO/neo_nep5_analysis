/**
 * Filename: /Users/wei/Desktop/yedian/message-distributing-center/src/middlewares/validateMiddleware.ts
 * Path: /Users/wei/Desktop/yedian/message-distributing-center
 * Created Date: Wednesday, November 8th 2017, 5:31:30 pm
 * Author: wei
 *
 * Copyright (c) 2017 Your Company
 */

import * as joi from "joi"

/**
 * joi 验证中间件
 */

function ValidateMiddleware(schema) {
    return (req, res, next) => {
        let result: any = {}
        if (schema.body) {
            result = joi.validate(req.body, schema.body)
            if (result.error) {
                return res.apiError(result.error.message)
            }
        }
        if (schema.params) {
            result = joi.validate(req.params, schema.params)
            if (result.error) {
                return res.apiError(result.error.message)
            }
        }
        if (schema.query) {
            result = joi.validate(req.query, schema.query)
            if (result.error) {
                return res.apiError(result.error.message)
            }
        }
        if (schema.header) {
            result = joi.validate(req.headers, schema.header, { allowUnknown: true })
            if (result.error) {
                return res.apiError(result.error.message)
            }
        }
        next()
    }
}

export { ValidateMiddleware }
