/**
 * Filename: /Users/wei/Desktop/otcgo/neo_wallet_analysis/web-server/src/utils/pageQuery.ts
 * Path: /Users/wei/Desktop/otcgo/neo_wallet_analysis/web-server
 * Created Date: Sunday, November 26th 2017, 12:14:02 pm
 * Author: qknow
 *
 * Copyright (c) 2017 otcgo.cn
 */


import async from 'async'
import { resolve } from 'url'

const pageQuery = function (skip = 0, limit = 20, Model, populate= {}, queryParams= {}, sortParams = {createdAt: 'desc'}) {
  console.log('queryParams', queryParams)
  return new Promise((resolve, reject) => {
    const $page = {
      rows: [],
      count: 0
    }
    async.parallel({
      count (done) {  // 查询数量
        Model.count(queryParams).exec(function (err, count) {
          done(err, count)
        })
      },
      records (done) {   // 查询一页的记录
        Model.find(queryParams).skip(skip).limit(limit).populate(populate).sort(sortParams).exec(function (err, doc) {
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

