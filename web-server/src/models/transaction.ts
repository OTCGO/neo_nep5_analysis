import { mongoose } from '../lib'
import * as timestamps from 'mongoose-timestamp'



const baseSchema = {
  txid: String,  // txid
  to: String,  // 转入地址
  from: String, // 输出地址
  value: String, // 金额
  blockIndex: String, // 区块
  operation: String, // 操作,
  contract: String,  // contract
}

const transaction = new mongoose.Schema(baseSchema, {
  collection: 'nep5_m_transactions',
  strict: false
})

transaction.plugin(timestamps, {
  createdAt: 'createdAt',
  updatedAt: 'updatedAt'
})


const Transaction = mongoose.model('Transaction', transaction)



export { Transaction }