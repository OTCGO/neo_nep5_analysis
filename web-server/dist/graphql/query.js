"use strict";
/**
 * Filename: /Users/wei/Desktop/otcgo/neo_wallet_analysis/web-server/src/graphql/query.ts
 * Path: /Users/wei/Desktop/otcgo/neo_wallet_analysis/web-server
 * Created Date: Thursday, November 23rd 2017, 4:25:17 pm
 * Author: qknow
 *
 * Copyright (c) 2017 otcgo.cn
 */
var __awaiter = (this && this.__awaiter) || function (thisArg, _arguments, P, generator) {
    return new (P || (P = Promise))(function (resolve, reject) {
        function fulfilled(value) { try { step(generator.next(value)); } catch (e) { reject(e); } }
        function rejected(value) { try { step(generator["throw"](value)); } catch (e) { reject(e); } }
        function step(result) { result.done ? resolve(result.value) : new P(function (resolve) { resolve(result.value); }).then(fulfilled, rejected); }
        step((generator = generator.apply(thisArg, _arguments || [])).next());
    });
};
Object.defineProperty(exports, "__esModule", { value: true });
const graphql = require("graphql");
const models_1 = require("./models");
const models_2 = require("../models");
const utils_1 = require("../utils");
const query = new graphql.GraphQLObjectType({
    name: 'query',
    description: 'This is a root query',
    fields: {
        AddressQuery: {
            type: new graphql.GraphQLNonNull(new graphql.GraphQLObjectType({
                name: 'AddressQuery',
                fields: {
                    count: {
                        type: graphql.GraphQLInt
                    },
                    rows: {
                        type: new graphql.GraphQLList(models_1.address)
                    }
                }
            })),
            args: utils_1.argsBuilder({
                _id: {
                    type: graphql.GraphQLString
                },
                address: {
                    type: graphql.GraphQLString
                }
            }),
            resolve(root, args) {
                return __awaiter(this, void 0, void 0, function* () {
                    if (args.address) {
                        args.$or = [
                            { 'address.value': args.address },
                            { 'address.hash': args.address },
                        ];
                        delete args.address;
                    }
                    return utils_1.pageQuery(args.skip, args.limit, models_2.Address, '', utils_1.queryBuilder({}, args));
                });
            }
        },
        TransactionQuery: {
            type: new graphql.GraphQLNonNull(new graphql.GraphQLObjectType({
                name: 'TransactionQuery',
                fields: {
                    count: {
                        type: graphql.GraphQLInt
                    },
                    rows: {
                        type: new graphql.GraphQLList(models_1.transaction)
                    }
                }
            })),
            args: utils_1.argsBuilder({
                _id: {
                    type: graphql.GraphQLString
                },
                txid: {
                    type: graphql.GraphQLString
                },
                blockIndex: {
                    type: graphql.GraphQLString
                },
                search: {
                    type: graphql.GraphQLString
                },
            }),
            resolve(root, args) {
                return __awaiter(this, void 0, void 0, function* () {
                    if (args.search) {
                        args.$or = [
                            { txid: args.search },
                            { blockIndex: args.search },
                            { contract: args.search },
                            { operation: args.search },
                            { 'to.value': args.search },
                            { 'to.hash': args.search },
                            { 'from.value': args.search },
                            { 'from.hash': args.search }
                        ];
                        delete args.search;
                    }
                    return utils_1.pageQuery(args.skip, args.limit, models_2.Transaction, '', utils_1.queryBuilder({}, args));
                });
            }
        },
        AssetQuery: {
            type: new graphql.GraphQLNonNull(new graphql.GraphQLObjectType({
                name: 'AssetQuery',
                fields: {
                    count: {
                        type: graphql.GraphQLInt
                    },
                    rows: {
                        type: new graphql.GraphQLList(models_1.asset)
                    }
                }
            })),
            args: utils_1.argsBuilder({
                _id: {
                    type: graphql.GraphQLString
                },
                symbol: {
                    type: graphql.GraphQLString
                },
            }),
            resolve(root, args) {
                return __awaiter(this, void 0, void 0, function* () {
                    return utils_1.pageQuery(args.skip, args.limit, models_2.Asset, '', utils_1.queryBuilder({}, args));
                });
            }
        },
    }
});
exports.default = query;
//# sourceMappingURL=query.js.map