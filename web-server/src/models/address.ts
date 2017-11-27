import { mongoose } from '../lib'
import * as timestamps from 'mongoose-timestamp'


const baseSchema = {
  contract: String,  // contract
  address: String,  // 转入地址
}

const address = new mongoose.Schema(baseSchema, {
  collection: 'nep5_m_addresses',
  strict: false
})

address.plugin(timestamps, {
  createdAt: 'createdAt',
  updatedAt: 'updatedAt'
})

const Address = mongoose.model('Address', address)



export { Address }