import { mongoose } from '../lib'
import * as timestamps from 'mongoose-timestamp'


const baseSchema = {
  txid: String,  // txid
  to: String,  // 转入地址
  from: String, // 输出地址
  value: Number, // 金额
  blockIndex: String, // 区块
  operation: String, // 操作,
  contract: String,  // contract
}

const address = new mongoose.Schema(baseSchema, {
  collection: 'nep5_m_transactions',
  strict: false
})

address.plugin(timestamps, {
  createdAt: 'createdAt',
  updatedAt: 'updatedAt'
})

const Address = mongoose.model('Address', address)



export { Address }