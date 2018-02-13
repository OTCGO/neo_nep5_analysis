/**
 * Filename: /Users/wei/Desktop/otcgo/neo_scrapy/src/modules/rpx/rpx.ts
 * Path: /Users/wei/Desktop/otcgo/neo_scrapy
 * Created Date: Thursday, November 16th 2017, 12:14:47 am
 * Author: wei
 *
 * Copyright (c) 2017 Your Company
 */

import * as log4js from 'log4js'
import * as config from 'config'
import { Router } from 'express'
import { NRequest } from '../../interface'
import * as graphqlHTTP from 'express-graphql'
import { Request as WebHandler } from '../../utils'
// import {  Asset } from '../../models'
import schema from '../../graphql'
import { api } from '@cityofzion/neon-js'
import { parallel } from '../../utils/index'



const logger = log4js.getLogger('mainnet')
const mainnet: Router = Router()

mainnet.use(`/public/graphql`, graphqlHTTP({
  schema,
  graphiql: true,
  pretty: true,
  extensions ({
    documet,
    variables,
    operationName,
    result
  }) {
    if (result.errors) {
      result.error_code = 500
      result.error_msg = result.errors[0].message
      delete result.errors
      result.status = 'Error'
    } else {
      result.code = 200
      result.status = 'OK'
      result.server_time = new Date()
    }
  }
}))


mainnet.get(`/address/balances/:address`,  async (req: NRequest, res: any)  => {
     try {
      // const { address } = req.params
      // logger.info('address', address)
      // logger.info('rpc', config.get('rpc'))
      // // const result = await api.nep5.getTokenBalance(config.get('rpc'), '0d821bd7b6d53f5c2b40e217c6defc8bbe896cf5', 'ARGpitrDs1rcynXmBd6JRgvEJ8PLSetFiW')
      // // logger.info('result', result)
      // const asset: any = await Asset.find()
      // logger.info('asset', asset)
      // const arr = []
      // asset.forEach(item => {
      //     arr.push(async () => {
      //       const balances = await api.nep5.getTokenBalance(config.get('rpc'), item.contract.substring(2), address)
      //       return {
      //         _id: item._id,
      //         updatedAt: item.updatedAt,
      //         contract: item.contract,
      //         createdAt: item.createdAt,
      //         symbol: item.symbol,
      //         balances
      //       }
      //     })
      // })
      // const result = await parallel(arr, 10)
      // logger.info('asset', result)
      return res.apiSuccess('ok')

    } catch (error) {
      logger.error('mainnet', error)
      return res.apiError(error)
    }
  })

export { mainnet }



