# coding:utf8
import os
from math import floor
from django.db import transaction
from django.core.cache import cache
from rest_framework import serializers
from decimal import Decimal as D, ROUND_DOWN, ROUND_HALF_DOWN
from AntShares.Core.TransactionInput import TransactionInput
from AntShares.Core.TransactionOutput import TransactionOutput
from AntShares.Cryptography.Helper import pubkey_to_address, compress_pubkey
from OTCGO.settings import AGENT_PUBKEY, AGENT_PRIKEY, RMB_ASSET, MAX_ICO_BUYER
from wallet.models import *
from wallet.WalletTool import WalletTool as WT
from wallet.ICOTool import ICOTool as IT
from wallet.tasks import confirm_transaction
from wallet.AntAddress import AntAddress
from OTCGO.Enums import MatchStatus, Option, ClaimStatus
import logging

logger = logging.getLogger('django')

HEX_RANGE = [ord(x) for x in '0123456789abcdef']
ASCII_NORMAL_RANGE = [ord(x) for x in '0123456789abcdefghijklmnopqrstuvwxyz']


def hex_verify(c):
    try:
        return ord(c.lower()) in HEX_RANGE
    except:
        return False


def ascii_normal_verify(c):
    try:
        return ord(c.lower()) in ASCII_NORMAL_RANGE
    except:
        return False


def validate_length(s, num):
    if len(s) != num:
        return False
    else:
        return True


def validate_hex(s):
    if False in map(hex_verify, s):
        return False
    else:
        return True


def validate_ascii_normal(s):
    if False in map(ascii_normal_verify, s):
        return False
    else:
        return True


def validate_hex_field(s, num, name):
    if not validate_length(s, num):
        raise serializers.ValidationError(
            "%s's length must be %s" % (name, num))
    if not validate_hex(s):
        raise serializers.ValidationError("invalid characters in %s" % name)
    return True


def validate_ascii_field(s, num, name):
    if 34 == num and 'A' != s[0]:
        raise serializers.ValidationError(
            "This field(%s:%s) is not an AntShares Address" % (s, name))
    if not validate_length(s, num):
        raise serializers.ValidationError(
            "%s's length must be %s" % (name, num))
    if not validate_ascii_normal(s):
        raise serializers.ValidationError("invalid characters in %s" % name)
    return True


def validate_asset(assetId, name, num=64, shareCanTransfer=False):
    if validate_hex_field(assetId, num, name):
        if not WT.asset_exist(assetId):
            raise serializers.ValidationError(u"%s资产不存在" % assetId)
        else:
            # hard code
            if not shareCanTransfer and WT.is_share_asset(assetId):
                raise serializers.ValidationError(u'Share类资产暂不支持转账')
            return True


def validate_float(s, name, num=21, length=4):
    try:
        fs = float(s)
    except:
        raise serializers.ValidationError('%s is not a valid float' % s)
    if fs <= 0:
        raise serializers.ValidationError(
            '%s should > 0,but is %s' % (name, s))
    ss = str(fs)
    if len(ss) > num:
        raise serializers.ValidationError('%s is too large' % ss)
    if '.' in ss:
        dicimal_part = ss.split('.')[1]
        if len(dicimal_part) > length:
            raise serializers.ValidationError(
                "%s's decimal part is too long, the limit is 4" % ss)
    return D(ss)


class OrderBookSerializer(serializers.Serializer):
    class Meta:
        model = MatchOrder


class MarketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Market
        fields = ('marketId', 'name')


class OrderCancelSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=True)
    nonce = serializers.CharField(required=True, max_length=8)
    signature = serializers.CharField(required=True, max_length=128)

    class Meta:
        model = AgencyOrder

    def validate_id(self, value):
        oid = value
        if oid <= 0:
            raise serializers.ValidationError('id:%s invalid' % oid)
        if not WT.agency_order_exist(oid):
            raise serializers.ValidationError('id:%s invalid' % oid)
        return value

    def validate_nonce(self, value):
        if validate_hex_field(value, 8, 'nonce'):
            return value

    def validate_signature(self, value):
        if validate_hex_field(value, 128, 'signature'):
            return value

    def validate(self, data):
        '''
        1.是否可以取消
        2.验证签名
        '''
        oid = data['id']
        nonce = data['nonce']
        signature = data['signature']
        if not WT.agency_order_exist(oid):
            raise serializers.ValidationError(u'id:%s 订单不存在' % oid)
        ao = WT.get_agency_order(oid)
        if Option.BuyerICO.value == ao.option:
            if not IT.can_cancel(ao):
                raise serializers.ValidationError(u'众筹进行中，不可撤销')
        if MatchStatus.WaitingForMatch.value != ao.status:
            raise serializers.ValidationError(u'此订单无法取消')
        if not WT.verify(ao.hexPubkey, nonce, signature):
            raise serializers.ValidationError(u'无效签名')
        return data

class SignSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=True)
    nonce = serializers.CharField(required=True, max_length=8)
    signature = serializers.CharField(required=True, max_length=128)
    class Meta:
        model = AgencyOrder
    def validate_id(self, value):
        oid = value
        if 0 == oid:
            raise serializers.ValidationError('id:%s invalid' % oid)
        if oid > 0:
            if not WT.agency_order_exist(oid):
                raise serializers.ValidationError('id:%s invalid' % oid)
            return value
        if oid < 0:
            if not WT.transfer_exist((-1)*oid):
                raise serializers.ValidationError('id:%s invalid' % oid)
            return value
    def validate_nonce(self, value):
        if validate_hex_field(value,8,'nonce'):
            return value
    def validate_signature(self, value):
        if validate_hex_field(value,128,'signature'):
            return value
    @transaction.atomic
    def validate(self, data):
        '''
        1.可签名状态,[等待签名，等待匹配]
        2.签名有效
        3.发送交易
        '''
        order_id = data['id']
        nonce = data['nonce']
        signature = data['signature'] 
        # step 1
        if 0 > order_id: #转账
            try:
                oid = (-1)*order_id
                tr = WT.get_transfer_by_id(oid)
                txid = tr.txid
                tran = cache.get(str(oid)+'_transfer')
                if not tran:
                    raise serializers.ValidationError(u'操作超时，请稍候再试！')
                hexPubkey = tr.hexPubkey
                compressedPubkey = WT.pubkey_to_compress(hexPubkey)
            except Exception as e:
                raise serializers.ValidationError('error while getting transfer order:%s' % (oid))
            if not WT.verify(hexPubkey,tran,signature):
                raise serializers.ValidationError('signature invalid for transfer')
            ao = WT.new_agency_order({'id':-1,'signature':signature,'client':compressedPubkey})
            send, msg = WT.sendrawtransaction([ao], tran)
            if not send:
                raise serializers.ValidationError(msg)
            else:
                tr.broadcast = True
                tr.save()
            data['txid'] = txid
            return data
        if not WT.agency_order_exist(order_id):
            raise serializers.ValidationError('order not exist %s' % order_id)
        ao = WT.get_lock_agency_order(order_id)
        if MatchStatus.WaitingForMatch.value != ao.status:
            raise serializers.ValidationError('do not need signature')
        # 撤销
        marketId = WT.get_market_id(ao.assetId,ao.valueId)
        ao.signature = signature
        assetId = ao.assetId if ao.way else ao.valueId
        tran = cache.get(str(order_id)+'_cancel')
        if not tran:
            raise serializers.ValidationError('No transaction to redeem id %s' % ao.id)
        if not WT.verify(ao.hexPubkey,tran,signature):
            raise serializers.ValidationError('signature invalid')
        aos = [ao]
        if (ao.way and 'Share' == WT.get_asset_type(ao.assetId)) or (False==ao.way and 'Share'==WT.get_asset_type(ao.valueId)):
            sao = WT.create_zero_id_agency_order(ao.client,ao.agent,ao.assetId,ao.valueId,ao.way,ao.price)
            sao.signature = signature
            aos.append(sao)
        print '-'*5,'cancel: amount:%s  price:%s' % (ao.amount, ao.price)
        send, msg = WT.sendrawtransaction(aos, tran, True)
        if not send:
            raise serializers.ValidationError(msg)
        ao.status = MatchStatus.Cancelled.value
        ao.redeemTxid = WT.compute_txid(tran)
        ao.order = WT.get_match_order_in_status(ao.status)
        ao.save()
        return data

# OTC部分的签名
class OTCSignSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=True)
    signature = serializers.CharField(required=True, max_length=128)
    class Meta:
        model = AgencyOrder
    def validate_id(self, value):
        oid = value
        if oid > 0 and WT.agency_order_exist(oid):
            return value
        raise serializers.ValidationError('id:%s invalid' % oid)
    def validate_signature(self, value):
        if validate_hex_field(value,128,'signature'):
            return value
    @transaction.atomic
    def validate(self, data):
        '''
        1.可签名状态,[等待签名，等待匹配]
        2.签名有效
        3.发送交易
        '''
        order_id = data['id']
        signature = data['signature'] 
        # step 1
        if not WT.agency_order_exist(order_id):
            raise serializers.ValidationError(u'订单不存在 %s' % order_id)
        ao = WT.get_lock_agency_order(order_id)
        if MatchStatus.WaitingForSignature.value != ao.status:
            raise serializers.ValidationError(u'不可签名')
        marketId = WT.get_market_id(ao.assetId,ao.valueId)
        ao.signature = signature
        assetId = ao.assetId if ao.way else ao.valueId
        if not ao.prevHash:
            raise serializers.ValidationError('no prevHash')
        tran = cache.get(ao.prevHash)
        if not tran:
            raise serializers.ValidationError(u'操作超时')
        if not WT.verify(ao.hexPubkey,tran,signature):
            raise serializers.ValidationError(u'无效签名')
        if ao.otcId:#OTC直接吃单
            if ao.way:#直接吃超导买单
                bid = WT.get_agency_order(ao.otcId)
                aos = [bid]
                for a in aos:
                    sig = WT.sign(AGENT_PRIKEY, tran)
                    a.signature = sig
                aos.append(ao)
                print '<'*5,'free ask: amount:%s  price:%s' % (ao.amount, ao.price)
                send, msg = WT.send_transaction_for_otc_free_ask(aos, tran)
                if not send:
                    ao.delete()
                    raise serializers.ValidationError(msg)
                ao.status = MatchStatus.Unconfirmation.value
                ao.save()
                print 'eat agency order is: %d, status:%s' % (ao.id,ao.status)
                History(option=Option.SellerOTC.value,
                        marketId = marketId,
                        fromAddress=bid.contractAddress,
                        fromRealAddress = bid.address,
                        fromId = bid.id,
                        toAddress=ao.address,
                        toRealAddress = ao.address,
                        toId = ao.id,
                        way = True,
                        assetId = ao.valueId,
                        amount = bid.amount,
                        price = bid.price,
                        txid = ao.prevHash,
                        redeem=True,
                        redeemTxid=ao.prevHash).save()
                History(option=Option.SellerOTC.value,
                        marketId = marketId,
                        fromAddress=ao.address,
                        fromRealAddress = ao.address,
                        fromId = ao.id,
                        toAddress=bid.contractAddress,
                        toRealAddress = bid.address,
                        toId = bid.id,
                        way = False,
                        assetId = ao.assetId,
                        amount = ao.amount,
                        price = ao.price,
                        show = True,
                        txid = ao.prevHash).save()
                bid.status = MatchStatus.Finish.value
                moFinish = WT.get_match_order_in_status(bid.status)
                bid.order = moFinish
                bid.otcId = ao.id
                bid.save()
                ao.order = moFinish
                ao.save()
                WT.update_market_price(marketId, bid.price)
            else:#直接吃超导卖单
                ask = WT.get_agency_order(ao.otcId)
                aos = [ask]
                for a in aos:
                    sig = WT.sign(AGENT_PRIKEY, tran)
                    a.signature = sig
                aos.append(ao)
                print '<'*5,'bid: amount:%s  price:%s' % (ao.amount, ao.price)
                send, msg = WT.send_transaction_for_otc_free_bid(aos, tran)
                if not send:
                    ao.delete()
                    raise serializers.ValidationError(msg)
                ao.status = MatchStatus.Unconfirmation.value
                ao.save()
                print 'eat agency order is: %d, status:%s' % (ao.id,ao.status)
                History(option=Option.SellerOTC.value,
                        marketId = marketId,
                        fromAddress=ao.address,
                        fromRealAddress = ao.address,
                        fromId = ao.id,
                        toAddress=ask.contractAddress,
                        toRealAddress = ask.address,
                        toId = ask.id,
                        way = True,
                        assetId = ask.valueId,
                        amount = ao.amount,
                        price = ask.price,
                        show = True,
                        txid = ao.prevHash).save()
                History(option=Option.SellerOTC.value,
                        marketId = marketId,
                        fromAddress=ask.contractAddress,
                        fromRealAddress = ask.address,
                        fromId = ask.id,
                        toAddress=ao.address,
                        toRealAddress = ao.address,
                        toId = ao.id,
                        way = False,
                        assetId = ao.assetId,
                        amount = ask.amount,
                        price = ao.price,
                        txid = ao.prevHash,
                        redeem=True,
                        redeemTxid=ao.prevHash).save()
                ask.status = MatchStatus.Finish.value
                moFinish = WT.get_match_order_in_status(ask.status)
                ask.order = moFinish
                ask.otcId = ao.id
                ask.save()
                ao.order = moFinish
                ao.save()
                WT.update_market_price(marketId, ask.price)
        else:#OTC超导挂单
            aos = [ao]
            if 'Share' == WT.get_asset_type(assetId):
                sao = WT.create_zero_id_agency_order(ao.client,ao.agent,ao.assetId,ao.valueId,ao.way,ao.price)
                sao.signature = WT.sign(AGENT_PRIKEY, tran)
                aos.append(sao)
            if ao.way:
                print '>'*5,'OTC ask: amount:%s  price:%s' % (ao.amount, ao.price)
            else:
                print '>'*5,'OTC bid: amount:%s  price:%s' % (ao.amount, ao.price)
            send, msg = WT.sendrawtransaction(aos, tran)
            if not send:
                ao.delete()
                raise serializers.ValidationError(msg)
            ao.status = MatchStatus.Unconfirmation.value
            ao.save()
        return data

class TransferSerializer(serializers.Serializer):
    source = serializers.CharField(required=True,max_length=34)
    dest = serializers.CharField(required=True,max_length=34) 
    assetId = serializers.CharField(required=True,max_length=64)
    amount = serializers.CharField(required=True,max_length=21)
    hexPubkey = serializers.CharField(required=True, max_length=130)
    class Meta:
        model = Transfer
    def validate_source(self, value):
        if validate_ascii_field(value,34,'source'):
            return value
    def validate_dest(self, value):
        if validate_ascii_field(value,34,'dest'):
            return value
    def validate_assetId(self, value):
        if validate_asset(value, 'assetId'):
            return value
    def validate_amount(self, value):#return a decimal
        return validate_float(value, 'amount', 21, 8)
    def validate_hexPubkey(self, value):
        if validate_hex_field(value,130,'hexPubkey'):
            return value
        raise serializers.ValidationError(u'hexPubkey有误')
    def validate(self, data):
        '''
        1.确认资产足够
        2.确认资产可分割操作
        3.生成交易
        '''
        # step 1
        address = data['source']
        assetId = data['assetId']
        amount = data['amount'] #decimal
        aa = AntAddress(address)
        if aa.get_asset_balance(assetId) < amount:
            raise serializers.ValidationError("poor balances")
        # step 2
        divisible = WT.get_asset_divisible(assetId)
        if not divisible and amount > amount.quantize(D('1.'),rounding=ROUND_DOWN):
            raise serializers.ValidationError(u"此资产不可分割")
        # setp 3
        inputs,outputs = aa.get_transactions(amount, assetId, data['dest'])
        tran, txid = WT.generate_reg_tx(inputs,outputs)
        cache.set(txid+'_transfer', tran, timeout=60)
        data['txid'] = txid
        return data
    def create(self, validated_data):
        tr = WT.create_transfer(validated_data) 
        key = tr.txid + '_transfer'
        trans = cache.get(key)
        print 'transfer serializer:',trans
        cache.set(str(tr.id)+'_transfer',trans, timeout=60)
        return tr

class AgencyOrderSerializer(serializers.Serializer):
    client = serializers.CharField(required=True, max_length=66)
    hexPubkey = serializers.CharField(required=True, max_length=130)
    assetId = serializers.CharField(required=True, max_length=64)
    valueId = serializers.CharField(required=True, max_length=64)
    amount = serializers.CharField(required=True, max_length=32)
    price  = serializers.CharField(required=True, max_length=32)
    way    = serializers.BooleanField(required=True)
    class Meta:
        model = AgencyOrder
    def validate_client(self, value):
        if validate_hex_field(value,66,'client'):
            return value
    def validate_hexPubkey(self, value):
        if validate_hex_field(value,130,'hexPubkey'):
            return value
        raise serializers.ValidationError(u'hexPubkey有误')
    def validate_assetId(self, value):
        if validate_asset(value, 'assetId'):
            return value
    def validate_valueId(self, value):
        if validate_asset(value, 'valueId'):
            return value
    def validate_amount(self, value):
        return validate_float(value, 'amount')
    def validate_price(self, value):
        return validate_float(value, 'price')
    def validate(self, data):
        '''
        -1.agent == AGENT_PUBKEY
        0.确定assetId != valueId
        1.支持交易品种
        2.整数交易资产
        3.client 与 hexPubkey 匹配
        4.total 赋值 amount
        5.status 赋值 WaitingForSignature
        6.余额充足
        7.address
        8.同价单是否正常
        '''
        # step -1
        data['agent'] = AGENT_PUBKEY
        # step 0
        if data['assetId'] == data['valueId']:
            raise serializers.ValidationError(u"同种资产不可交易")
        # step 1
        marketId = WT.get_market_id(data['assetId'],data['valueId'])
        if not WT.support_market(marketId):
            raise serializers.ValidationError(u"尚不支持交易")
        # step 2
        if data['way']:
            divisible = WT.get_asset_divisible(data['assetId'])
        else:
            divisible = WT.get_asset_divisible(data['valueId'])
        if (not divisible) and float(data['amount']) != floor(float(data['amount'])):
                raise serializers.ValidationError(u"不可分隔资产必须为整数")
        # step 3
        if not data['hexPubkey'][2:].startswith(data['client'][2:]):
            raise serializers.ValidationError(u"client与hexPubkey不匹配")
        # step 4
        if data['way']:
            data['total'] = data['amount']
        else:
            data['amount'] = data['amount']*data['price']
            data['total'] = data['amount']
        # step 5
        # step 6
        address = pubkey_to_address(data['client'])
        aa = AntAddress(address)
        if data['way']:
            if WT.get_asset_balance(address,data['assetId'] < data['amount']):
                raise serializers.ValidationError(u"余额不足")
        else:
            if WT.get_asset_balance(address,data['valueId'] < data['amount']):
                raise serializers.ValidationError(u"余额不足")
        data['status'] = MatchStatus.WaitingForSignature.value
        data['order'] = WT.get_match_order_in_status(data['status'])
        # step 7
        data['address'] = address
        # step 8
        if data['way']:
            data['contractAddress'] = WT.get_contract_address(data['client'],data['agent'],data['assetId'],data['valueId'],data['way'],data['price'])
        return data
    def create(self, validated_data):
        return WT.create_agency_order(validated_data)

class UIDSerializer(serializers.Serializer):
    address = serializers.CharField(required=True, max_length=34)
    class Meta:
        model = UID
    def validate_address(self, value):
        if validate_ascii_field(value,34,'address'):
            return value
    def create(self, validated_data):
        address = validated_data['address']
        if not WT.uid_exist(address):
            return WT.create_uid(address)
        else:
            return WT.get_uid(address)

class RedeemCreateSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=True)
    nonce = serializers.CharField(required=True, max_length=8)
    address = serializers.CharField(required=True, max_length=34)
    signature = serializers.CharField(required=True, max_length=128)
    class Meta:
        model = History
    def validate_id(self, value):
        if not WT.history_exist(value):
            raise serializers.ValidationError(u'不存在')
        if WT.history_is_redeem(value):
            raise serializers.ValidationError(u'已取回')
        return value
    def validate_nonce(self, value):
        if validate_hex_field(value,8,'nonce'):
            return value
    def validate_address(self, value):
        if validate_ascii_field(value,34,'address'):
            return value
    def validate_signature(self, value):
        if validate_hex_field(value,128,'signature'):
            return value
    def validate(self, data):
        hid = data['id']
        nonce = data['nonce']
        address = data['address']
        signature = data['signature']
        his = WT.get_history(hid)
        ao =  WT.get_agency_order(his.toId)
        if ao.address != address:
            raise serializers.ValidationError(u'无权取回')
        hexPubkey = ao.hexPubkey
        if not WT.verify(hexPubkey,nonce,signature):
            raise serializers.ValidationError(u'无效签名')
        if ao.contractAddress != his.toAddress:
            raise serializers.ValidationError(u'不匹配')
        if Option.BuyerICO.value == ao.option:
            inputs,outputs = AntAddress(ao.contractAddress).get_transactions(his.amount,his.assetId,ao.address)
        else:
            # inputs = [TransactionInput(prevHash=his.txid, prevIndex=1 if ao.way else 0)]
            inputs = [TransactionInput(prevHash=his.txid, prevIndex=WT.get_prev_index(his.txid,his.toAddress,his.assetId))]
            outputs = [TransactionOutput(AssetId=his.assetId,Value=float(str(his.amount)),ScriptHash=WT.address_to_scripthash(address))]
        tran,txid = WT.generate_reg_tx(inputs, outputs)
        cache.set(str(hid)+'_redeem', tran, timeout=60)
        return data

class RedeemSignatureSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=True)
    signature = serializers.CharField(required=True, max_length=128)
    class Meta:
        model = AgencyOrder
    def validate_id(self, value):
        if not WT.history_exist(value):
            raise serializers.ValidationError(u'不存在')
        if WT.history_is_redeem(value):
            raise serializers.ValidationError(u'已取回')
        return value
    def validate_signature(self, value):
        if validate_hex_field(value,128,'signature'):
            return value
    @transaction.atomic
    def validate(self, data):
        hid = data['id']
        signature = data['signature']
        his = WT.get_history(hid)
        ao = WT.get_agency_order(his.toId)
        hexPubkey = ao.hexPubkey
        tran = cache.get(str(hid)+'_redeem')
        if not tran:
            raise serializers.ValidationError(u'操作超时')
        if not WT.verify(hexPubkey,tran,signature):
            raise serializers.ValidationError(u'无效签名')
        if ao.contractAddress != his.toAddress:
            raise serializers.ValidationError(u'不匹配')
        ao.signature = signature
        ao.id = 0
        aos = [ao]
        if (ao.way and 'Share'==WT.get_asset_type(ao.valueId)) or (False==ao.way and 'Share' == WT.get_asset_type(ao.assetId)):
            sao = WT.get_agency_order(his.toId)
            sao.signature = signature
            aos.append(sao)
        print '='*5,'redeem: amount:%s  price:%s' % (ao.amount, ao.price)
        send, msg = WT.sendrawtransaction(aos, tran)
        if not send:
            raise serializers.ValidationError(msg)
        his.redeem = True
        his.confirm = False
        his.redeemTxid = WT.compute_txid(tran)
        his.save()
        return data

class OTCAskOrderSerializer(serializers.Serializer):
    hexPubkey = serializers.CharField(required=True, max_length=130)
    assetId = serializers.CharField(required=True, max_length=64)
    valueId = serializers.CharField(required=True, max_length=64)
    amount = serializers.CharField(required=True, max_length=32)
    price  = serializers.CharField(required=True, max_length=32)
    class Meta:
        model = AgencyOrder
    def validate_hexPubkey(self, value):
        if validate_hex_field(value,130,'hexPubkey'):
            return value
        raise serializers.ValidationError(u'hexPubkey有误')
    def validate_assetId(self, value):
        if validate_asset(value, 'assetId', 64, True):
            return value
    def validate_valueId(self, value):
        if validate_asset(value, 'valueId', 64, True):
            return value
    def validate_amount(self, value):
        return validate_float(value, 'amount')
    def validate_price(self, value):
        return validate_float(value, 'price')
    def validate(self, data):
        '''
        1.初始值
        2.非同中资产交易
        3.交易所支持的 交易对
        4.判断可分割性
        5.余额是否充足
        6.生成合约地址
        '''
        # step 1
        data['way'] =       True
        data['agent'] =     AGENT_PUBKEY
        data['total'] =     data['amount']
        data['client'] =    WT.pubkey_to_compress(data['hexPubkey'])
        data['address'] =   pubkey_to_address(data['client'])
        data['status'] =    MatchStatus.WaitingForSignature.value
        data['order'] =     WT.get_match_order_in_status(data['status'])
        # step 2
        if data['assetId'] == data['valueId']:
            raise serializers.ValidationError(u"同种资产不可交易")
        # step 3
        marketId = WT.get_market_id(data['assetId'],data['valueId'])
        if not WT.support_market(marketId):
            raise serializers.ValidationError(u"尚不支持此交易对")
        # step 4
        assetDiv,valueDiv = map(WT.get_asset_divisible, [data['assetId'],data['valueId']])
        if (not assetDiv) and data['amount'] != data['amount'].quantize(D('1.'), rounding=ROUND_DOWN):
            raise serializers.ValidationError(u"卖出资产必须为整数")
        if assetDiv and data['amount'] != data['amount'].quantize(D('.00000001'), rounding=ROUND_DOWN):
            raise serializers.ValidationError(u"卖出资产小数位超过8位")
        if data['price'] != data['price'].quantize(D('.00000001'), rounding=ROUND_DOWN):
            raise serializers.ValidationError(u"价格小数位超过8位")
        valueAmount = data['amount']*data['price']
        if (not valueDiv) and valueAmount != valueAmount.quantize(D('1.'), rounding=ROUND_DOWN):
            raise serializers.ValidationError(u"买入资产必须为整数")
        if valueDiv and valueAmount != valueAmount.quantize(D('.00000001'), rounding=ROUND_DOWN):
            raise serializers.ValidationError(u"买入资产量超过8位小数")
        # step 5
        aa = AntAddress(data['address'])
        if aa.get_asset_balance(data['assetId']) < data['amount']:
            raise serializers.ValidationError(u"余额不足")
        # step 6
        data['contractAddress'] = WT.get_contract_address(data['client'],data['agent'],data['assetId'],data['valueId'],data['way'],data['price'])
        return data
    def create(self, validated_data):
        return WT.create_agency_order(validated_data)

class OTCBidOrderSerializer(serializers.Serializer):
    hexPubkey = serializers.CharField(required=True, max_length=130)
    assetId = serializers.CharField(required=True, max_length=64)
    valueId = serializers.CharField(required=True, max_length=64)
    amount = serializers.CharField(required=True, max_length=32)
    price  = serializers.CharField(required=True, max_length=32)
    class Meta:
        model = AgencyOrder
    def validate_hexPubkey(self, value):
        if validate_hex_field(value,130,'hexPubkey'):
            return value
        raise serializers.ValidationError(u'hexPubkey有误')
    def validate_assetId(self, value):
        if validate_asset(value, 'assetId', 64, True):
            return value
    def validate_valueId(self, value):
        if validate_asset(value, 'valueId', 64, True):
            return value
    def validate_amount(self, value):
        return validate_float(value, 'amount')
    def validate_price(self, value):
        return validate_float(value, 'price')
    def validate(self, data):
        '''
        1.初始值
        2.非同中资产交易
        3.交易所支持的 交易对
        4.判断可分割性
        5.余额是否充足
        6.生成合约地址
        '''
        # step 1
        data['way'] =       False
        data['agent'] =     AGENT_PUBKEY
        data['total'] =     data['amount']
        data['client'] =    WT.pubkey_to_compress(data['hexPubkey'])
        data['address'] =   pubkey_to_address(data['client'])
        data['status'] =    MatchStatus.WaitingForSignature.value
        data['order'] =     WT.get_match_order_in_status(data['status'])
        # step 2
        if data['assetId'] == data['valueId']:
            raise serializers.ValidationError(u"同种资产不可交易")
        # step 3
        marketId = WT.get_market_id(data['assetId'],data['valueId'])
        if not WT.support_market(marketId):
            raise serializers.ValidationError(u"尚不支持此交易对")
        # step 4
        assetDiv,valueDiv = map(WT.get_asset_divisible, [data['assetId'],data['valueId']])
        if (not assetDiv) and data['amount'] != data['amount'].quantize(D('1.'), rounding=ROUND_DOWN):
            raise serializers.ValidationError(u"卖出资产必须为整数")
        if assetDiv and data['amount'] != data['amount'].quantize(D('.00000001'), rounding=ROUND_DOWN):
            raise serializers.ValidationError(u"卖出资产小数位超过8位")
        if data['price'] != data['price'].quantize(D('.00000001'), rounding=ROUND_DOWN):
            raise serializers.ValidationError(u"价格小数位超过8位")
        valueAmount = data['amount']*data['price']
        if (not valueDiv) and valueAmount != valueAmount.quantize(D('1.'), rounding=ROUND_DOWN):
            raise serializers.ValidationError(u"买入资产必须为整数")
        if valueDiv and valueAmount != valueAmount.quantize(D('.00000001'), rounding=ROUND_DOWN):
            raise serializers.ValidationError(u"买入资产量超过8位小数")
        # step 5
        data['amount'] = valueAmount
        aa = AntAddress(data['address'])
        if aa.get_asset_balance(data['valueId']) < data['amount']:
            raise serializers.ValidationError(u"余额不足")
        # step 6
        data['contractAddress'] = WT.get_contract_address(data['client'],data['agent'],data['assetId'],data['valueId'],data['way'],data['price'])
        return data
    def create(self, validated_data):
        return WT.create_agency_order(validated_data)

# OTC直接吃买单
class FreeAskOrderSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=True)
    hexPubkey = serializers.CharField(required=True, max_length=130)
    class Meta:
        model = AgencyOrder
    def validate_id(self, value):
        oid = value
        if oid <= 0:
            raise serializers.ValidationError(u'id:%s值必须为整数' % oid)
        if not WT.agency_order_exist(oid):
            raise serializers.ValidationError(u'id:%s不存在' % oid)
        if not WT.bid_agency_order_can_cancel(oid):
            raise serializers.ValidationError(u'id:%s状态有误' % oid)
        return value
    def validate_hexPubkey(self, value):
        if validate_hex_field(value,130,'hexPubkey'):
            return value
        raise serializers.ValidationError(u'hexPubkey有误')
    def validate(self, data):
        '''
        1.初始值
        2.余额充足
        '''
        data['way'] = True
        data['agent'] = AGENT_PUBKEY
        otcId = data['id']
        del data['id']
        sao = WT.get_agency_order(otcId)
        data['otcId'] = otcId
        client = WT.pubkey_to_compress(data['hexPubkey'])
        amount = sao.amount/sao.price
        address = pubkey_to_address(client)
        data['client'] = client
        data['price'] = sao.price
        data['amount'] = amount
        data['address'] = address
        data['assetId'] = sao.assetId
        data['valueId'] = sao.valueId
        if WT.get_asset_balance(address,data['assetId']) < amount:
            raise serializers.ValidationError(u"余额不足")
        data['status'] = MatchStatus.WaitingForSignature.value
        data['order'] = WT.get_match_order_in_status(data['status'])
        return data
    def create(self, validated_data):
        return WT.create_agency_order(validated_data)

# OTC直接吃卖单
class FreeBidOrderSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=True)
    hexPubkey = serializers.CharField(required=True, max_length=130)
    class Meta:
        model = AgencyOrder
    def validate_id(self, value):
        oid = value
        if oid <= 0:
            raise serializers.ValidationError(u'id:%s值必须为整数' % oid)
        if not WT.agency_order_exist(oid):
            raise serializers.ValidationError(u'id:%s不存在' % oid)
        if not WT.ask_agency_order_can_cancel(oid):
            raise serializers.ValidationError(u'id:%s状态有误' % oid)
        return value
    def validate_hexPubkey(self, value):
        if validate_hex_field(value,130,'hexPubkey'):
            return value
        raise serializers.ValidationError(u'hexPubkey有误')
    def validate(self, data):
        '''
        1.初始值
        2.余额充足
        '''
        data['way'] = False
        data['agent'] = AGENT_PUBKEY
        otcId = data['id']
        del data['id']
        sao = WT.get_agency_order(otcId)
        data['otcId'] = otcId
        client = WT.pubkey_to_compress(data['hexPubkey'])
        amount = sao.amount*sao.price
        address = pubkey_to_address(client)
        data['client'] = client
        data['price'] = sao.price
        data['amount'] = amount
        data['address'] = address
        data['assetId'] = sao.assetId
        data['valueId'] = sao.valueId
        if WT.get_asset_balance(address,data['valueId']) < amount:
            raise serializers.ValidationError(u"余额不足")
        data['status'] = MatchStatus.WaitingForSignature.value
        data['order'] = WT.get_match_order_in_status(data['status'])
        return data
    def create(self, validated_data):
        return WT.create_agency_order(validated_data)

class ICOBidOrderSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=True)
    hexPubkey = serializers.CharField(required=True, max_length=130)
    class Meta:
        model = AgencyOrder
    def validate_id(self, value):
        icoId = value
        if icoId <= 0:
            raise serializers.ValidationError(u'id:%s值必须为整数' % icoId)
        if not IT.ico_exist_by_id(icoId):
            raise serializers.ValidationError(u'不存在此ICO项目')
        if not IT.ico_is_waiting_promise(icoId):
            raise serializers.ValidationError(u'尚未进入兑现期')
        return value
    def validate_hexPubkey(self, value):
        if validate_hex_field(value,130,'hexPubkey'):
            return value
        raise serializers.ValidationError(u'hexPubkey有误')
    def validate(self, data):
        '''
        0.地址相符
        1.状态相符,包括买家状态
        2.余额充足
        2.初始值
        '''
        # step 0:
        icoId = data['id']
        ico = IT.get_ico_by_id(icoId)
        client = WT.pubkey_to_compress(data['hexPubkey'])
        address = pubkey_to_address(client)
        if ico.adminAddress != address:
            raise serializers.ValidationError(u'非众筹发起地址')
        # step 1
        if ICOStatus.WaitingForPromise.value != ico.status:
            raise serializers.ValidationError(u'众筹未达100%')
        if not IT.ico_sellers_are_all_confirm(ico.id):
            raise serializers.ValidationError(u'请等待所有用户的交易确认，约20s后再操作')
        if not IT.ico_buyers_are_all_confirm(ico.id):
            raise serializers.ValidationError(u'请等待上一笔承兑交易确认，约20s后再操作')
        if ico.currentShares != ico.totalShares:
            raise serializers.ValidationError(u'份额有误')
        # step 2:
        baos = IT.get_ico_sellers(ico.id, MAX_ICO_BUYER)
        if not baos:
            raise serializers.ValidationError(u"查无挂单")
        amount= reduce(lambda a,b:a+b, [b.amount for b in baos])
        valueAmount = reduce(lambda a,b:a+b, [b.icoAmount for b in baos])
        if amount > ico.totalShares*ico.assetPerShare:
            raise serializers.ValidationError(u"asset amount 计算错误")
        '''
        if valueAmount > ico.totalShares*ico.valuePerShare:
            raise serializers.ValidationError(u"value amount 计算错误")
        '''
        if WT.get_asset_balance(address,ico.valueId) < valueAmount:
            raise serializers.ValidationError(u"余额不足")
        # step 3:
        del data['id']
        data['agent'] = AGENT_PUBKEY
        data['way'] = False
        data['option'] = Option.BuyerICO.value
        data['address'] = address
        data['client'] = client
        data['amount'] = valueAmount
        data['price'] = ico.price
        data['assetId'] = ico.assetId
        data['valueId'] = ico.valueId
        data['icoId'] = icoId
        data['icoAmount'] = amount
        data['status'] = MatchStatus.WaitingForSignature.value
        data['order'] = WT.get_match_order_in_status(data['status'])
        return data
    def create(self, validated_data):
        return WT.create_agency_order(validated_data)

class ICOAskOrderSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=True)
    shares = serializers.IntegerField(required=True)
    hexPubkey = serializers.CharField(required=True, max_length=130)
    password = serializers.CharField(required=True, max_length=64)
    class Meta:
        model = AgencyOrder
    def validate_id(self, value):
        icoId = value
        if icoId <= 0:
            raise serializers.ValidationError(u'id:%s值必须为整数' % icoId)
        if not IT.ico_is_active(icoId):
            raise serializers.ValidationError(u'id:%s无效值' % icoId)
        return value
    def validate_shares(self, value):
        if value <= 0:
            raise serializers.ValidationError(u'shares值必须为正整数')
        return value
    def validate_hexPubkey(self, value):
        if validate_hex_field(value,130,'hexPubkey'):
            return value
        raise serializers.ValidationError(u'hexPubkey有误')
    def validate_password(self,value):
        value = value.strip()
        if len(value) > 64:
            raise serializers.ValidationError(u'密码过长')
        return value
    def validate(self, data):
        '''
        -1.核对密码
        0.剩余份额足够
        1.地址不能为adminAddress
        2.余额充足
        3.初始值
        '''
        # step -1
        icoId = data['id']
        password = data['password']
        del data['password']
        print '*'*10,password
        if not IT.ico_password_correct(icoId, password):
            raise serializers.ValidationError(u'密码有误')
        # step 0:
        shares = data['shares']
        if not IT.shares_acceptable(icoId, shares):
            raise serializers.ValidationError(u'%s此份额不可接受' % shares)
        ico = IT.get_ico_by_id(icoId)
        # step 1:
        client = WT.pubkey_to_compress(data['hexPubkey'])
        address = pubkey_to_address(client)
        if ico.adminAddress == address:
            raise serializers.ValidationError(u'发起者地址不可申购')
        # step 2:
        amount = ico.assetPerShare*shares
        if WT.get_asset_balance(address,ico.assetId) < amount:
            raise serializers.ValidationError(u"余额不足")
        # step 3:
        del data['id']
        del data['shares']
        data['agent'] = AGENT_PUBKEY
        data['way'] = True
        data['option'] = Option.BuyerICO.value
        data['address'] = address
        data['client'] = client
        data['amount'] = amount
        data['price'] = ico.price
        data['assetId'] = ico.assetId
        data['valueId'] = ico.valueId
        data['icoId'] = icoId
        data['earlyBird'] = IT.get_early_bird(ico,shares)
        data['icoAmount'] = ico.valuePerShare*shares+data['earlyBird']
        data['status'] = MatchStatus.WaitingForSignature.value
        data['order'] = WT.get_match_order_in_status(data['status'])
        data['contractAddress'] = WT.get_contract_address(data['client'],data['agent'],data['assetId'],data['valueId'],data['way'],data['price'])
        return data
    def create(self, validated_data):
        return WT.create_agency_order(validated_data)

class ICOSignatureSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=True)
    signature = serializers.CharField(required=True, max_length=128)
    class Meta:
        model = AgencyOrder
    def validate_id(self, value):
        if not WT.agency_order_exist(value):
            raise serializers.ValidationError(u'不存在')
        if not WT.agency_order_for_ico(value):
            raise serializers.ValidationError(u'类型错误')
        return value
    def validate_signature(self, value):
        if validate_hex_field(value,128,'signature'):
            return value
    @transaction.atomic
    def validate(self, data):
        '''
        0.判断状态
        1.验证签名
        2.发送交易
        3.更新ICO状态
        '''
        # step 0
        oid = data['id']
        ao = WT.get_agency_order(oid)
        if MatchStatus.WaitingForSignature.value != ao.status:
            raise serializers.ValidationError(u'状态错误')
        # step 1
        signature = data['signature']
        hexPubkey = ao.hexPubkey
        tran = cache.get(ao.prevHash)
        if not tran:
            ao.delete()
            raise serializers.ValidationError(u'操作超时')
        if not WT.verify(hexPubkey,tran,signature):
            raise serializers.ValidationError(u'无效签名')
        ao.signature = signature
        # ico = IT.get_ico_by_id(ao.icoId)
        ico = ICO.objects.select_for_update().get(id=ao.icoId)
        if ao.way:
            shares = ao.amount/ico.assetPerShare
            if ico.currentShares + shares > ico.totalShares:
                raise serializers.ValidationError(u'份额超限')
            aos = [ao]
            if 'Share' == WT.get_asset_type(ao.assetId):
                sao = WT.create_zero_id_agency_order(ao.client,ao.agent,ao.assetId,ao.valueId,ao.way,ao.price)
                sao.signature = WT.sign(AGENT_PRIKEY, tran)
                aos.append(sao)
            print '>'*5,'ICO ask: amount:%s  price:%s' % (ao.amount, ao.price)
            send, msg = WT.sendrawtransaction(aos, tran)
            if not send:
                ao.delete()
                raise serializers.ValidationError(msg)
            ao.status = MatchStatus.Unconfirmation.value
            ao.save()
            ico.currentShares += shares
            if ico.currentShares == ico.totalShares:
                ico.status = ICOStatus.WaitingForPromise.value
            ico.save()
        else:#承兑
            if ico.adminAddress != ao.address:
                raise serializers.ValidationError(u'非众筹发起者')
            if ICOStatus.WaitingForPromise.value != ico.status:
                raise serializers.ValidationError(u'众筹未达100%')
            if not IT.ico_sellers_are_all_confirm(ico.id):
                raise serializers.ValidationError(u'请等待所有用户的交易确认，约20s后再操作')
            if not IT.ico_buyers_are_all_confirm(ico.id):
                raise serializers.ValidationError(u'请等待上一笔承兑交易确认，约20s后再操作')
            baos = IT.get_ico_sellers(ico.id, MAX_ICO_BUYER)
            aos = [ao]
            for b in baos:
                b.ori_id = b.id
                b.id = 0
                b.signature = WT.sign(AGENT_PRIKEY, tran)
                aos.append(b)
            # send
            print '>'*5,'ICO bid: amount:%s  price:%s' % (ao.amount, ao.price)
            send, msg = WT.sendrawtransaction(aos, tran)
            if not send:
                ao.delete()
                raise serializers.ValidationError(msg)
            # update ao
            ao.status = MatchStatus.Unconfirmation.value
            ao.save()
            # update ico
            ico.txid = ao.prevHash
            ico.save()
            # add history
            History(option=Option.BuyerICO.value,
                    marketId = ico.marketId,
                    # fromAddress=ao.address,
                    # fromRealAddress = ao.address,
                    fromId = ao.id,
                    toAddress=ao.address,
                    toRealAddress = ao.address,
                    toId = ao.id,
                    way = False,
                    assetId = ico.assetId,
                    amount = ao.icoAmount,
                    price = ico.price,
                    redeem=True,
                    txid = ico.txid,
                    redeemTxid=ico.txid).save()
            baos_dict = {}
            baos2 = []
            for b in baos:
                b.id = b.ori_id
                del b.ori_id
                baos2.append([b.contractAddress,b.address,b.id,b.icoAmount])
                if baos_dict.has_key(b.contractAddress):
                    baos_dict[b.contractAddress][2] += b.icoAmount
                else:
                    baos_dict[b.contractAddress] = [b.address,b.id,b.icoAmount]
                b.status = MatchStatus.Finish.value
                b.save()
            print 'baos_dict:',baos_dict
            for conAdd in baos_dict:
                History(option=Option.BuyerICO.value,
                        marketId = ico.marketId,
                        fromAddress=ao.address,
                        fromRealAddress = ao.address,
                        fromId = ao.id,
                        toAddress=conAdd,
                        # toAddress=i[0],
                        toRealAddress = baos_dict[conAdd][0],
                        # toRealAddress = i[1],
                        toId = baos_dict[conAdd][1],
                        # toId = i[2],
                        way = True,
                        assetId = ico.valueId,
                        amount = baos_dict[conAdd][2],
                        # amount = i[3],
                        price = ico.price,
                        txid = ico.txid,
                        redeem=False).save()
            # update ico
            if IT.ico_sellers_are_all_finish(ico.id):
                ico.status = ICOStatus.Success.value
                ico.save()
        return data

class ICOCheckPasswordSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=True)
    password = serializers.CharField(required=True, max_length=64)
    class Meta:
        model = ICO
    def validate_id(self, value):
        icoId = value
        if icoId <= 0:
            raise serializers.ValidationError(u'id:%s值必须为整数' % icoId)
        if not IT.ico_is_active(icoId):
            raise serializers.ValidationError(u'id:%s无效值' % icoId)
        return value
    def validate_password(self,value):
        value = value.strip()
        if len(value) > 64:
            raise serializers.ValidationError(u'密码过长')
        return value
    def validate(self, data):
        '''核对密码'''
        icoId = data['id']
        password = data['password']
        if not IT.check_password(icoId, password):
            raise serializers.ValidationError(u'密码有误')
        return data

class ANCClaimSerializer(serializers.Serializer):
    hexPubkey = serializers.CharField(required=True, max_length=130)
    class Meta:
        model = ANCClaim
    def validate_hexPubkey(self, value):
        if validate_hex_field(value,130,'hexPubkey'):
            return value
    def validate(self, data):
        '''计算地址,判断是否可提取'''
        try:
            hexPubkey = data['hexPubkey']
            client = WT.pubkey_to_compress(data['hexPubkey'])
            data['address'] = pubkey_to_address(client)
        except:
            raise serializers.ValidationError(u'hexPubkey有误')
            data['height'] = cache.get('height')
        result = WT.get_claims(data['address'])
        if '0' == result['enable']:
            raise serializers.ValidationError(u'No Gas to claim')
        return data
    def create(self, validated_data):
        return WT.create_ancclaim(validated_data)
class ANCClaimSignSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=True)
    signature = serializers.CharField(required=True, max_length=128)
    class Meta:
        model = ANCClaim
    def validate_id(self, value):
        if not WT.ancclaim_exist(value):
            raise serializers.ValidationError(u'不存在')
        if not WT.ancclaim_accept_signature(value):
            raise serializers.ValidationError(u'无权签名')
        return value
    def validate_signature(self, value):
        if validate_hex_field(value,128,'signature'):
            return value
    def validate(self, data):
        '''验证签名，广播交易,更新状态'''
        signature = data['signature']
        ac = WT.get_ancclaim(data['id'])
        hexPubkey = ac.hexPubkey
        tran = cache.get(ac.txid)
        if not tran:
            ac.delete()
            raise serializers.ValidationError(u'操作超时')
        if not WT.verify(hexPubkey,tran,signature):
            raise serializers.ValidationError(u'无效签名')
        ac.signature = signature
        send, msg = WT.send_claim_transaction(ac, tran)
        if not send:
            raise serializers.ValidationError(msg)
        else:
            ac.status = ClaimStatus.Unconfirmation.value
            ac.save()
        return data
class BankSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bank
        fields = ('id','uid','type','name','nickName','bankName','sort','accountWithBank','account','status')
        
    def create(self, validated_data):
        logger.info(validated_data)
        return WT.create_bank(validated_data)

        
