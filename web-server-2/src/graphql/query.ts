/**
 * Filename: /Users/wei/Desktop/otcgo/neo_wallet_analysis/web-server/src/graphql/query.ts
 * Path: /Users/wei/Desktop/otcgo/neo_wallet_analysis/web-server
 * Created Date: Thursday, November 23rd 2017, 4:25:17 pm
 * Author: qknow
 *
 * Copyright (c) 2017 otcgo.cn
 */

import * as graphql from 'graphql'
import { address, transaction, asset } from './models'
import { Address, Transaction, Asset } from '../models'
import { queryBuilder, argsBuilder, pageQuery } from '../utils'
import { print } from 'util'


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
            type: new graphql.GraphQLList(address)
          }
        }
      })),
      args: argsBuilder({
        _id: {
          type: graphql.GraphQLString
        },
        address: {
          type: graphql.GraphQLString
        }
      }),
      async resolve (root, args) {
        if (args.address) {
          args.$or = [
            {'address.value': args.address},
            {'address.hash': args.address},
          ]
          delete args.address
        }
        return  pageQuery(args.skip, args.limit, Address, '', queryBuilder({}, args))
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
            type: new graphql.GraphQLList(transaction)
          }
        }
      })),
      args: argsBuilder({
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
      async resolve (root, args) {
        if (args.search) {
          args.$or = [
            {txid: args.search},
            {blockIndex: args.search},
            {contract: args.search},
            {operation: args.search},
            {'to.value': args.search},
            {'to.hash': args.search},
            {'from.value': args.search},
            {'from.hash': args.search}
          ]
          delete args.search
        }
        return  pageQuery(args.skip, args.limit, Transaction, '', queryBuilder({}, args))
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
            type: new graphql.GraphQLList(asset)
          }
        }
      })),
      args: argsBuilder({
        _id: {
          type: graphql.GraphQLString
        },
        symbol: {
          type: graphql.GraphQLString
        },
      }),
      async resolve (root, args) {
        return  pageQuery(args.skip, args.limit, Asset, '', queryBuilder({}, args))
      }
    },
    BlockQuery: {
      type: new graphql.GraphQLNonNull(new graphql.GraphQLObjectType({
        name: 'BlockQuery',
        fields: {
          count: {
            type: graphql.GraphQLInt
          },
          rows: {
            type: new graphql.GraphQLList(asset)
          }
        }
      })),
      args: argsBuilder({
        _id: {
          type: graphql.GraphQLString
        },
        symbol: {
          type: graphql.GraphQLString
        },
      }),
      async resolve (root, args) {
        return  pageQuery(args.skip, args.limit, Asset, '', queryBuilder({}, args))
      }
    },
  }
})

export default query