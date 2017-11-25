#! /usr/bin/env python
# coding: utf-8
# qknow@蓝鲸淘
# Licensed under the MIT License.

import pymongo
from AntShares.Wallets.Wallet import Wallet
import binascii
from time import strftime, gmtime
from AntShares.Fixed8 import Fixed8


class NEP5Handler(object):
    def __init__(self, args):
        # print args.db
        self.client = pymongo.MongoClient('mongodb://' + args.mongodb + '/')
        self.db = self.client[args.db]
        # self.collection = self.db.nep5
        self.wallet = Wallet()

    def transfer(self, obj):
            # print obj['state']['value'][0]['value']
        result = self.db['nep5_m_transactions'].find_one({
            "txid": obj['txid'],
            "from": self.wallet.toAddress(obj['state']['value'][1]['value']),
            "to": self.wallet.toAddress(obj['state']['value'][2]['value'])
        })
        # print result
        if result is None:
            self.db['nep5_m_transactions'].insert_one({
                "blockIndex": obj['blockIndex'],
                "txid": obj['txid'],
                "contract": obj['contract'],
                "operation": binascii.unhexlify(obj['state']['value'][0]['value']),
                # 转出
                "from": self.wallet.toAddress(obj['state']['value'][1]['value']),
                # 输入
                "to": self.wallet.toAddress(obj['state']['value'][2]['value']),
                "value": Fixed8.getNumStr(obj['state']['value'][3]['value']),
                'createdAt': strftime("%Y-%m-%d %H:%M:%S", gmtime()),
                'updatedAt': strftime("%Y-%m-%d %H:%M:%S", gmtime())
            })
            # from address
            address_form = self.db['nep5_m_addresses'].find_one({"address": self.wallet.toAddress(
                obj['state']['value'][1]['value'])})

            if address_form is None:
                self.db['nep5_m_addresses'].insert_one({
                    "address": self.wallet.toAddress(obj['state']['value'][1]['value']),
                    "contract": obj['contract'],
                    'createdAt': strftime("%Y-%m-%d %H:%M:%S", gmtime()),
                    'updatedAt': strftime("%Y-%m-%d %H:%M:%S", gmtime())
                })

            # to
            address_to = self.db['nep5_m_addresses'].find_one({"address": self.wallet.toAddress(
                obj['state']['value'][2]['value'])})

            if address_to is None:
                self.db['nep5_m_addresses'].insert_one({
                    "address": self.wallet.toAddress(obj['state']['value'][2]['value']),
                    "contract": obj['contract'],
                    'createdAt': strftime("%Y-%m-%d %H:%M:%S", gmtime()),
                    'updatedAt': strftime("%Y-%m-%d %H:%M:%S", gmtime())
                })

        else:
            print 'txid', obj['txid'], 'exist'
