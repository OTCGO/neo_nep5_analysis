"use strict";
/**
 * Filename: /Users/wei/Desktop/otcgo/neo_wallet_analysis/web-server/src/graphql/models/address.ts
 * Path: /Users/wei/Desktop/otcgo/neo_wallet_analysis/web-server
 * Created Date: Thursday, November 23rd 2017, 4:31:49 pm
 * Author: qknow
 *
 * Copyright (c) 2017 otcgo.cn
 */
Object.defineProperty(exports, "__esModule", { value: true });
const graphql = require("graphql");
const asset = new graphql.GraphQLObjectType({
    name: 'assets',
    description: 'This is a assets',
    fields: {
        _id: {
            type: graphql.GraphQLString
        },
        contract: {
            type: graphql.GraphQLString
        },
        symbol: {
            type: graphql.GraphQLString
        },
        createdAt: {
            type: graphql.GraphQLString
        },
        updatedAt: {
            type: graphql.GraphQLString
        }
    }
});
exports.asset = asset;
//# sourceMappingURL=asset.js.map