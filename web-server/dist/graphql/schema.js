"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const graphql = require("graphql");
const query_1 = require("./query");
const schema = new graphql.GraphQLSchema({
    query: query_1.default
});
exports.default = schema;
//# sourceMappingURL=schema.js.map