#coding:utf8
import binascii
from AntShares.Fixed8 import Fixed8
from AntShares.Helper import big_or_little
from AntShares.Core.Scripts.ScriptOp import ScriptOp
from AntShares.Core.Scripts.ScriptBuilder import ScriptBuilder
from AntShares.Cryptography.Helper import scripthash_to_address,redeem_to_scripthash
from OTCGO.settings import APPHASH
from decimal import Decimal as D

class LockContract:
    @staticmethod
    def get_redeem_hex(client, timestamp):
        '''创建代理合约脚本'''
        sb = ScriptBuilder()
        sb.push(client)
        sb.push(Fixed8(timestamp).getDataFree())
        sb.add(ScriptOp().OP_APPCALL)
        sb.add(binascii.unhexlify(big_or_little('898f810b3881ec021a6282883abe78fa207e9316')))
        return sb.toArray()
    @classmethod
    def get_address(cls,client,timestamp):
        '''生成代理地址'''
        script = cls.get_redeem_hex(client,timestamp)
        hash_script = redeem_to_scripthash(binascii.unhexlify(script))
        address = scripthash_to_address(hash_script)
        return address


if __name__ == "__main__":
    client = '0383cdbc3f4d2213043c19d6bd041c08fbe0a3bacd43ef695500a1b33c609a9e8a'
    agent = '039b2c6b8a8838595b8ebcc67bbc85cec78d805d56890e9a0d71bcae89664339d6'
    assetid = '602c79718b16e442de58778e148d0b1084e3b2dffd5de6b7b16cee7969282de7'
    valueassetid = '5fd33b8d1ff8185b30f59c35313e60663d026eb8351d0dd9fd6f60eb279b301a'
    way = True
    timestamp = 1.001
    contract_address = AgencyContract.get_address(client,timestamp)
    print '---Lock Contract Address---:',contract_address
