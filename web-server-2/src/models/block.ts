import { mongoose } from '../lib'
// import * as timestamps from 'mongoose-timestamp'



const baseSchema = {
    hash: String,
    size: Number,
    version: Number,
    previousblockhash: String,
    merkleroot: String,
    time: Number, // 时间
    index: Number, // 高度
    nonce: String,
    nextconsensus: String,
    script: {
        invocation: String,
        verification: String
    },
    tx: [ // tx.length  交易数

    ],
    confirmations: Number,
    nextblockhash: String
}

const block = new mongoose.Schema(baseSchema, {
    collection: 'nep5_m_blocks',
    strict: false
})

// block.plugin(timestamps, {
//   createdAt: 'createdAt',
//   updatedAt: 'updatedAt'
// })


const Block = mongoose.model('Block', block)



export { Block }