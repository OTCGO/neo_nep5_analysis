/**
 * Filename: /Users/wei/Desktop/otcgo/neo_wallet_analysis/web-server/src/utils/pageQuery.ts
 * Path: /Users/wei/Desktop/otcgo/neo_wallet_analysis/web-server
 * Created Date: Sunday, November 26th 2017, 12:14:02 pm
 * Author: qknow
 *
 * Copyright (c) 2017 otcgo.cn
 */

/**
 * Filename: /Users/wei/Desktop/otcgo/neo_wallet_analysis/web-server/src/utils/pageQuery.ts
 * Path: /Users/wei/Desktop/otcgo/neo_wallet_analysis/web-server
 * Created Date: Sunday, November 26th 2017, 12:14:02 pm
 * Author: qknow
 *
 * Copyright (c) 2017 otcgo.cn
 */

import async from 'async'


const pageQuery = function (skip = 0, limit = 20, Model, aggregate= [], queryParams= {}, sortParams: any = {createdAt: -1}, display: any= {}) {
  console.log('queryParams', queryParams)
  return new Promise((resolve, reject) => {
    const $page = {
      rows: [],
      count: 0
    }
    async.parallel({
      count (done) {  // 查询数量
        Model.find(queryParams).count(function (err, count) {
         // console.log('doc', count)
          done(err, count)
        })
      },
      records (done) {   // 查询一页的记录
        if (!limit) {
         return Model.find(queryParams, display).skip(skip).sort(sortParams).toArray(function (err, doc) {
            done(err, doc)
          })
        }
        // aggregate(aggregate)
        return Model.find(queryParams, display).skip(skip).limit(limit).sort(sortParams).toArray(function (err, doc) {
          done(err, doc)
        })
      }
    }, function (err, results) {
      if (err) return reject(err)
      $page.count = results.count
      $page.rows = results.records
      return resolve($page)
    })
  })

}

export { pageQuery}

