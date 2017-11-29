"use strict";
/**
 * Filename: g:\project\airplake\mdc-v4\src\router.ts
 * Path: g:\project\airplake\mdc-v4
 * Created Date: Tuesday, August 29th 2017, 11:08:16 am
 * Author: Wy
 *
 * Copyright (c) 2017 Your Company
 */
Object.defineProperty(exports, "__esModule", { value: true });
const express_1 = require("express");
const _1 = require("./modules/");
const router = express_1.Router();
router.use('/nep5', _1.nep5);
exports.default = router;
//# sourceMappingURL=router.js.map