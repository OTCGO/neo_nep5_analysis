"use strict";
/**
 * Filename: /Users/wei/Desktop/otcgo/neo_scrapy/src/utils/request.ts
 * Path: /Users/wei/Desktop/otcgo/neo_scrapy
 * Created Date: Thursday, November 16th 2017, 12:01:49 am
 * Author: wei
 *
 * Copyright (c) 2017 Your Company
 */
Object.defineProperty(exports, "__esModule", { value: true });
const request = require("request");
function Request(params) {
    return new Promise((resolve, reject) => {
        request.post(params, (err, response, body) => {
            if (err)
                reject(err);
            if (!err && /^2\d+/.test(response.statusCode.toString()))
                resolve(body);
            reject(body);
        });
    });
}
exports.Request = Request;
//# sourceMappingURL=request.js.map