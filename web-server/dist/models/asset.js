"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const lib_1 = require("../lib");
const timestamps = require("mongoose-timestamp");
const baseSchema = {
    symbol: String,
    contract: String,
};
const asset = new lib_1.mongoose.Schema(baseSchema, {
    collection: 'nep5_m_assets',
    strict: false
});
asset.plugin(timestamps, {
    createdAt: 'createdAt',
    updatedAt: 'updatedAt'
});
const Asset = lib_1.mongoose.model('Asset', asset);
exports.Asset = Asset;
//# sourceMappingURL=asset.js.map