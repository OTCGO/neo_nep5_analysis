#coding:utf8
import binascii
from base58 import b58decode
from decimal import Decimal as D
from AntShares.Core.TransactionInput import TransactionInput
from AntShares.Core.TransactionOutput import TransactionOutput
from AntShares.Cryptography.Helper import scripthash_to_address
from .Browser import Browser

class AntAddress(object):
    def __init__(self,address):
        self.address = address
        self.scripthash = self.address_to_scriptHash(self.address)
        self.raw_info = self.get_baseinfo()
        self.balances = self.raw_info['balances']
        self.utxo= self.raw_info['utxo']

    @staticmethod
    def address_to_scriptHash(address):
        return binascii.hexlify(b58decode(address)[1:-4])

    def get_baseinfo(self):
        r = Browser().address(self.address)
        if r:
            for au in r['utxo'].keys():
                for i in xrange(len(r['utxo'][au])):
                    r['utxo'][au][i]['value'] = D(r['utxo'][au][i]['value'])
            return r
        else:
            return {'balances':{}, 'utxo':{}}

    def get_asset_balance(self, assetid):
        if self.balances.has_key(assetid):
            return D(self.balances[assetid])
        else:
            return D('0')

    def get_high(self, value):
        s = bin(int(value)*10**8)
        if 34 >= len(s):
            return 0
        else:
            return int(s[:-32],2)

    def get_low(self, value):
        s = bin(int(value)*10**8)
        if len(s)-2 >= 32:
            return int(s[-32:],2)
        else:
            return int(s[2:],2)

    def print_transaction(self,inputs,outputs):
        s = """{"vin":[{"""
        for y in xrange(len(inputs)):
            i = inputs[y]
            if y > 0:
                s += ''',{'''
            s += '''"txid":"%s","vout":%s}''' % (i.prevHash, i.prevIndex)
        else:
            s += '''],"vout":[{'''
        for x in xrange(len(outputs)):
            o = outputs[x]
            if x > 0:
                s += ''',{'''
            s += '''"n":%s,"asset":"%s","value":"%s","high":%s,"low":%s,"address":"%s"}''' % (x,o.AssetId,o.Value,self.get_high(o.Value),self.get_low(o.Value),scripthash_to_address(o.ScriptHash))
        else:
            s += '''],"change_address":"%s"}''' % (self.address)
        #print '---prtty transaction---\n',s
    def get_right_utxo(self, value, asset):
        '''
        utxo选取原则:
            1.如果所有utxo相加后小于该金额,返回空
            2.排序
            3.如果存在正好等于该金额的,就取该utxo
            4.如果存在大于该金额的,就取大于该金额的最小的utxo
            5.取最大的utxo并移除,然后回到第3步以获取剩余金额的utxo
        '''
        #print self.address,asset,'\n',self.utxo[asset]
        result = []
        if not self.utxo[asset]:
            return result
        max_utxo = reduce(lambda a,b:a+b, [i['value'] for i in self.utxo[asset]])
        if max_utxo < value:
            return result
        utxos = self.utxo[asset][:]
        sorted_utxos = sorted(utxos, cmp=lambda a,b:cmp(a['value'],b['value'])) #sort little --> big
        while value:
            if value in [s['value'] for s in sorted_utxos]:
                for s in sorted_utxos:
                    if value == s['value']:
                        result.append(s)
                        value = D('0')
                        break
            elif value < sorted_utxos[-1]['value']:
                for s in sorted_utxos:
                    if value < s['value']:
                        result.append(s)
                        value = D('0')
                        break
            else:
                result.append(sorted_utxos[-1])
                value = value - sorted_utxos[-1]['value']
                del sorted_utxos[-1]
        return result

    def get_transactions(self, value, asset, tx_address):
        '''生成交易输入与输出'''
        if not isinstance(value, D):
            value = D(str(value))
        inputs = []
        outputs = []
        right_utxo = self.get_right_utxo(value, asset)
        #print '-'*10,right_utxo
        assert right_utxo
        for r in right_utxo:
            inputs.append(TransactionInput(prevHash=r['prevHash'], prevIndex=r['prevIndex']))
        outputs.append(TransactionOutput(AssetId=asset,Value=value, ScriptHash=self.address_to_scriptHash(tx_address)))
        return_value = sum([i['value'] for i in right_utxo]) - value
        if return_value:
            outputs.append(TransactionOutput(AssetId=asset,Value=return_value, ScriptHash=self.scripthash))
        #self.print_transaction(inputs, outputs)
        return inputs,outputs

    def get_multi_transactions(self, items, asset):
        '''生成交易输入与输出,输出为多方'''
        inputs = []
        outputs = []
        value = sum([i[1] for i in items])
        if not isinstance(value, D):
            value = D(str(value))
        #print '---contract address:%s,asset:%s,value:%s' % (self.address,asset,value)
        right_utxo = self.get_right_utxo(D(str(value)), asset)
        assert right_utxo
        for r in right_utxo:
            inputs.append(TransactionInput(prevHash=r['prevHash'], prevIndex=r['prevIndex']))
        for i in items:
            outputs.append(TransactionOutput(AssetId=asset,Value=i[1], ScriptHash=self.address_to_scriptHash(i[0])))
        return_value = sum([i['value'] for i in right_utxo]) - value
        if return_value:
            outputs.append(TransactionOutput(AssetId=asset,Value=return_value, ScriptHash=self.scripthash))
        self.print_transaction(inputs, outputs)
        return inputs,outputs
