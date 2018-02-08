/**
 * Filename: /Users/wei/Desktop/otcgo/neo_wallet_analysis/web-server/src/graphql/models/address.ts
 * Path: /Users/wei/Desktop/otcgo/neo_wallet_analysis/web-server
 * Created Date: Thursday, November 23rd 2017, 4:31:49 pm
 * Author: qknow
 *
 * Copyright (c) 2017 otcgo.cn
 */


import * as graphql from 'graphql'
// import { getAssetState } from '../../services'
import * as config from 'config'

const asset = new graphql.GraphQLObjectType({
  name: 'assets',
  description: 'This is a assets',
  fields: {
    _id: {
      type: graphql.GraphQLString
    },
    assetId: {
      type: graphql.GraphQLString
    },
    contract: {
      type: graphql.GraphQLString
    },
    symbol: {
        type: graphql.GraphQLString
    },
    type: {
      type: graphql.GraphQLString,
      async resolve (asset) {
        if (asset.contract) {
          return 'nep5'
        }
      }
    },
    name: {
      type: graphql.GraphQLString,
      async resolve (assets) {
       // console.log('assetssss', assets)
        if (assets.assetId) {
          return config.get(`asserts.${assets.assetId}`)
         // const result = await getAssetState(assets.assetId)
         // console.log('result', result)
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

export { asset }