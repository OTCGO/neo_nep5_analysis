"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
/**
 * 给res对象添加拓展的返回方法
 */
function APIOutputMiddleware(req, res, next) {
    // 相应api成功结果
    res.apiSuccess = (data) => {
        res.jsonp({
            status: 'OK',
            code: 200,
            data,
            server_time: new Date()
        });
    };
    // 相应api出错结果，err是一个Error对象
    res.apiError = (err) => {
        res.jsonp({
            status: 'Error',
            error_code: parseInt(err.code) || parseInt(err.err_code) || 500,
            error_msg: err.message || err.error_msg || err.toString() || 'Unknown Error',
            server_time: new Date()
        });
    };
    next();
}
exports.APIOutputMiddleware = APIOutputMiddleware;
//# sourceMappingURL=APIOutputMiddleware.js.map