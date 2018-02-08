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
      return new Promise<string>((resolve, reject) => {
        request(options, function (error, response, body) {
          if (error) return reject(error)
          return resolve(body)
        })
      })
}



export { getAssetState }