const request = require('request')
import * as config from 'config'

const getAssetState = async (assetId) => {
    const options = {
        method: 'POST',
        url: config.get('rpc'),
        headers:
        {
          'content-type': 'application/json'
        },
        body: {
          jsonrpc: '2.0', method: 'getassetstate', params: [assetId], id: 1
        },
        json: true
      }
      return function (callback) {
        request(options, function (error, response, body) {
          if (error) return callback(error)
          return callback(undefined, {...body})
        })
      }
}


export { getAssetState }