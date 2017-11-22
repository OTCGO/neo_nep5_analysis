/**
 * Filename: /Users/wei/Desktop/otcgo/neo_scrapy/src/modules/rpx/rpx.ts
 * Path: /Users/wei/Desktop/otcgo/neo_scrapy
 * Created Date: Thursday, November 16th 2017, 12:14:47 am
 * Author: wei
 *
 * Copyright (c) 2017 Your Company
 */

import * as log4js from 'log4js'

const logger = log4js.getLogger('rpx')
const { neo } = require('neo-js-blockchain')

// logger.info('rpx:neo', node())
const neoBlockchain = new neo('full', 'mainnet')
// logger.info('rpx', neoBlockchain)

export async function getRPX() {

    neoBlockchain.sync.start()
   // const blockCount = await new neoBlockchain.node().getBlockCount()

  // logger.info('rpx', await neoBlockchain.node.nodes[0].getBlockCount())
}