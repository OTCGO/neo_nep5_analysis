"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const graphql = require("graphql");
const argsBuilder = (args) => {
    const defaultArgs = {
        _id: {
            type: graphql.GraphQLString
        },
        skip: {
            type: graphql.GraphQLInt,
            defaultValue: 0
        },
        limit: {
            type: graphql.GraphQLInt,
            defaultValue: 20
        },
        sort: {
            type: graphql.GraphQLString
        }
    };
    return Object.assign({}, defaultArgs, args);
};
exports.argsBuilder = argsBuilder;
//# sourceMappingURL=argsBuilder.js.map