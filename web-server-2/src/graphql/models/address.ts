/**
 * Filename: /Users/wei/Desktop/otcgo/neo_wallet_analysis/web-server/src/graphql/models/address.ts
 * Path: /Users/wei/Desktop/otcgo/neo_wallet_analysis/web-server
 * Created Date: Thursday, November 23rd 2017, 4:31:49 pm
 * Author: qknow
 *
 * Copyright (c) 2017 otcgo.cn
 */


import * as graphql from 'graphql'
import {  Asset } from '../../models'

const address = new graphql.GraphQLObjectType({
  name: 'addresses',
  description: 'This is a address',
  fields: {
    _id: {
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

export { address }