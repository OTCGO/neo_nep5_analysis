#coding:utf8
import binascii
from AntShares.Fixed8 import Fixed8
from AntShares.Helper import big_or_little
from AntShares.Core.Scripts.ScriptOp import ScriptOp
from AntShares.Core.Scripts.ScriptBuilder import ScriptBuilder
from AntShares.Cryptography.Helper import scripthash_to_address,redeem_to_scripthash
from OTCGO.settings import APPHASH

class AddContract:
    @staticmethod
    def get_redeem_hex(a, b):
        '''创建代理合约脚本'''
        sb = ScriptBuilder()
        sb.push(Fixed8(a).getDataFree())
        sb.push(Fixed8(b).getDataFree())
        sb.add(ScriptOp().OP_APPCALL)
        sb.add(binascii.unhexlify(big_or_little('e04035601ea4a2d4cf679cdd10c2ca133856346d')))
        return sb.toArray()
    @classmethod
    def get_address(cls,a,b):
        '''生成代理地址'''
        script = cls.get_redeem_hex(a,b)
        hash_script = redeem_to_scripthash(binascii.unhexlify(script))
        address = scripthash_to_address(hash_script)
        return address
