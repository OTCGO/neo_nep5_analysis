#coding:utf8
import random
import uuid
import datetime
from django.db import models
from django.db.models import Q
from django.utils import timezone
from OTCGO.Enums import MatchStatus,Option,ICOStatus,ClaimStatus
from decimal import Decimal as D

# Create your models here.
class Asset(models.Model):
    '''
    assetType: 'AntShare','AntCoin','Token','Share'
    '''
    assetId=models.CharField(max_length=64,primary_key=True)
    name=models.CharField(max_length=64)
    assetType=models.CharField(max_length=20)
    marketSign=models.CharField(max_length=10, unique=True)
    divisible = models.BooleanField(default=True)
    decimalDigits = models.PositiveSmallIntegerField(default=8)
    @classmethod
    def get_asset_by_market_sign(cls, marketSign):
        try:
            return cls.objects.get(marketSign=marketSign)
        except:
            raise ValueError(marketSign)
    @classmethod
    def get_assetid_by_market_sign(cls, marketSign):
        try:
            return cls.objects.get(marketSign=marketSign).assetId
        except:
            raise ValueError(marketSign)
    @classmethod
    def get_asset(cls, assetId):
        return cls.objects.get(assetId=assetId)
    @classmethod
    def get_market_sign(cls,assetId):
        at = cls.objects.get(assetId = assetId)
        return at.marketSign
    @classmethod
    def get_asset_type(cls,assetId):
        return cls.objects.get(assetId=assetId).assetType
    @classmethod
    def get_divisible(cls,assetId):
        return cls.objects.get(assetId = assetId).divisible
    @classmethod
    def get_name(cls, assetId):
        at = cls.objects.get(assetId = assetId)
        return at.name
    @classmethod
    def exist(cls, assetId):
        return cls.objects.filter(assetId=assetId)
    @classmethod
    def is_share(cls, assetId):
        return 'Share' == cls.objects.get(assetId=assetId).assetType

class Market(models.Model):
    marketId = models.CharField(max_length=20, primary_key=True)
    name = models.CharField(max_length=20)
    price = models.DecimalField(max_digits=20,decimal_places=8,default=D('0'))
    active = models.BooleanField(default=True)
    @classmethod
    def get_market(cls, marketId):
        return cls.objects.get(marketId=marketId)
    @classmethod
    def support(cls,marketId):
        try:
            cls.objects.get(marketId=marketId)
            return True
        except cls.DoesNotExist:
            return False
    @classmethod
    def get_all_marketid(cls):
        ms = cls.objects.all()
        return [m.marketId for m in ms]
    @classmethod
    def update_price(cls, marketId, price):
        m = cls.objects.get(marketId=marketId)
        m.price = price
        m.save()
    @classmethod
    def get_price(cls,marketId):
        market = cls.objects.get(marketId=marketId)
        return str(market.price).rstrip('0').rstrip('.')
    @classmethod
    def get_market_id(cls,assetId,valueId):
        assetSign,valueSign = map(Asset.get_market_sign,[assetId,valueId])
        marketId = assetSign + valueSign
        return marketId
    @classmethod
    def get_price_by_asset(cls,assetId,valueId):
        return cls.get_price(cls.get_market_id(assetId,valueId))
    @classmethod
    def exist(cls,marketId):
        return cls.objects.filter(marketId=marketId)

class Order(models.Model):
    assetId = models.CharField(max_length=64)
    valueId = models.CharField(max_length=64)
    amount = models.DecimalField(max_digits=20,decimal_places=8,default=D('0'))
    price = models.DecimalField(max_digits=20,decimal_places=8,default=D('0'))
    agent = models.CharField(max_length=66)
    way = models.BooleanField(default=True)
    createdTime = models.DateTimeField(auto_now_add=True)
    modifiedTime = models.DateTimeField(auto_now=True)
    prevHash = models.CharField(max_length=64)
    prevIndex = models.PositiveIntegerField(default=0)
    class Meta:
        abstract = True

class AgencyOrder(Order):
    option = models.IntegerField(default=Option.SellerOTC.value)
    address = models.CharField(max_length=34)
    client = models.CharField(max_length=66)
    hexPubkey = models.CharField(max_length=130)
    total = models.DecimalField(max_digits=20,decimal_places=8,default=D('0'))
    signature = models.CharField(max_length=128)
    contractAddress = models.CharField(max_length=34)
    status = models.IntegerField(default=MatchStatus.WaitingForSignature.value)
    order = models.ForeignKey('MatchOrder',related_name='orders')
    redeemTxid = models.CharField(max_length=64,null=True)
    tradeAmount = models.DecimalField(max_digits=20,decimal_places=8,default=D('0'))
    otcId = models.PositiveIntegerField(default=0)
    icoId = models.PositiveIntegerField(default=0)
    icoAmount = models.DecimalField(max_digits=20,decimal_places=8,default=D('0'))
    earlyBird = models.DecimalField(max_digits=20,decimal_places=8,default=D('0'))
    apphash = models.CharField(max_length=40,default='ce3a97d7cfaa770a5e51c5b12cd1d015fbb5f87d')
    @classmethod
    def get_unconfirm_of_address(cls, address, assetId):
        asks = list(cls.objects.filter(Q(address=address)&Q(way=True)&Q(assetId=assetId)&Q(status=MatchStatus.Unconfirmation.value)))
        bids = list(cls.objects.filter(Q(address=address)&Q(way=False)&Q(valueId=assetId)&Q(status=MatchStatus.Unconfirmation.value)))
        return asks + bids
    @classmethod
    def get_unconfirm(cls):
        return cls.objects.filter(status=MatchStatus.Unconfirmation.value)
    @classmethod
    def get_frozen_ask_order(cls,address,assetId,status):
        return list(cls.objects.filter(Q(address=address)&Q(assetId=assetId)&Q(status=status)&Q(way=True)))
    @classmethod
    def get_frozen_bid_order(cls,address,valueId,status):
        return list(cls.objects.filter(Q(address=address)&Q(valueId=valueId)&Q(status=status)&Q(way=False)))
    @classmethod
    def get_seller(cls,option,assetId,valueId,status):
        return cls.objects.filter(Q(option=option)&Q(assetId=assetId)&Q(valueId=valueId)&Q(status=status)&Q(way=True)).order_by('price','amount','createdTime')
    @classmethod
    def get_buyer(cls,option,assetId,valueId,status):
        return cls.objects.filter(Q(option=option)&Q(assetId=assetId)&Q(valueId=valueId)&Q(status=status)&Q(way=False)).order_by('price','amount','createdTime')
    @classmethod
    def get_order_of_address_in_status(cls,address,status):
        return cls.objects.filter(address=address,status=status)
    @classmethod
    def get_order_by_id(cls,oid):
        return cls.objects.get(id=oid)
    @classmethod
    def get_prevhash(cls,oid):
        return cls.objects.get(id=oid).prevHash
    @staticmethod
    def update_prevhash(ao,txid):
        ao.prevHash = txid
        ao.save()
    @classmethod
    def new(cls,datas):
        return cls(**datas)
    @classmethod
    def create(cls,datas):
        return cls.objects.create(**datas)
    @classmethod
    def exist(cls,oid):
        return cls.objects.filter(id=oid)
    @classmethod
    def can_cancel(cls,oid,way):
        ao = cls.objects.get(id=oid)
        return way==ao.way and MatchStatus.WaitingForMatch.value==ao.status
    @classmethod
    def lock_to_update(cls,oid):
        return cls.objects.select_for_update().get(id=oid)
    @classmethod
    def update_status(cls,oid,status):
        ao = cls.objects.get(id=oid)
        ao.status = status
        ao.save()
    @classmethod
    def is_for_ico(cls,oid):
        ao = cls.objects.get(id=oid)
        return Option.BuyerICO.value == ao.option
    @classmethod
    def ico_sellers_are_all_confirm(cls, icoId):
        aos = cls.objects.filter(Q(option=Option.BuyerICO.value)&Q(way=True)&Q(icoId=icoId)&Q(status=MatchStatus.Unconfirmation.value))
        if aos:
            return False
        return True
    @classmethod
    def ico_buyers_are_all_confirm(cls, icoId):
        aos = cls.objects.filter(Q(option=Option.BuyerICO.value)&Q(way=False)&Q(icoId=icoId)&Q(status=MatchStatus.Unconfirmation.value))
        if aos:
            return False
        return True
    @classmethod
    def ico_sellers_are_all_finish(cls, icoId):
        #是否还有未确认的
        aos = cls.objects.filter(Q(option=Option.BuyerICO.value)&Q(way=True)&Q(icoId=icoId)&Q(status=MatchStatus.WaitingForMatch.value))
        if aos:
            return False
        return True
        '''
        aos = cls.objects.filter(Q(option=Option.BuyerICO.value)&Q(way=True)&Q(icoId=icoId)&Q(status=MatchStatus.Finish.value))
        icoAmount = sum([ao.icoAmount-ao.earlyBird for ao in aos])
        ico = ICO().get_ico_by_id(icoId)
        if icoAmount == ico.amountForICO:
            return True
        return False
        '''
    @classmethod
    def get_ico_sellers_on_waiting_for_match(cls, icoId,limit=0):
        aos = list(cls.objects.filter(Q(option=Option.BuyerICO.value)&Q(way=True)&Q(icoId=icoId)&Q(status=MatchStatus.WaitingForMatch.value)))
        if not limit:
            return aos
        else:
            return aos[:limit]
    @classmethod
    def get_ico_sellers_on_finish(cls, icoId):
        return cls.objects.filter(Q(option=Option.BuyerICO.value)&Q(way=True)&Q(icoId=icoId)&Q(status=MatchStatus.Finish.value))
    @classmethod
    def get_waiting_for_match_of_otc(cls, address,marketId):
        if 'ALL' == marketId:
            return cls.objects.filter(Q(address=address)&Q(option=Option.SellerOTC.value)&Q(status=MatchStatus.WaitingForMatch.value))
        assetId,valueId = map(Asset.get_assetid_by_market_sign, [marketId[:3], marketId[3:]])
        return cls.objects.filter(Q(assetId=assetId)&Q(valueId=valueId)&Q(address=address)&Q(option=Option.SellerOTC.value)&Q(status=MatchStatus.WaitingForMatch.value))
    @classmethod
    def get_waiting_for_match_of_ico(cls, address):
        return cls.objects.filter(Q(address=address)&Q(option=Option.BuyerICO.value)&Q(way=True)&Q(status=MatchStatus.WaitingForMatch.value))

class MatchOrder(Order):
    option = models.IntegerField(default=Option.SellerOTC.value)
    marketId = models.CharField(max_length=10)
    status = models.IntegerField(default=MatchStatus.Normal.value)
    @classmethod
    def get_order_in_status(cls, status):
        return cls.objects.get(status=status)

class Transfer(models.Model):
    source =            models.CharField(max_length=34)
    dest =              models.CharField(max_length=34) 
    assetId =           models.CharField(max_length=64)
    amount =            models.DecimalField(max_digits=20,decimal_places=8,default=D('0'))
    hexPubkey =         models.CharField(max_length=130)
    txid =              models.CharField(max_length=64,null=True)
    confirm =           models.BooleanField(default=False)
    broadcast =         models.BooleanField(default=False)
    createdTime = models.DateTimeField(auto_now_add=True)
    modifiedTime = models.DateTimeField(auto_now=True)
    @classmethod
    def get_unconfirm(cls):
        return cls.objects.filter(confirm=False)
    @classmethod
    def get_broadcast_uncomfirm_transfer(cls,source,assetId):
        return cls.objects.filter(Q(source=source)&Q(assetId=assetId)&Q(confirm=False)&Q(broadcast=True))
    @classmethod
    def get_transfer(cls,address):
        return cls.objects.filter(Q(source=address)&Q(broadcast=True)&Q(confirm=True)).order_by('-id')
    @classmethod
    def create(cls,datas):
        return cls.objects.create(**datas)
    @classmethod
    def exist(cls,tid):
        return cls.objects.filter(id=tid)
    @classmethod
    def get_transfer_by_id(cls,tid):
        return cls.objects.get(id=tid)

class UID(models.Model):
    address = models.CharField(max_length=34,unique=True)
    uid = models.CharField(max_length=10,unique=True)
    nickName = models.CharField(max_length=50)
    createdTime = models.DateTimeField(auto_now_add=True)
    modifiedTime = models.DateTimeField(auto_now=True)
    @classmethod
    def new_uid(cls):
        letters = '23456789ABCDEFGHJKLMNPQRSTUVWXYZ'
        while True:
            newUid = ''
            for i in range(6):
                newUid += random.choice(letters)
            else:
                try:
                    cls.objects.get(uid=newUid)
                except cls.DoesNotExist:
                    return newUid
                else:
                    continue
    @classmethod
    def create(cls,address):
        return cls.objects.create(uid=cls.new_uid(),address=address)
    @classmethod
    def get_uid(cls,address):
        return cls.objects.get(address=address)
    @classmethod
    def exist(cls,address):
        return cls.objects.filter(address=address)

class History(models.Model):
    option =            models.IntegerField(default=Option.SellerOTC.value)
    marketId =          models.CharField(max_length=10)
    fromAddress =       models.CharField(max_length=34)
    fromRealAddress =   models.CharField(max_length=34)
    fromId =            models.BigIntegerField()
    toAddress =         models.CharField(max_length=34)
    toRealAddress =     models.CharField(max_length=34)
    toId =              models.BigIntegerField()
    way =               models.BooleanField(default=True)#way=True 卖出
    assetId =           models.CharField(max_length=64)
    amount =            models.DecimalField(max_digits=20,decimal_places=8,default=D('0'))
    price =             models.DecimalField(max_digits=20,decimal_places=8,default=D('0'))
    createdTime =       models.DateTimeField(auto_now_add=True)
    modifiedTime =      models.DateTimeField(auto_now=True)
    redeem =            models.BooleanField(default=False)
    redeemTxid =        models.CharField(max_length=64,null=True)
    txid =              models.CharField(max_length=64,null=True)
    confirm =           models.BooleanField(default=False)
    error =             models.CharField(max_length=1024,null=True)
    show =              models.BooleanField(default=False)
    @classmethod
    def get_volumn(cls,marketId,offset=24):
        offset_time = timezone.now() - datetime.timedelta(hours=offset)
        his = cls.objects.filter(Q(option=Option.SellerOTC.value)&Q(marketId=marketId)&Q(way=False)&Q(createdTime__gte=offset_time)).order_by('createdTime')
        volumn = sum([h.amount for h in his])
        rate = '0'
        if len(his)>=2:
            his = list(his)
            rate = str((his[-1].price-his[0].price)/his[0].price)
        return volumn,rate
    @classmethod
    def get_unredeem_unconfirm(cls):
        return cls.objects.filter(Q(redeem=False)&Q(confirm=False))
    @classmethod
    def get_redeem_unconfirm(cls):
        return cls.objects.filter(Q(redeem=True)&Q(confirm=False))
    @classmethod
    def get_unredeem_of_address_and_asset(cls,address,assetId):
        return cls.objects.filter(Q(toRealAddress=address)&Q(assetId=assetId)&Q(redeem=False))
    @classmethod
    def get_address_history(cls,address,marketId,option):
        if 'otc' == option:
            option = Option.SellerOTC.value
        if 'ico' == option:
            option = Option.BuyerICO.value
        if marketId:
            his = cls.objects.filter(Q(option=option)&Q(toRealAddress=address)&Q(confirm=True)&Q(marketId=marketId)).order_by('-id')
        else:
            his = cls.objects.filter(Q(option=option)&Q(toRealAddress=address)&Q(confirm=True)).order_by('-id')
        return his
    @classmethod
    def get_market_history(cls,marketId):
        his = cls.objects.filter(Q(marketId=marketId)&Q(confirm=True)&Q(show=True)).order_by('-id')
        return his
    @classmethod
    def get_redeem_txid_by_id(cls,hid):
        return cls.objects.get(id=hid).redeemTxid
    @classmethod
    def exist(cls,hid):
        return cls.objects.filter(id=hid)
    @classmethod
    def is_redeem(cls,hid):
        return cls.objects.get(id=hid).redeem
    @classmethod
    def get_history_by_id(cls, hid):
        return cls.objects.get(id=hid)

#For ICO
class ICO(models.Model):
    title =             models.CharField(max_length=128)
    marketId =          models.CharField(max_length=10)
    assetId =           models.CharField(max_length=64)
    valueId =           models.CharField(max_length=64)
    assetCapacity =     models.DecimalField(max_digits=20,decimal_places=8,default=D('0'))#众筹资产的总量
    amountForICO =      models.DecimalField(max_digits=20,decimal_places=8,default=D('0'))#用来众筹的总量
    amountToICO =       models.DecimalField(max_digits=20,decimal_places=8,default=D('0'))#众筹多少valueId
    assetPerShare =     models.DecimalField(max_digits=20,decimal_places=8,default=D('0'))#每份出让数量
    valuePerShare =     models.DecimalField(max_digits=20,decimal_places=8,default=D('0'))#每份筹集数量
    price =             models.DecimalField(max_digits=20,decimal_places=8,default=D('0'))#价格=value/asset
    totalShares =       models.PositiveIntegerField(default=100)#筹集总份数
    currentShares =     models.PositiveIntegerField(default=0)#已筹集份数
    adminAddress =      models.CharField(max_length=34) #管理员地址
    txid =              models.CharField(max_length=64,null=True)
    status =            models.IntegerField(default=ICOStatus.NotStart.value)
    startTime =         models.DateTimeField()
    endTime =           models.DateTimeField()
    createdTime =       models.DateTimeField(auto_now_add=True)
    modifiedTime =      models.DateTimeField(auto_now=True)
    password =          models.CharField(max_length=64,default='password')
    @classmethod
    def password_correct(cls,icoId, pwd):
        ico = cls.get_by_id(icoId)
        return pwd==ico.password
    @classmethod
    def get_current_shares_by_id(cls,icoId):
        ico = cls.get_by_id(icoId)
        return ico.currentShares
    @classmethod
    def get_total_shares_by_id(cls,icoId):
        ico = cls.get_by_id(icoId)
        return ico.totalShares
    @classmethod
    def get_by_id(cls,icoId):
        return cls.objects.get(id=icoId)
    @classmethod
    def exist(cls,icoId):
        return cls.objects.filter(id=icoId)
    @classmethod
    def is_active(cls,icoId):
        ico = cls.get_by_id(icoId)
        if ICOStatus.Proceeding.value == ico.status:
            return True
        return False
    @classmethod
    def lock_to_update(cls,icoId):
        return cls.objects.select_for_update().get(id=icoId)
    @classmethod
    def is_waiting_promise(cls,icoId):
        ico = cls.objects.get(id=icoId)
        return ICOStatus.WaitingForPromise.value == ico.status
    @classmethod
    def get_unstarts(cls):
        return cls.objects.filter(status=ICOStatus.NotStart.value)
    @classmethod
    def update_status(cls, icoId, status):
        ico = cls.objects.get(id=icoId)
        ico.status = status
        ico.save()

class EarlyBird(models.Model):
    icoId =             models.PositiveIntegerField()
    startTime =         models.DateTimeField()
    endTime =           models.DateTimeField()
    rewardPerShare =    models.DecimalField(max_digits=20,decimal_places=8,default=D('0'))#每份奖励
    createdTime =       models.DateTimeField(auto_now_add=True)
    modifiedTime =      models.DateTimeField(auto_now=True)
    @classmethod
    def get_by_icoid_and_time(cls, icoId, currentTime):
        ebs = cls.objects.filter(icoId=icoId)
        for eb in ebs:
            if eb.startTime <= currentTime and eb.endTime > currentTime:
                return eb
        return None

class ANCClaim(models.Model):
    address =       models.CharField(max_length=34)
    hexPubkey =     models.CharField(max_length=130)
    txid =          models.CharField(max_length=64,null=True)
    status =        models.IntegerField(default=ClaimStatus.WaitingForSignature.value)
    height =        models.PositiveIntegerField(default=0)
    signature =     models.CharField(max_length=128,null=True)
    createdTime =   models.DateTimeField(auto_now_add=True)
    modifiedTime =  models.DateTimeField(auto_now=True)
    @classmethod
    def create(cls,datas):
        return cls.objects.create(**datas)
    @staticmethod
    def update_txid(ac,txid):
        ac.txid = txid
        ac.save()
    @classmethod
    def exist(cls, acid):
        return cls.objects.filter(id=acid)
    @classmethod
    def accept_signature(cls, acid):
        ac = cls.objects.get(id=acid)
        return ClaimStatus.WaitingForSignature.value == ac.status
    @classmethod
    def get_by_id(cls, acid):
        return cls.objects.get(id=acid)
    @classmethod
    def check_unconfirm(cls, address):
        return cls.objects.filter(Q(address=address)&Q(status=ClaimStatus.Unconfirmation.value))
    @classmethod
    def get_unconfirm(cls):
        return cls.objects.filter(Q(status=ClaimStatus.Unconfirmation.value))

#Pay
"银行卡"
class Bank(models.Model):
    id =        models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    uid =       models.CharField(max_length=10)
    type =      models.IntegerField(default=D('0'),null=True)
    name =      models.CharField(max_length=64)
    nickName =  models.CharField(max_length=50,null=True)
    bankName =  models.CharField(max_length=50,null=True)
    sort =      models.PositiveSmallIntegerField(default=0)
    accountWithBank = models.CharField(max_length=50,null=True)
    account =   models.CharField(max_length=50,null=True)
    status =    models.PositiveSmallIntegerField(default=0)
    createdTime =   models.DateTimeField(auto_now_add=True)
    modifiedTime =  models.DateTimeField(auto_now=True)
    @classmethod
    def create(cls,datas):
        return cls.objects.create(**datas)

class Pay(models.Model):
    id =        models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    uid =       models.CharField(max_length=10)
    txid =      models.CharField(max_length=64,null=True)
    bankId =    models.CharField(max_length=50,null=True)
    sort =      models.PositiveSmallIntegerField(default=0)
    amount =    models.DecimalField(max_digits=20,decimal_places=8,default=D('0'))
    fee =       models.DecimalField(max_digits=20,decimal_places=8,default=D('0'))
    feeRate =   models.DecimalField(max_digits=20,decimal_places=8,default=D('0'))
    feeTxid =   models.CharField(max_length=64,null=True)
    feeType =   models.PositiveSmallIntegerField(default=0)
    note =      models.CharField(max_length=128)
    status =    models.PositiveSmallIntegerField(default=0)
    createdTime =   models.DateTimeField(auto_now_add=True)
    modifiedTime =  models.DateTimeField(auto_now=True)
    class Meta:
        abstract = True

"冲值"
class Deposit(Pay):
    error =     models.CharField(max_length=128)
    randomStr = models.CharField(max_length=8)

"提现"
class Withdraw(Pay):
    pass

"签名"
class SignCheck(models.Model):
    signature = models.CharField(max_length=128, primary_key=True)
    pubkey =    models.CharField(max_length=66)
