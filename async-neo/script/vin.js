/**
 * Filename: /Users/wei/Desktop/otcgo/neo_wallet_analysis/async-neo/script/vin.js
 * Path: /Users/wei/Desktop/otcgo/neo_wallet_analysis/async-neo
 * Created Date: Monday, February 12th 2018, 7:39:21 pm
 * Author: qknow
 *
 * Copyright (c) 2018 Your Company
 *
 * async vin info script
 */

const MongoClient = require('mongodb').MongoClient
const ObjectId = require('mongodb').ObjectID
const config = require('config')

console.log('config', config.get('mongo'))
// Connection URL
// const url = config.get('mongo')

const url = 'mongodb://127.0.0.1:27017'
// const url = 'mongodb://otcgo:u3fhhrPr@114.215.30.71:27017/?authSource=admin'

const dbName = 'neo-main'
// Use connect method to connect to the server

function main () {
// Use connect method to connect to the Server passing in
// additional options
  MongoClient.connect(url, (err, client) => {
    console.log('err', err)
    console.log('Connected correctly to server')
    if (err) return client.close()

    const db = client.db(dbName)
    const transactions = db.collection('b_neo_m_transactions')

    let stream = transactions.find({
      $or: [
       {'vin.$.utxo': {$exists: false}},
        {'vin.$.utxo.address': {$exists: false}}
      ]

    }).sort({'blockIndex': -1})
    stream.on('data', async (d) => {
      console.log('d', d.blockIndex)
      for (let i = 0; i < d.vin.length; i++) {
        if (d.vin[i]) {
          let result = await client.db(dbName).collection('b_neo_m_transactions').findOne({txid: d.vin[i].txid})
            // console.log('result', result)
          if (result) {
            d.vin[i].utxo = d.vin[i].vout ? result.vout[d.vin[i].vout] : {}
          }
        }
         // console.log('d.vin[i].utxo', d.vin[i].utxo)
      }
        // console.log('d', d.vin)

      // console.log('d', d.vin)
      transactions.updateOne({
        '_id': ObjectId(d._id)
      }, {
        $set: {
          'vin': d.vin || []
        }
      })
    })
    stream.on('end', () => {
      console.log('end')
    })
  })
}

setInterval(main, 30000)
