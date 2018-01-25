import { mongoose } from '../lib'
import * as timestamps from 'mongoose-timestamp'


const baseSchema = {
  contract: String,  // contract
  address: {
    value: String,
    hash: String
  },
  createdAt: String,
  updatedAt: String
}

const address = new mongoose.Schema(baseSchema, {
  collection: 'nep5_m_addresses',
  strict: false
})

// address.plugin(timestamps, {
//   createdAt: 'createdAt',
//   updatedAt: 'updatedAt'
// })

const Address = mongoose.model('Address', address)



export { Address }