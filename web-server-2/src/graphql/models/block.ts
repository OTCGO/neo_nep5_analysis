/**
 * Filename: /Users/wei/Desktop/otcgo/neo_wallet_analysis/web-server/src/graphql/models/address.ts
 * Path: /Users/wei/Desktop/otcgo/neo_wallet_analysis/web-server
 * Created Date: Thursday, November 23rd 2017, 4:31:49 pm
 * Author: qknow
 *
 * Copyright (c) 2017 otcgo.cn
 */


import * as graphql from 'graphql'

const block = new graphql.GraphQLObjectType({
  name: 'blocks',
  description: 'This is a blocks',
  fields: {
    _id: {
      type: graphql.GraphQLString
    },
    size: {
        type: graphql.GraphQLInt
    },
    version: {
        type: graphql.GraphQLInt
    },
    previousblockhash: {
        type: graphql.GraphQLString
    },
    merkleroot: {
        type: graphql.GraphQLString
    },
    time: {
        type: graphql.GraphQLInt
    }, // 时间
    index: {
        type: graphql.GraphQLInt
    }, // 高度
    nonce: {
        type: graphql.GraphQLString
    },
    nextconsensus: {
        type: graphql.GraphQLString
    },
    script: {
        type: new graphql.GraphQLObjectType({
            name: 'script',
            fields: {
                invocation: {
                 type: graphql.GraphQLString
               },
               verification: {
                 type: graphql.GraphQLString
               }
            }
          })
    },
    // tx: [ // tx.length  交易数

    // ],
    confirmations: {
        type: graphql.GraphQLInt
    },
    nextblockhash: {
        type: graphql.GraphQLString
    },
    createdAt: {
      type: graphql.GraphQLString
    },
    updatedAt: {
      type: graphql.GraphQLString
    }
  }
})

export { block }

hash: String,
    size: Number,
    version: Number,
    previousblockhash: String,
    merkleroot: String,
    time: Number, // 时间
    index: Number, // 高度
    nonce: String,
    nextconsensus: String,
    script: {
        invocation: String,
        verification: String
    },
    tx: [ // tx.length  交易数

    ],
    confirmations: Number,
    nextblockhash: String