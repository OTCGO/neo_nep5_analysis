import { mongoose } from '../lib'
import * as timestamps from 'mongoose-timestamp'

const baseSchema = {
    contract: String,  // contract
    address: String,  // 转入地址
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