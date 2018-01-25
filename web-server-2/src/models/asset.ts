import { mongoose } from '../lib'
import * as timestamps from 'mongoose-timestamp'



const baseSchema = {
  symbol: String,  // symbol
  contract: String,  // contract
  createdAt: String,
  updatedAt: String
}

const asset = new mongoose.Schema(baseSchema, {
  collection: 'nep5_m_assets',
  strict: false
})

// asset.plugin(timestamps, {
//   createdAt: 'createdAt',
//   updatedAt: 'updatedAt'
// })


const Asset = mongoose.model('Asset', asset)



export { Asset }