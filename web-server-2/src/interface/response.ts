/**
 * Filename: /Users/wei/Desktop/otcgo/neo_wallet_analysis/web-server/src/interface/request.ts
 * Path: /Users/wei/Desktop/otcgo/neo_wallet_analysis/web-server
 * Created Date: Tuesday, November 28th 2017, 9:53:19 pm
 * Author: qknow
 *
 * Copyright (c) 2017 otcgo.cn
 */


import { Response } from 'express'

export interface NResponse extends Response {
    apiSuccess: Function,
    apiError: Function
}


