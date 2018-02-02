/**
 * Filename: /Users/wei/Desktop/otcgo/neo_wallet_analysis/web-server/src/graphql/models/address.ts
 * Path: /Users/wei/Desktop/otcgo/neo_wallet_analysis/web-server
 * Created Date: Thursday, November 23rd 2017, 4:31:49 pm
 * Author: qknow
 *
 * Copyright (c) 2017 otcgo.cn
 */


import * as graphql from 'graphql'
// import {  Asset } from '../../models'
import { DBClient } from '../../lib'
import * as config from 'config'

const dbNep5Client: any = new DBClient(config.get('dbNep5'))

const transaction = new graphql.GraphQLObjectType({
  name: 'transaction',
  description: 'This is a transaction',
  fields: {
    _id: {
      type: graphql.GraphQLString
    },
    txid: {
      type: graphql.GraphQLString
    },
    /*
    to: {
     type: new graphql.GraphQLObjectType({
       name: 'toAddress',
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
    from: {
      type: new graphql.GraphQLObjectType({
        name: 'fromAddress',
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
      async resolve (address) {
        const asset = await Asset.findOne({contract: address.contract})
        return asset.symbol
      }
    },
    value: {
      type: graphql.GraphQLString
    },
    */
    blockIndex: {
      type: graphql.GraphQLInt
    },
    size: {
      type: graphql.GraphQLInt
    },
    type: {
      type: graphql.GraphQLString
    },
    scripts: {
      type: new graphql.GraphQLList(new graphql.GraphQLObjectType({
        name: 'scripts',
        fields: {
          invocation: {
             type: graphql.GraphQLString
           },
           verification: {
             type: graphql.GraphQLString
           }
        }
      }))
    },
    attributes: {
      type: graphql.GraphQLString
    },
    vin: {
      type: new graphql.GraphQLList(new graphql.GraphQLObjectType({
        name: 'vin',
        description: 'This is a vin',
        fields: {
          vout: {
            type: graphql.GraphQLInt
          },
          txid: {
            type: graphql.GraphQLString
          },
        }
      }))
    },
    vout: {
      type: new graphql.GraphQLList(new graphql.GraphQLObjectType({
        name: 'vout',
        description: 'This is a vout',
        fields: {
          address: {
            type: graphql.GraphQLString
          },
          value: {
            type: graphql.GraphQLInt
          },
          asset: {
            type: graphql.GraphQLString
          },
          n: {
            type: graphql.GraphQLInt
          },
        }
      }))
    },
    nep5: {
      type: new graphql.GraphQLObjectType({
        name: 'nep5',
        description: 'This is a nep5',
        fields: {
          to: {
            type: new graphql.GraphQLObjectType({
              name: 'toAddress',
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
           from: {
             type: new graphql.GraphQLObjectType({
               name: 'fromAddress',
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
             async resolve (address) {
              console.log('address', address)
               if (address) {
                const dbNep5 = await dbNep5Client.connection()
                const asset = await dbNep5.nep5_m_assets.findOne({contract: address.contract})
                console.log('asset', asset)
                return asset.symbol
               }
             }
           },
           value: {
             type: graphql.GraphQLString
           },
           operation: {
            type: graphql.GraphQLString
          },
          contract: {
            type: graphql.GraphQLString
          }
        }
      }),
      async resolve (transaction) {
        if (transaction.type === 'InvocationTransaction') {
          const dbNep5 = await dbNep5Client.connection()
          return dbNep5.nep5_m_transactions.findOne({txid: transaction.txid})
        }

      }
    },
    createdAt: {
      type: graphql.GraphQLString
    },
    updatedAt: {
      type: graphql.GraphQLString
    }
  }
})

export { transaction }

/*
{
  "_id" : ObjectId("5a6be77f8fd7c724493cb174"),
  "txid" : "0xdecbdc420b4a1081c0e8b4cd87f09b297b8e07112b58203725973041be5c2caa",
  "size" : 10,
  "type" : "MinerTransaction",
  "version" : 0,
  "sys_fee" : 0,
  "net_fee" : 0,
  "blockIndex" : 14,
  "scripts" : [],
  "vout" : [
      {
          "address" : "AQ3c2yWjSwm6M2ukBoEYnEPybyRDHscvno",
          "value" : 9,
          "asset" : "0xc56f33fc6ecfcd0c225c4ab356fee59390af8560be0e930faebe74a6daff7c9b",
          "n" : 0
      }
  ],
  "vin" : [
      {
          "vout" : 0,
          "txid" : "0xa7873afc5439140818bec9a10af5117ed09d9e07d5bf0a28897f22618fdfae31"
      }
  ],
  "attributes" : [],
  "__v" : 0
}

*/