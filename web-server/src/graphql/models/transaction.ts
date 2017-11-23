/**
 * Filename: /Users/wei/Desktop/otcgo/neo_wallet_analysis/web-server/src/graphql/models/transaction.ts
 * Path: /Users/wei/Desktop/otcgo/neo_wallet_analysis/web-server
 * Created Date: Thursday, November 23rd 2017, 4:31:52 pm
 * Author: qknow
 *
 * Copyright (c) 2017 otcgo.cn
 */

import * as graphql from 'graphql'

const transaction  = new graphql.GraphQLObjectType({
  name: 'transaction',
  description: 'This is a transaction',
  fields: {
    _id: {
      type: graphql.GraphQLString
    },
    contract: {
      type: graphql.GraphQLString
    },
    address: {
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

export { transaction }