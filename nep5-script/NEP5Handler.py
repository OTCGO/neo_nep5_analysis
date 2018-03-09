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
        print args.mongodb
        print args.db
        # self.client = pymongo.MongoClient('mongodb://' + args.mongodb)
        # self.db = pymongo.MongoClient('mongodb://otcgo:u3fhhrPr@114.215.30.71:27017/?authSource=admin&replicaSet=rs1')['neo-otcgo']
        # self.collection = self.db.nep5
        # self.db = pymongo.MongoClient('mongodb://otcgo:u3fhhrPr@127.0.0.1:27017/?authSource=admin&replicaSet=rs1')  
        self.db = pymongo.MongoClient(args.mongodb)[args.db]
        self.wallet = Wallet()

    def handle_data(self,blockIndex,data):
        transfer = '7472616e73666572'
        if data is not None:
            for item in data:
                # print type(item)
                # print item['txid']
               
                if item['state']['value'][0]['value'] == transfer:
                    result = self.db['nep5_m_transactions'].find_one({
                        "txid": item['txid']
                    })
                    if result is None:
                        for item_m in data:
                            item_m['blockIndex'] = blockIndex
                            if item_m['txid'] == item['txid']:
                                self.transfer(item_m)

    def transfer(self, obj):
        # print obj['state']['value'][0]['value']
        # url = 'http://127.0.0.1:10332'
        try:



            # url = 'http://seed2.neo.org:10332'
            url = 'http://114.215.30.71:10332'

           
            #  mintTokens
            if obj['state']['value'][1]['value'] == "":
                asserts = self.db['nep5_m_assets'].find_one({
                    "contract": obj['contract'],
                })
                print 'asserts', asserts
                # asserts
                if asserts is None:
                    # rpc get symbol
                    print 'contract', type(obj['contract'])
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

                # result = self.db['nep5_m_transactions'].find_one({
                #     "txid": obj['txid'],
                #     "from": {
                #         "value": "",
                #         "hash": ""
                #     },
                #     "to": {
                #         "value": self.wallet.toAddress(
                #             obj['state']['value'][2]['value']),
                #         "hash": obj['state']['value'][2]['value']
                #     }
                # })

                # print 'nep5_m_transactions', result
                # if result is None:
                    # print 'blockIndex', obj['blockIndex']
                    #  rpc block_time
                    # block_time = requests.post(url, json={
                    #     "jsonrpc": "2.0",
                    #     "method": "getblock",
                    #     "params": [int(obj['blockIndex']), 1],
                    #     "id": 1
                    # })

                    # print 'block_time', block_time.json()

                self.db['nep5_m_transactions'].insert_one({
                    "blockIndex": obj['blockIndex'],
                    "txid": obj['txid'],
                    "contract": obj['contract'],
                    "operation": 'mintTokens',
                    # 转出
                    "from": {
                        "value": "",
                        "hash": ""
                    },
                    # 输入
                    "to": {
                        "value": self.wallet.toAddress(
                            obj['state']['value'][2]['value']),
                        "hash": obj['state']['value'][2]['value'],
                    },
                    "value": Fixed8.getNumStr(obj['state']['value'][3]['value']),
                    'createdAt': str(obj['time']),
                    'updatedAt': str(obj['time'])
                })

                # to
                address_to = self.db['nep5_m_addresses'].find_one({"address.value": self.wallet.toAddress(
                    obj['state']['value'][2]['value'])})

                if address_to is None:
                    self.db['nep5_m_addresses'].insert_one({
                        "address": {
                            "value": self.wallet.toAddress(obj['state']['value'][2]['value']),
                            "hash": obj['state']['value'][2]['value']
                        },
                        "contract": obj['contract'],
                        'createdAt': str(obj['time']),
                        'updatedAt': str(obj['time'])
                    })

            # transferred
            if obj['state']['value'][1]['value'] != "" and obj['state']['value'][2]['value'] != '':
                # print 'tt'

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

                # result = self.db['nep5_m_transactions'].find_one({
                #     "txid": obj['txid'],
                #     "from": {
                #         "value": self.wallet.toAddress(obj['state']['value'][1]['value']),
                #         "hash": obj['state']['value'][1]['value']
                #     },
                #     "to": {
                #         "value": self.wallet.toAddress(
                #             obj['state']['value'][2]['value']),
                #         "hash": obj['state']['value'][2]['value']
                #     }
                # })

                # print 'nep5_m_transactions', result
                # if result is None:
                #     print 'blockIndex', obj['blockIndex']
                    #  rpc block_time
                    # block_time = requests.post(url, json={
                    #     "jsonrpc": "2.0",
                    #     "method": "getblock",
                    #     "params": [int(obj['blockIndex']), 1],
                    #     "id": 1
                    # })

                    # print 'block_time', block_time.json()

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
                    'createdAt': str(obj['time']),
                    'updatedAt': str(obj['time'])
                })
                

                # from address
                address_form = self.db['nep5_m_addresses'].find_one({"address.value": self.wallet.toAddress(
                    obj['state']['value'][1]['value'])})

                print 'address_form', address_form
                if address_form is None:
                    self.db['nep5_m_addresses'].insert_one({
                        "address":  {
                            "value": self.wallet.toAddress(obj['state']['value'][1]['value']),
                            "hash": obj['state']['value'][1]['value']
                        },
                        "contract": obj['contract'],
                        'createdAt': str(obj['time']),
                        'updatedAt': str(obj['time'])
                    })

                # to
                address_to = self.db['nep5_m_addresses'].find_one({"address.value": self.wallet.toAddress(
                    obj['state']['value'][2]['value'])})

                print 'address_to', address_to
                if address_to is None:
                    self.db['nep5_m_addresses'].insert_one({
                        "address": {
                            "value": self.wallet.toAddress(obj['state']['value'][2]['value']),
                            "hash": obj['state']['value'][2]['value']
                        },
                        "contract": obj['contract'],
                        'createdAt': str(obj['time']),
                        'updatedAt': str(obj['time'])
                    })

        except Exception as e:
            print e
