import { mongoose } from '../lib'
import * as timestamps from 'mongoose-timestamp'



const baseSchema = {
  symbol: String,  // symbol
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


const Asset = mongoose.model('Transaction', transaction)



export { Asset }