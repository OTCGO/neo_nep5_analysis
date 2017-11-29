"use strict";
/**
 * Filename: /Users/wei/Desktop/otcgo/neo_wallet_analysis/web-server/src/graphql/models/address.ts
 * Path: /Users/wei/Desktop/otcgo/neo_wallet_analysis/web-server
 * Created Date: Thursday, November 23rd 2017, 4:31:49 pm
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
const models_1 = require("../../models");
const address = new graphql.GraphQLObjectType({
    name: 'addresses',
    description: 'This is a address',
    fields: {
        _id: {
            type: graphql.GraphQLString
        },
        contract: {
            type: graphql.GraphQLString
        },
        address: {
            type: new graphql.GraphQLObjectType({
                name: 'address',
                fields: {
                    value: {
                        type: graphql.GraphQLString
                    },
                    hash: {
                        type: graphql.GraphQLString
                    }
                }
            })
        },
        symbol: {
            type: graphql.GraphQLString,
            resolve(address) {
                return __awaiter(this, void 0, void 0, function* () {
                    const asset = yield models_1.Asset.findOne({ contract: address.contract });
                    return asset.symbol;
                });
            }
        },
        createdAt: {
            type: graphql.GraphQLString
        },
        updatedAt: {
            type: graphql.GraphQLString
        }
    }
});
exports.address = address;
//# sourceMappingURL=address.js.map