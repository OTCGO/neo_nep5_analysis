/**
 * Filename: g:\project\airplake\mdc-v4\src\router.ts
 * Path: g:\project\airplake\mdc-v4
 * Created Date: Tuesday, August 29th 2017, 11:08:16 am
 * Author: Wy
 *
 * Copyright (c) 2017 Your Company
 */

import { Router } from 'express'
import { mainnet } from './modules/'

const router: Router = Router()

router.use('/mainnet', mainnet)
export default router
