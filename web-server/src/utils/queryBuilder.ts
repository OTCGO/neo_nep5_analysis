/**
 * Filename: /Users/wei/Desktop/otcgo/neo_wallet_analysis/web-server/src/utils/queryBuilder.ts
 * Path: /Users/wei/Desktop/otcgo/neo_wallet_analysis/web-server
 * Created Date: Thursday, November 23rd 2017, 7:33:06 pm
 * Author: qknow
 *
 * Copyright (c) 2017 otcgo.cn
 */

const queryBuilder = (query, args) => {

    if ('sort' in args) {
      query = query.sort(args.sort)
    }

    if ('limit' in args) {
      query = query.limit(parseInt(args.limit))
    }

    if ('offset' in args) {
      query = query.skip(parseInt(args.offset))
    }

    delete args.sort
    delete args.limit
    delete args.offset
    delete args.key
    query = query.where(args)

    return query
  }

  export { queryBuilder }