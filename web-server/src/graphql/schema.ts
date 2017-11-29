import * as graphql from 'graphql'
import query from './query'


const schema = new graphql.GraphQLSchema({
  query
})

export default schema



