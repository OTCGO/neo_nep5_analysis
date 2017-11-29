"use strict";
/**
 * Filename: /Users/wei/Desktop/otcgo/neo_scrapy/src/modules/rpx/rpx.ts
 * Path: /Users/wei/Desktop/otcgo/neo_scrapy
 * Created Date: Thursday, November 16th 2017, 12:14:47 am
 * Author: wei
 *
 * Copyright (c) 2017 Your Company
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
const log4js = require("log4js");
const config = require("config");
const express_1 = require("express");
const graphqlHTTP = require("express-graphql");
const neon = require("@cityofzion/neon-js");
const utils_1 = require("../../utils");
const graphql_1 = require("../../graphql");
const logger = log4js.getLogger('nep5');
const nep5 = express_1.Router();
exports.nep5 = nep5;
nep5.use(`/public/graphql`, graphqlHTTP({
    schema: graphql_1.default,
    graphiql: true,
    pretty: true,
    extensions({ documet, variables, operationName, result }) {
        if (result.errors) {
            result.error_code = 500;
            result.error_msg = result.errors[0].message;
            delete result.errors;
            result.status = 'Error';
        }
        else {
            result.code = 200;
            result.status = 'OK';
            result.server_time = new Date();
        }
    }
}));
nep5.get(`/address/balanceOf`, (req, res) => __awaiter(this, void 0, void 0, function* () {
    try {
        logger.info(`${config.get('rpc')}`);
        const result = yield utils_1.Request({
            url: `${config.get('rpc')}`,
            method: 'post',
            json: {
                jsonrpc: '2.0',
                method: 'invokefunction',
                params: [
                    'ecc6b20d3ccac1ee9ef109af5a7cdb85706b1df9',
                    'balanceOf',
                    [
                        {
                            type: 'Hash160',
                            value: 'bfc469dd56932409677278f6b7422f3e1f34481d'
                        }
                    ]
                ],
                id: 3
            }
        });
        console.log('0x' + result.result.stack[0].value.toString(10).toString(10));
        console.log(neon.u.fixed82num(result.result.stack[0].value));
        return res.apiSuccess('11');
    }
    catch (error) {
        logger.error('nep5', error);
        return res.apiError(error);
    }
}));
//# sourceMappingURL=nep5.js.map