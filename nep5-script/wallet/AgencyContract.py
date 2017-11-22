#coding:utf8
import binascii
from AntShares.Fixed8 import Fixed8
from AntShares.Helper import big_or_little
from AntShares.Core.Scripts.ScriptOp import ScriptOp
from AntShares.Core.Scripts.ScriptBuilder import ScriptBuilder
from AntShares.Cryptography.Helper import scripthash_to_address,redeem_to_scripthash
from decimal import Decimal as D

class AgencyContract:
    @staticmethod
    def get_redeem_hex(client, agent, assetId, valueId, way, price, apphash):
        '''创建代理合约脚本'''
        sb = ScriptBuilder()
        if False == way and price in [D('0.1'),D('0.09')]:
            sb.push(Fixed8(price).getData())
        else:
            sb.push(Fixed8(price).getDataFree())
        sb.push(1 if way else 0)
        sb.push(client)
        sb.push(big_or_little(valueId))
        sb.push(big_or_little(assetId))
        sb.push(agent)
        sb.add(ScriptOp().OP_APPCALL)
        #8a4d2865d01ec8e6add72e3dfdd20c12f44834e3  ce3a97d7cfaa770a5e51c5b12cd1d015fbb5f87d
        sb.add(binascii.unhexlify(big_or_little(apphash)))
        return sb.toArray()
    @classmethod
    def get_address(cls,client,agent,assetid,valueassetid,way,price,apphash):
        '''生成代理地址'''
        script = cls.get_redeem_hex(client, agent, assetid, valueassetid, way, price, apphash)
        hash_script = redeem_to_scripthash(binascii.unhexlify(script))
        address = scripthash_to_address(hash_script)
        return address
