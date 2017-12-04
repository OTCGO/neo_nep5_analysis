#! /usr/bin/env python
# coding: utf-8
# qknow@蓝鲸淘
# Licensed under the MIT License.

import pymongo
from AntShares.Wallets.Wallet import Wallet
import binascii
import datetime
from AntShares.Fixed8 import Fixed8
import requests


class NEP5Handler(object):
    def __init__(self, args):
        # print args.db
        self.client = pymongo.MongoClient('mongodb://' + args.mongodb + '/')
        self.db = self.client[args.db]
        # self.collection = self.db.nep5
        self.wallet = Wallet()

    def transfer(self, obj):
            # print obj['state']['value'][0]['value']
        # url = 'http://127.0.0.1:10332'
        try:
            # url = 'http://seed2.neo.org:10332'
            url = 'http://127.0.0.1:10332'

            # transferred
            # not contain mintToken
            if obj['state']['value'][1]['value'] is "" and obj['state']['value'][2]['value'] is '':

                asserts = self.db['nep5_m_assets'].find_one({
                    "contract": obj['contract'],
                })

                print 'asserts', asserts
                # asserts
                if asserts is None:
                    # rpc get symbol
                    # print 'contract', type(obj['contract'])
                    r = requests.post(url, json={
                        "jsonrpc": "2.0",
                        "method": "invokefunction",
                        "params": [
                            obj['contract'],
                            "symbol",
                            []
                        ],
                        "id": 1
                    })

                    # print 'value', binascii.unhexlify(r.json()['result']['stack'][0]['value'])
                    self.db['nep5_m_assets'].insert_one({
                        "contract": obj['contract'],
                        "symbol": binascii.unhexlify(r.json()['result']['stack'][0]['value']),
                        'createdAt': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        'updatedAt': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    })

                result = self.db['nep5_m_transactions'].find_one({
                    "txid": obj['txid'],
                    "from": {
                        "value": self.wallet.toAddress(obj['state']['value'][1]['value']),
                        "hash": obj['state']['value'][1]['value']
                    },
                    "to": {
                        "value": self.wallet.toAddress(
                            obj['state']['value'][2]['value']),
                        "hash": obj['state']['value'][2]['value']
                    }
                })

                print 'nep5_m_transactions', result
                if result is None:
                    self.db['nep5_m_transactions'].insert_one({
                        "blockIndex": obj['blockIndex'],
                        "txid": obj['txid'],
                        "contract": obj['contract'],
                        "operation": binascii.unhexlify(obj['state']['value'][0]['value']),
                        # 转出
                        "from": {
                            "value": self.wallet.toAddress(obj['state']['value'][1]['value']),
                            "hash": obj['state']['value'][1]['value'],
                        },
                        # 输入
                        "to": {
                            "value": self.wallet.toAddress(
                                obj['state']['value'][2]['value']),
                            "hash": obj['state']['value'][2]['value'],
                        },
                        "value": Fixed8.getNumStr(obj['state']['value'][3]['value']),
                        'createdAt': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        'updatedAt': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    })
                    # from address
                    address_form = self.db['nep5_m_addresses'].find_one({"address": self.wallet.toAddress(
                        obj['state']['value'][1]['value'])})

                    if address_form is None:
                        self.db['nep5_m_addresses'].insert_one({
                            "address":  {
                                "value": self.wallet.toAddress(obj['state']['value'][1]['value']),
                                "hash": obj['state']['value'][1]['value']
                            },
                            "contract": obj['contract'],
                            'createdAt': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                            'updatedAt': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        })

                    # to
                    address_to = self.db['nep5_m_addresses'].find_one({"address": self.wallet.toAddress(
                        obj['state']['value'][2]['value'])})

                    if address_to is None:
                        self.db['nep5_m_addresses'].insert_one({
                            "address": {
                                "value": self.wallet.toAddress(obj['state']['value'][2]['value']),
                                "hash": obj['state']['value'][2]['value']
                            },
                            "contract": obj['contract'],
                            'createdAt': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                            'updatedAt': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        })

                else:
                    print 'txid', obj['txid'], 'exist'
        except Exception as e:
            print e
