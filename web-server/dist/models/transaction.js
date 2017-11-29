"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const lib_1 = require("../lib");
const timestamps = require("mongoose-timestamp");
const baseSchema = {
    txid: String,
    to: {
        value: String,
        hash: String
    },
    from: {
        value: String,
        hash: String
    },
    value: String,
    blockIndex: String,
    operation: String,
    contract: String,
};
const transaction = new lib_1.mongoose.Schema(baseSchema, {
    collection: 'nep5_m_transactions',
    strict: false
});
transaction.plugin(timestamps, {
    createdAt: 'createdAt',
    updatedAt: 'updatedAt'
});
const Transaction = lib_1.mongoose.model('Transaction', transaction);
exports.Transaction = Transaction;
//# sourceMappingURL=transaction.js.map