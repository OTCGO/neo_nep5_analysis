# coding:utf8
import ecdsa
import hashlib
import requests
import binascii
import base64
from time import sleep
from decimal import Decimal as D
from django.db import transaction
from AntShares.Fixed8 import Fixed8
from AntShares.Helper import big_or_little
from AntShares.Wallets.Contract import Contract
from AntShares.Network.RemoteNode import RemoteNode
from AntShares.IO.MemoryStream import MemoryStream
from AntShares.IO.BinaryWriter import BinaryWriter
from AntShares.Core.Transaction import Transaction
from AntShares.Core.Scripts.ScriptOp import ScriptOp
from AntShares.Core.TransactionInput import TransactionInput
from AntShares.Core.TransactionOutput import TransactionOutput
from AntShares.Core.Scripts.ScriptBuilder import ScriptBuilder
from AntShares.Cryptography.Helper import get_privkey_format, decode_privkey, encode_pubkey, fast_multiply, G, scripthash_to_address, bin_dbl_sha256, redeem_to_scripthash
from OTCGO.settings import RPC_NODE, RPC_NODE2, AGENT_PRIKEY, AGENT_PUBKEY, APPHASH as appHash, TESTNET
from .AgencyContract import AgencyContract
from .AntAddress import AntAddress
from .Browser import Browser
from .models import *


class WalletTool:
    @staticmethod
    def get_prev_index(txid, address, assetId):
        result = Browser().transaction(txid)['vout']
        for r in result:
            if address == r['address'] and assetId == r['asset']:
                return r['n']
        raise ValueError('transaction error')

    @staticmethod
    def get_length_for_tx(ins):
        assert len(ins) < 65536, 'Too much items'
        aoLenHex = hex(len(ins))[2:]
        aoLenHex = '0' + aoLenHex if len(aoLenHex) % 2 else aoLenHex
        return big_or_little(aoLenHex)
    # 小蚁币相关

    @staticmethod
    def get_claims(address, detail=False):
        result = Browser().claim(address, detail)
        if ANCClaim.check_unconfirm(address):
            result['enable'] = '0'
        return result

    @staticmethod
    def get_unconfirm_ancclaims():
        return ANCClaim.get_unconfirm()

    @staticmethod
    def get_ancclaim(acid):
        return ANCClaim.get_by_id(acid)

    @staticmethod
    def create_ancclaim(datas):
        '''创建ANCClaim'''
        return ANCClaim.create(datas)

    @classmethod
    def get_claim_transaction(cls, address):
        details = cls.get_claims(address, True)
        tx = '0200' + cls.get_length_for_tx(details['claims'])
        for c in details['claims']:
            tx += big_or_little(c[0])
            prevIndex = cls.get_length_for_tx(int(c[1]) * [0])
            if len(prevIndex) < 4:
                prevIndex += '00'
            tx += prevIndex
        tx += '000001e72d286979ee6cb1b7e65dfddfb2e384100b8d148e7758de42e4168b71792c60'
        tx += Fixed8(details['enable']).getData()
        tx += cls.address_to_scripthash(address)
        return tx, cls.compute_txid(tx)

    @staticmethod
    def update_ancclaim_txid(ac, txid):
        '''更形ANCClaim的txid'''
        ANCClaim.update_txid(ac, txid)

    @staticmethod
    def ancclaim_exist(acid):
        return ANCClaim.exist(acid)

    @staticmethod
    def ancclaim_accept_signature(acid):
        return ANCClaim.accept_signature(acid)

    @classmethod
    def send_claim_transaction(cls, ac, tran):
        '''发送交易'''
        regtx = tran + '014140' + ac.signature + '2321' + \
            cls.pubkey_to_compress(ac.hexPubkey) + 'ac'
        return cls.send_transaction_to_node(regtx, tran)

    # 资产相关
    @staticmethod
    def get_asset_balance(address, assetId):
        aa = AntAddress(address)
        return aa.get_asset_balance(assetId)

    @staticmethod
    def get_asset_name(assetId):
        '''获取指定资产的资产名'''
        return Asset.get_name(assetId)

    @staticmethod
    def asset_exist(assetId):
        '''资产是否存在'''
        return Asset.exist(assetId)

    @staticmethod
    def is_share_asset(assetId):
        '''是否为股权类资产'''
        return Asset.is_share(assetId)

    @staticmethod
    def get_valid_assets():
        '''获取平台支持的交易品种'''
        mids = Market.get_all_marketid()
        validAssetSign = [i[0:3] for i in mids]
        validAssetSign.extend([i[3:] for i in mids])
        validAssetSign = list(set(validAssetSign))
        return map(Asset.get_asset_by_market_sign, validAssetSign)

    @staticmethod
    def get_asset_type(assetId):
        '''获得资产的类型'''
        return Asset.get_asset_type(assetId)

    @staticmethod
    def get_asset(assetId):
        return Asset.get_asset(assetId)

    @staticmethod
    def get_asset_divisible(assetId):
        '''获取资产是否可分割'''
        return Asset.get_divisible(assetId)
    # AgencyOrder相关

    @staticmethod
    def update_agency_order_prevhash(ao, txid):
        '''更形agencyOrder的prevHash'''
        AgencyOrder.update_prevhash(ao, txid)

    @staticmethod
    def create_agency_order(datas):
        '''创建AgencyOrder'''
        return AgencyOrder.create(datas)

    @staticmethod
    def new_agency_order(datas):
        '''创建新的AgencyOrder对象，不存数据库'''
        return AgencyOrder.new(datas)

    @staticmethod
    def create_zero_id_agency_order(client, agent, assetId, valueId, way, price):
        '''创建一个id=0的AgencyOrder'''
        return AgencyOrder(client=client, agent=agent, assetId=assetId, valueId=valueId, way=way, price=price)

    @staticmethod
    def ask_agency_order_can_cancel(oid):
        '''是否可以取消:1.way=True;2.status=WaitingForMatch'''
        return AgencyOrder.can_cancel(oid, way=True)

    @staticmethod
    def bid_agency_order_can_cancel(oid):
        '''是否可以取消:1.way=True;2.status=WaitingForMatch'''
        return AgencyOrder.can_cancel(oid, way=False)

    @staticmethod
    def agency_order_for_ico(oid):
        '''为ICO单'''
        return AgencyOrder.is_for_ico(oid)

    @staticmethod
    def agency_order_exist(oid):
        '''指定id的订单是否存在'''
        return AgencyOrder.exist(oid)

    @staticmethod
    def get_unconfirm_agency_order():
        '''获取所有未确认的成交记录'''
        return AgencyOrder.get_unconfirm()

    @staticmethod
    def get_unconfirm_agency_order_of_address(address, assetId):
        '''获取所有未确认的成交记录'''
        return AgencyOrder.get_unconfirm_of_address(address, assetId)

    @staticmethod
    def get_agency_order(oid):
        '''获取指定id的AgencyOrder'''
        return AgencyOrder.get_order_by_id(oid)

    @staticmethod
    def get_agency_order_prevhash(oid):
        '''获取指定id的AgencyOrder的prevHash'''
        return AgencyOrder.get_prevhash(oid)

    @staticmethod
    def get_frozen_ask_agency_order(address, assetId, status):
        return AgencyOrder.get_frozen_ask_order(address, assetId, status)

    @staticmethod
    def get_frozen_bid_agency_order(address, assetId, status):
        return AgencyOrder.get_frozen_bid_order(address, assetId, status)

    @staticmethod
    def update_agency_order_status(oid, status):
        AgencyOrder.update_status(oid, status)
    # 市场相关

    @staticmethod
    def get_market(marketId):
        return Market.get_market(marketId)

    @staticmethod
    def get_market_last_24_volumn(marketId):
        return History.get_volumn(marketId)

    @staticmethod
    def update_market_price(marketId, price):
        '''更新市场价格'''
        Market.update_price(marketId, price)

    @staticmethod
    def market_exist(marketId):
        '''市场是否有效'''
        return Market.exist(marketId)

    @staticmethod
    def get_market_id(assetId, valueId):
        '''获取market_id,形如anscny'''
        return Market.get_market_id(assetId, valueId)

    @staticmethod
    def support_market(marketId):
        '''是否支持此市场'''
        return Market.support(marketId)

    @staticmethod
    def get_current_price(assetid, valueId):
        '''获得当前市场价'''
        return str(Market.get_price_by_asset(assetid, valueId))

    @staticmethod
    def get_market_price(marketId):
        '''获取市场价格'''
        return Market.get_price(marketId)
    # 转账相关

    @staticmethod
    def transfer_exist(tid):
        return Transfer.exist(tid)

    @staticmethod
    def create_transfer(datas):
        return Transfer.create(datas)

    @staticmethod
    def get_broadcast_uncomfirm_transfer(source, assetId):
        '''获得已广播但尚未确认的转账'''
        return Transfer.get_broadcast_uncomfirm_transfer(source, assetId)

    @staticmethod
    def get_unconfirm_transfer():
        '''获取所有未确认的转账'''
        return Transfer.get_unconfirm()
    # UID相关

    @staticmethod
    def create_uid(address):
        return UID.create(address)

    @staticmethod
    def uid_exist(address):
        return UID.exist(address)

    @staticmethod
    def get_uid(address):
        return UID.get_uid(address)
    # 交易历史相关

    @staticmethod
    def get_history(hid):
        '''获取指定id的历史记录'''
        return History.get_history_by_id(hid)

    @staticmethod
    def history_exist(hid):
        '''历史交易记录是否存在'''
        return History.exist(hid)

    @staticmethod
    def history_is_redeem(hid):
        '''是否已经取回'''
        return History.is_redeem(hid)

    @staticmethod
    def get_redeem_txid(hid):
        '''获取取回交易的txid'''
        return History.get_redeem_txid_by_id(hid)

    @staticmethod
    def get_unredeem_unconfirm_history():
        '''获取所有未取回未确认的成交记录'''
        return History.get_unredeem_unconfirm()

    @staticmethod
    def get_redeem_unconfirm_history():
        '''获取所有已取回未确认的成交记录'''
        return History.get_redeem_unconfirm()

    @staticmethod
    def get_unredeem_history_of_address_and_asset(address, assetId):
        '''获取未取回的历史记录'''
        return History.get_unredeem_of_address_and_asset(address, assetId)
        ret
    # 合约相关

    @staticmethod
    def get_contract_address(client, agent, assetId, valueId, way, price, apphash='ce3a97d7cfaa770a5e51c5b12cd1d015fbb5f87d'):
        '''生成合约地址'''
        return AgencyContract.get_address(client, agent, assetId, valueId, way, price, apphash)

    @staticmethod
    def compute_txid(trans):
        '''计算txid'''
        return big_or_little(binascii.hexlify(bin_dbl_sha256(binascii.unhexlify(trans))))

    @staticmethod
    def get_input_hex_num(ins, redeem=False):
        '''获取输入个数的16进制表示,此处需用小端'''
        if False not in map(lambda i: Option.BuyerICO.value == i.option, ins):
            iFalse = [i for i in ins if False == i.way]
            if iFalse:
                ins = iFalse + \
                    list(set([j.contractAddress for j in ins if True == j.way]))
        if len(ins) >= 65536:
            return False
        aoLenHex = hex(len(ins))[2:]
        aoLenHex = '0' + aoLenHex if len(aoLenHex) % 2 else aoLenHex
        return big_or_little(aoLenHex)

    @staticmethod
    def pubkey_to_compress(pubkey):
        '''生成压缩版公钥'''
        assert 130 == len(pubkey), 'Wrong pubkey length'
        x, y = pubkey[2:66], pubkey[66:]
        prefix = '03' if int('0x' + y[-1], 16) % 2 else '02'
        return prefix + x

    @staticmethod
    def private_to_hex_publickey(prik):
        '''私钥转换成公钥(完整版)'''
        f = get_privkey_format(prik)
        privkey = decode_privkey(prik, f)
        pubk = fast_multiply(G, privkey)
        pubk = encode_pubkey(pubk, 'hex')
        return pubk

    @staticmethod
    def sign(privkey, message):
        '''用私钥生成对message的签名'''
        sk = ecdsa.SigningKey.from_string(binascii.unhexlify(
            privkey), curve=ecdsa.SECP256k1, hashfunc=hashlib.sha256)
        signature = binascii.hexlify(
            sk.sign(binascii.unhexlify(message), hashfunc=hashlib.sha256))
        return signature

    @staticmethod
    def verify(pubkey, message, signature):
        '''验证签名 pubkey:hex pubkey, not hex_compressed'''
        vk = ecdsa.VerifyingKey.from_string(binascii.unhexlify(
            pubkey[2:]), curve=ecdsa.SECP256k1, hashfunc=hashlib.sha256)
        try:
            return vk.verify(binascii.unhexlify(signature), binascii.unhexlify(message))
        except ecdsa.BadSignatureError:
            return False

    @classmethod
    def generate_reg_tx(cls, inputs, outputs, extra=None):
        '''获取未签名的交易和txid'''
        tx = Transaction(inputs, outputs, [])
        stream = MemoryStream()
        writer = BinaryWriter(stream)
        tx.serializeUnsigned(writer)
        reg_tx = stream.toArray()
        #txid = tx.ensureHash()
        if extra:
            reg_tx = reg_tx[:4] + extra + reg_tx[6:]
        txid = cls.compute_txid(reg_tx)
        return reg_tx, txid

    @staticmethod
    def get_match_order_in_status(status):
        '''获取指定状态的MatchOrder'''
        return MatchOrder.get_order_in_status(status)

    @staticmethod
    def get_lock_agency_order(oid):
        return AgencyOrder.lock_to_update(oid)

    @staticmethod
    def get_agency_order_seller(option, assetId, valueId, status):
        return AgencyOrder.get_seller(option, assetId, valueId, status)

    @staticmethod
    def get_agency_order_buyer(option, assetId, valueId, status):
        return AgencyOrder.get_buyer(option, assetId, valueId, status)

    @staticmethod
    def get_ico_buyers(icoId):
        return AgencyOrder.get_ico_buyers(icoId)

    @staticmethod
    def get_asset_by_market_sign(marketSign):
        return Asset.get_asset_by_market_sign(marketSign)

    @staticmethod
    def get_agency_order_of_address_in_status(address, status):
        return AgencyOrder.get_order_of_address_in_status(address, status)

    @staticmethod
    def get_waiting_for_match_agency_order_of_otc(address, marketId='ALL'):
        return AgencyOrder.get_waiting_for_match_of_otc(address, marketId)

    @staticmethod
    def get_waiting_for_match_agency_order_of_ico(address):
        return AgencyOrder.get_waiting_for_match_of_ico(address)

    @staticmethod
    def get_transfer_by_id(tid):
        return Transfer.get_transfer_by_id(tid)

    @staticmethod
    def get_transfer(address):
        return Transfer.get_transfer(address)

    @staticmethod
    def address_to_scripthash(address):
        return AntAddress.address_to_scriptHash(address)

    @staticmethod
    def get_address_history(address, marketId=None, option='otc'):
        return History.get_address_history(address, marketId, option)

    @staticmethod
    def get_market_history(marketId):
        return History.get_market_history(marketId)

    @classmethod
    def get_transaction_for_otc(cls, ao):
        '''生成未签名的交易部分，otc专用 双方互转'''
        inputs = []
        outputs = []
        if ao.way:
            bid = cls.get_agency_order(ao.otcId)
            # seller
            ab = AntAddress(ao.address)
            ab_inputs, ab_outputs = ab.get_transactions(
                ao.amount, ao.assetId, bid.contractAddress)
            inputs.extend(ab_inputs)
            outputs.extend(ab_outputs)
            # buyer
            #inputs.append(TransactionInput(prevHash=bid.prevHash, prevIndex=bid.prevIndex))
            inputs.insert(0, TransactionInput(
                prevHash=bid.prevHash, prevIndex=bid.prevIndex))
            outputs.insert(-1, TransactionOutput(AssetId=bid.valueId, Value=bid.amount,
                                                 ScriptHash=AntAddress.address_to_scriptHash(ao.address)))
        else:
            ask = cls.get_agency_order(ao.otcId)
            # seller
            inputs.append(TransactionInput(
                prevHash=ask.prevHash, prevIndex=ask.prevIndex))
            outputs.append(TransactionOutput(AssetId=ask.assetId, Value=ask.amount,
                                             ScriptHash=AntAddress.address_to_scriptHash(ao.address)))
            # buyer
            ab = AntAddress(ao.address)
            ab_inputs, ab_outputs = ab.get_transactions(
                ao.amount, ao.valueId, ask.contractAddress)
            inputs.extend(ab_inputs)
            outputs.extend(ab_outputs)
        tran, txid = cls.generate_reg_tx(inputs, outputs)
        return tran, txid

    @classmethod
    def generate_unsignature_transaction_when_know_prevhash(cls, oid):
        '''为知道prevhash的订单生成未签名交易'''
        inputs = []
        outputs = []
        ao = cls.get_agency_order(oid)
        inputs.append(TransactionInput(
            prevHash=ao.prevHash, prevIndex=ao.prevIndex))
        assetId = ao.assetId if ao.way else ao.valueId
        outputs.append(TransactionOutput(AssetId=assetId, Value=float(
            str(ao.amount)), ScriptHash=AntAddress.address_to_scriptHash(ao.address)))
        return cls.generate_reg_tx(inputs, outputs)

    @classmethod
    def generate_unsignature_transaction(cls, oid, redeem=False):
        '''
        生成合约的前半部分，待签名
        redeem=False,转移至代理合约; redeem=True,从代理合约赎回至自己帐号
        '''
        ao = cls.get_agency_order(oid)
        if redeem:  # 从合约地址赎回
            aa = AntAddress(ao.contractAddress)
            toAddress = ao.address
        else:  # 发送至合约地址
            aa = AntAddress(ao.address)
            toAddress = ao.contractAddress
        asset = ao.assetId if ao.way else ao.valueId
        inputs, outputs = aa.get_transactions(ao.amount, asset, toAddress)
        return cls.generate_reg_tx(inputs, outputs)

    @classmethod
    def generate_unsignature_transaction_for_ico(cls, ao, baos):
        '''为ICO生成未签名交易 '''
        aa = AntAddress(ao.address)
        inputs = []
        outputs = []
        item_dict = {}
        items2 = []
        for b in baos:
            items2.append([b.contractAddress, b.icoAmount])
            if item_dict.has_key(b.contractAddress):
                item_dict[b.contractAddress] += b.icoAmount
            else:
                item_dict[b.contractAddress] = b.icoAmount
            inputs.append(TransactionInput(
                prevHash=b.prevHash, prevIndex=0))  # Hard code
        outputs.append(TransactionOutput(AssetId=ao.assetId,
                                         Value=ao.icoAmount, ScriptHash=aa.scripthash))
        items = item_dict.items()
        a_inputs, a_outputs = aa.get_multi_transactions(items, ao.valueId)
        #a_inputs,a_outputs = aa.get_multi_transactions(items2,ao.assetId)
        inputs.extend(a_inputs)
        outputs.extend(a_outputs)
        return cls.generate_reg_tx(inputs, outputs, extra='0190094f5443474f2d49434f')

    @classmethod
    def sort_transaction_script(cls, aos, redeem=False):
        '''排列脚本部分'''
        trScript = ''
        trScriptDict = {}
        trScriptList = []
        for ao in aos:
            if ao.id:
                if redeem:
                    redeemHex = AgencyContract.get_redeem_hex(
                        ao.client, ao.agent, ao.assetId, ao.valueId, ao.way, ao.price, ao.apphash)
                else:
                    redeemHex = '21' + ao.client + 'ac'
            else:
                if redeem:
                    redeemHex = '21' + ao.client + 'ac'
                else:
                    redeemHex = AgencyContract.get_redeem_hex(
                        ao.client, ao.agent, ao.assetId, ao.valueId, ao.way, ao.price, ao.apphash)
            trScriptDict[redeemHex] = ao.signature
        trScriptList = [rhx for rhx in trScriptDict]
        print '-' * 10, trScriptList
        trScriptList = sorted(trScriptList, key=cls.redeemhex_to_scripthash)
        print '-' * 10, trScriptList
        for rhx in trScriptList:
            trScript += '4140' + \
                trScriptDict[rhx] + hex(len(rhx) / 2)[2:] + rhx
        return trScript

    @classmethod
    def send_transaction_to_node(cls, regtx, tran, node=RPC_NODE):
        try:
            RN = RemoteNode(node)
            r = RN.sendRawTransaction(regtx)
            if r.has_key('error') and r['error']:
                print '-' * 5, 'raw:', regtx
                '''
                if RPC_NODE == node:
                    return cls.send_transaction_to_node(regtx,tran,RPC_NODE2)
                '''
                return False, r['error']['message'] + 'regtx:%s' % regtx
            if r['result']:
                print '-' * 5, 'txid:', cls.compute_txid(tran)
                return True, 'Success'
            else:
                print '-' * 5, 'raw:', regtx
                '''
                if RPC_NODE == node:
                    return cls.send_transaction_to_node(regtx,tran,RPC_NODE2)
                '''
                return False, u'广播失败，请于下一高度再尝试'
        except Exception as e:
            print '*' * 5, 'Exception', '*' * 5, e
            return False, 'Send to Node Exception'

    @classmethod
    def sendrawtransaction(cls, aos, tran, redeem=False):
        '''发送交易'''
        input_len_hex = cls.get_input_hex_num(aos)
        if not input_len_hex:
            return False, 'Too much inputs'
        regtx = tran + input_len_hex
        regtx += cls.sort_transaction_script(aos, redeem)
        return cls.send_transaction_to_node(regtx, tran)

    @classmethod
    def send_match_transaction(cls, ins, ous):
        '''
        发送撮合交易
        asks结构:[{'prevHash':__,'prevIndex':__},..]
        bids结构:[{'assetid':__,'value':__,'scripthash':__},..]
        '''
        input_len_hex = cls.get_input_hex_num(aos)
        if not input_len_hex:
            return False, 'Too much inputs'
        inputs = (TransactionInput(
            prevHash=a['prevHash'], prevIndex=a['prevIndex']) for a in ins)
        outputs = (TransactionOutput(
            AssetId=b['assetid'], Value=b['value'], ScriptHash=b['scripthash']) for b in ous)
        tx = Transaction(inputs, outputs, [])
        stream = MemoryStream()
        writer = BinaryWriter(stream)
        tx.serializeUnsigned(writer)
        tran = stream.toArray()
        txid = tx.ensureHash()
        sig = sign(AGENT_PRIKEY, binascii.unhexlify(tran))
        regtx = tran + input_len_hex
        for i in inputs:
            regtx += '4140' + sig + '2321' + AGENT_PUBKEY + 'ac'
        return cls.send_transaction_to_node(regtx, tran)

    @classmethod
    def send_transaction_for_otc_free_bid(cls, aos, tran):
        input_len_hex = cls.get_input_hex_num(aos)
        if not input_len_hex:
            return False, 'Too much inputs'
        regtx = tran + input_len_hex
        redeemHexDict = {}
        for ao in aos:
            if ao.way:
                redeemHex = AgencyContract.get_redeem_hex(
                    ao.client, ao.agent, ao.assetId, ao.valueId, ao.way, ao.price, ao.apphash)
            else:
                redeemHex = '21' + ao.client + 'ac'
            redeemHexDict[redeemHex] = ao.signature
        redeemHexList = [rhx for rhx in redeemHexDict]
        redeemHexList = sorted(redeemHexList, key=cls.redeemhex_to_scripthash)
        for rhx in redeemHexList:
            regtx += '4140' + redeemHexDict[rhx] + hex(len(rhx) / 2)[2:] + rhx
        return cls.send_transaction_to_node(regtx, tran)

    @classmethod
    def send_transaction_for_otc_free_ask(cls, aos, tran):
        input_len_hex = cls.get_input_hex_num(aos)
        if not input_len_hex:
            return False, 'Too much inputs'
        regtx = tran + input_len_hex
        redeemHexDict = {}
        for ao in aos:
            if ao.way:
                redeemHex = '21' + ao.client + 'ac'
            else:
                redeemHex = AgencyContract.get_redeem_hex(
                    ao.client, ao.agent, ao.assetId, ao.valueId, ao.way, ao.price, ao.apphash)
            redeemHexDict[redeemHex] = ao.signature
        redeemHexList = [rhx for rhx in redeemHexDict]
        redeemHexList = sorted(redeemHexList, key=cls.redeemhex_to_scripthash)
        for rhx in redeemHexList:
            regtx += '4140' + redeemHexDict[rhx] + hex(len(rhx) / 2)[2:] + rhx
        return cls.send_transaction_to_node(regtx, tran)

    @staticmethod
    def redeemhex_to_scripthash(redeemHex):
        scriptHash = big_or_little(
            redeem_to_scripthash(binascii.unhexlify(redeemHex)))
        print scriptHash
        return scriptHash

    @staticmethod
    def market_to_user(marketId):
        mu = marketId.upper()
        mu = mu[:3] + '\\' + mu[3:]
        return mu

    @staticmethod
    def create_bank(datas):
        '''create bank'''
        return Bank.create(datas)

    @staticmethod
    def encode(key, content):
        enc = []
        for i in range(len(content)):
            key_c = key[i % len(key)]
            enc_c = chr((ord(content[i]) + ord(key_c)) % 256)
            enc.append(enc_c)
        return base64.urlsafe_b64encode("".join(enc))

    @staticmethod
    def decode(key, enc):
        dec = []
        enc = base64.urlsafe_b64decode(enc)
        for i in range(len(enc)):
            key_c = key[i % len(key)]
            dec_c = chr((256 + ord(enc[i]) - ord(key_c)) % 256)
            dec.append(dec_c)
        return "".join(dec)


if "__main__" == __name__:
    redeemHexA = '2102abab730e3b83ae352a1d5210d8c4dac9cf2cacc6baf479709d7b989c2151b867ac'
    redeemHexB = '0400e1f5055121039b2c6b8a8838595b8ebcc67bbc85cec78d805d56890e9a0d71bcae89664339d620cd5e195b9235a31b7423af5e6937a660f7e7e62524710110b847bab41721090c20e72d286979ee6cb1b7e65dfddfb2e384100b8d148e7758de42e4168b71792c602102956593708a81bc6b64e66b1ba10a24eace9273f7a2945c746e604da2969a9f9f67e33448f4120cd2fd3d2ed7ade6c81ed065284d8a'
    print sorted([redeemHexA, redeemHexB], key=redeemhex_to_scripthash)
    print sorted([redeemHexB, redeemHexA], key=redeemhex_to_scripthash)
