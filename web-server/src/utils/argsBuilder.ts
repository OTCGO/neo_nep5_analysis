import * as graphql from 'graphql'

const  argsBuilder = (args) => {
  const defaultArgs = {
    _id: {
      type: graphql.GraphQLString
    },
    skip: {
      type: graphql.GraphQLInt,
      defaultValue: 0
    },
    limit: {
      type: graphql.GraphQLInt,
      defaultValue: 20
    },
    sort: {
      type: graphql.GraphQLString
    }
  }

  return {...defaultArgs, ...args}
}

export { argsBuilder }