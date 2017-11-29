"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const lib_1 = require("../lib");
const timestamps = require("mongoose-timestamp");
const baseSchema = {
    contract: String,
    address: {
        value: String,
        hash: String
    }
};
const address = new lib_1.mongoose.Schema(baseSchema, {
    collection: 'nep5_m_addresses',
    strict: false
});
address.plugin(timestamps, {
    createdAt: 'createdAt',
    updatedAt: 'updatedAt'
});
const Address = lib_1.mongoose.model('Address', address);
exports.Address = Address;
//# sourceMappingURL=address.js.map