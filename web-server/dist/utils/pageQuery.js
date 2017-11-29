"use strict";
/**
 * Filename: /Users/wei/Desktop/otcgo/neo_wallet_analysis/web-server/src/utils/pageQuery.ts
 * Path: /Users/wei/Desktop/otcgo/neo_wallet_analysis/web-server
 * Created Date: Sunday, November 26th 2017, 12:14:02 pm
 * Author: qknow
 *
 * Copyright (c) 2017 otcgo.cn
 */
Object.defineProperty(exports, "__esModule", { value: true });
/**
 * Filename: /Users/wei/Desktop/otcgo/neo_wallet_analysis/web-server/src/utils/pageQuery.ts
 * Path: /Users/wei/Desktop/otcgo/neo_wallet_analysis/web-server
 * Created Date: Sunday, November 26th 2017, 12:14:02 pm
 * Author: qknow
 *
 * Copyright (c) 2017 otcgo.cn
 */
const async_1 = require("async");
const pageQuery = function (skip = 0, limit = 20, Model, populate = {}, queryParams = {}, sortParams = { createdAt: 'desc' }) {
    console.log('queryParams', queryParams);
    return new Promise((resolve, reject) => {
        const $page = {
            rows: [],
            count: 0
        };
        async_1.default.parallel({
            count(done) {
                Model.count(queryParams).exec(function (err, count) {
                    done(err, count);
                });
            },
            records(done) {
                Model.find(queryParams).skip(skip).limit(limit).populate(populate).sort(sortParams).exec(function (err, doc) {
                    done(err, doc);
                });
            }
        }, function (err, results) {
            if (err)
                return reject(err);
            $page.count = results.count;
            $page.rows = results.records;
            return resolve($page);
        });
    });
};
exports.pageQuery = pageQuery;
//# sourceMappingURL=pageQuery.js.map