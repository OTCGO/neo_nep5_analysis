import * as graphql from 'graphql'

const  argsBuilder = (args) => {
  const defaultArgs = {
    _id: {
      type: graphql.GraphQLString
    },
    limit: {
      type: graphql.GraphQLInt
    },
    offset: {
      type: graphql.GraphQLInt
    },
    sort: {
      type: graphql.GraphQLString
    }
  }

  return {...defaultArgs, ...args}
}

export { argsBuilder }