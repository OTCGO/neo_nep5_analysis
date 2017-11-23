import * as graphql from 'graphql'
import { address, transaction } from './models'
import { Address, Transaction } from '../models'
import { queryBuilder, argsBuilder } from '../utils'


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
        }
      }),
      async resolve (root, args) {
        const query = Address.find()
        queryBuilder(query, args)
        const rows = await query.lean().exec()
        const count = await query.count().exec()
        return {
          count,
          rows
        }
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
        }
      }),
      async resolve (root, args) {
        const query = Transaction.find()
        queryBuilder(query, args)
        const rows = await query.lean().exec()
        const count = await query.count().exec()
        return {
          count,
          rows
        }
      }
    }
  }
})

export default query