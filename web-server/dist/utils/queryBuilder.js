"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
/**
 * Filename: /Users/wei/Desktop/otcgo/neo_wallet_analysis/web-server/src/utils/queryBuilder.ts
 * Path: /Users/wei/Desktop/otcgo/neo_wallet_analysis/web-server
 * Created Date: Thursday, November 23rd 2017, 7:33:06 pm
 * Author: qknow
 *
 * Copyright (c) 2017 otcgo.cn
 */
const queryBuilder = (query, args) => {
    delete args.skip;
    delete args.limit;
    return Object.assign({}, query, args);
};
exports.queryBuilder = queryBuilder;
//# sourceMappingURL=queryBuilder.js.map