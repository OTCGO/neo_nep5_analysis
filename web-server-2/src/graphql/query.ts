/**
 * Filename: /Users/wei/Desktop/otcgo/neo_wallet_analysis/web-server/src/graphql/query.ts
 * Path: /Users/wei/Desktop/otcgo/neo_wallet_analysis/web-server
 * Created Date: Thursday, November 23rd 2017, 4:25:17 pm
 * Author: qknow
 *
 * Copyright (c) 2017 otcgo.cn
 */

import * as graphql from 'graphql'
import * as config from 'config'
import { address, transaction, asset, block } from './models'
// import { Address, Transaction, Asset } from '../models'
import { queryBuilder, argsBuilder, pageQuery } from '../utils'
import { DBClient } from '../lib'

// const dbNep5Client: any = new DBClient(config.get('dbNep5'))
const dbGlobalClient: any = new DBClient(config.get('dbGlobal'))



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
        // if (args.address) {
        //   args.$or = [
        //     {'address.value': args.address},
        //     {'address.hash': args.address},
        //   ]
        //   delete args.address
        // }
         const dbGlobal = await dbGlobalClient.connection()
         return  pageQuery(args.skip, args.limit, dbGlobal.b_neo_m_addresses, undefined, queryBuilder({}, args), {})
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
          type: graphql.GraphQLInt
        },
        search: {
          type: graphql.GraphQLString
        },
      }),
      async resolve (root, args) {
        // if (args.search) {
        //   args.$or = [
        //     {txid: args.search},
        //     {blockIndex: args.search},
        //     {contract: args.search},
        //     {operation: args.search},
        //     {'to.value': args.search},
        //     {'to.hash': args.search},
        //     {'from.value': args.search},
        //     {'from.hash': args.search}
        //   ]
        //   delete args.search
        // }

        const dbGlobal = await dbGlobalClient.connection()
       // const dbNep5 = await dbNep5Client.connection()
        return  pageQuery(args.skip, args.limit, dbGlobal.b_neo_m_transactions, undefined, queryBuilder({}, args), { blockIndex: -1 })
       // let nep5Obj = pageQuery(args.skip, args.limit, dbNep5.b_neo_m_transactions, undefined, queryBuilder({}, args), { blockIndex: -1 })
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
       // return  pageQuery(args.skip, args.limit, Asset, '', queryBuilder({}, args))
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
            type: new graphql.GraphQLList(block)
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
        const dbGlobal = await dbGlobalClient.connection()
        return  pageQuery(args.skip, args.limit, dbGlobal.b_neo_m_blocks, undefined, queryBuilder({}, args), { index: -1 }, { })
      }
    },
  }
})

export default query