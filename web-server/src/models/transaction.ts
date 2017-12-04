import { mongoose } from '../lib'
import * as timestamps from 'mongoose-timestamp'



const baseSchema = {
  txid: String,  // txid
  to: {
    value: String,  // 转入地址
    hash: String
  },
  from: {
    value: String,  // 转出地址
    hash: String
  },
  value: String, // 金额
  blockIndex: String, // 区块
  operation: String, // 操作,
  contract: String,  // contract
  createdAt: String,
  updatedAt: String
}

const transaction = new mongoose.Schema(baseSchema, {
  collection: 'nep5_m_transactions',
  strict: false
})

// transaction.plugin(timestamps, {
//   createdAt: 'createdAt',
//   updatedAt: 'updatedAt'
// })


const Transaction = mongoose.model('Transaction', transaction)



export { Transaction }