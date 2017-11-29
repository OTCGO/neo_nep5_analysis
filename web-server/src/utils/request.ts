/**
 * Filename: /Users/wei/Desktop/otcgo/neo_scrapy/src/utils/request.ts
 * Path: /Users/wei/Desktop/otcgo/neo_scrapy
 * Created Date: Thursday, November 16th 2017, 12:01:49 am
 * Author: wei
 *
 * Copyright (c) 2017 Your Company
 */

import * as config from 'config'
import * as request from 'request'

export function Request(params) {
    return new Promise<string>((resolve, reject) => {
        request.post(params, (err, response, body) => {
            if (err) reject(err)
            if (!err && /^2\d+/.test(response.statusCode.toString())) resolve(body)
            reject(body)
        })
    })
}


