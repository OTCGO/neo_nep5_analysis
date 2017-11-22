#coding:utf8
import os
import pytz
import time
from math import ceil
from OTCGO.Enums import MatchStatus
from django.db.models import Q
from django.utils import timezone
from django.core.cache import cache
from django.shortcuts import render
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.forms.models import model_to_dict
from rest_framework import status, viewsets, mixins, serializers
from rest_framework.response import Response
from .serializers import BankSerializer,MarketSerializer, AgencyOrderSerializer, SignSerializer, OrderCancelSerializer, TransferSerializer, UIDSerializer, RedeemCreateSerializer, RedeemSignatureSerializer, OTCAskOrderSerializer, OTCBidOrderSerializer, FreeAskOrderSerializer,FreeBidOrderSerializer,OTCSignSerializer, ICOAskOrderSerializer, ICOBidOrderSerializer, ICOSignatureSerializer, ICOCheckPasswordSerializer,ANCClaimSerializer,ANCClaimSignSerializer
from django.db import transaction
from decimal import Decimal as D,ROUND_DOWN,ROUND_HALF_DOWN
from AntShares.Cryptography.Helper import pubkey_to_address
from OTCGO.settings import RMB_ASSET,NEED_RMB,ANC_ASSET,ANS_ASSET,TIME_ZONE as TZ,MAX_ICO_BUYER
from wallet.models import *
from wallet.AntAddress import AntAddress
from wallet.WalletTool import WalletTool as WT
from wallet.ICOTool import ICOTool as IT
from .Helper import *
from rest_framework.parsers import JSONParser
import logging

logger = logging.getLogger('django')

ASCII_NORMAL_RANGE = [ord(x) for x in '0123456789abcdefghijklmnopqrstuvwxyz']


# Create your views here.
class ANCClaimViewSet(viewsets.GenericViewSet):
    queryset = ANCClaim.objects.all()
    serializer_class = ANCClaimSerializer
    def create(self, request):
        '''
        提取小蚁币 
        ---
        请求参数:
            
            hexPubkey 类型:string 长度:130 含义:登录钱包时拿到的公钥 示例:"0483cdbc3f4d2213043c19d6bd041c08fbe0a3bacd43ef695500a1b33c609a9e8a180eee2ada65ddb65154863c57bac9ab1b89a61593235991d5fb6f627c0cadbd"

        响应参数:

            transaction 类型:string 最大长度:1024 含义:交易 示例:"80000001c686a413df35c45620a33c44ba892ea4cfcc81f59573c96777a994e08bf6211e010002e72d286979ee6cb1b7e65dfddfb2e384100b8d148e7758de42e4168b71792c6020523d43170000003d8acd68cce2640a2bf00bfa06022fe98441380ce72d286979ee6cb1b7e65dfddfb2e384100b8d148e7758de42e4168b71792c60e0b68930cc000000138bb1207f869b6c08a6fbd911251fcbf8194aa9"  
            order 类型:字段对象 含义:新建的订单详情  
                address 类型:string 长度:34 含义:小蚁地址 示例:"AHZDq78w1ERcDYVBWjU5owWcbFZKLvhg7X"  
                createdTime 类型:string 长度:20 含义:订单创建时间 示例:"2017-01-19T15:12:03Z"  
                id 类型:integer 含义:订单ID 示例:7  
        '''
        serializer = ANCClaimSerializer(data=request.data)
        if serializer.is_valid():
            ac = serializer.save()
            response_dict = {}
            response_dict['order'] = model_to_dict(ac, fields=['id','address'])
            response_dict['order'].update({'createdTime':ac.createdTime})
            untran,txid = WT.get_claim_transaction(ac.address)
            WT.update_ancclaim_txid(ac,txid)
            cache.set(txid, untran)
            response_dict['transaction'] = untran
            return Response(response_dict, status=status.HTTP_201_CREATED)
        else:
            if serializer.errors.has_key('non_field_errors'):
                errors = {'error':serializer.errors['non_field_errors'][0]}
                return Response(errors, status=status.HTTP_400_BAD_REQUEST)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ANCClaimSignViewSet(viewsets.GenericViewSet):
    queryset = ANCClaim.objects.all()
    serializer_class = ANCClaimSignSerializer
    def create(self, request):
        '''
        对订单签名
        ---
        请求参数：

            id          类型:integer                    含义:订单ID                     示例:9 
            signature   类型:string     长度:128        含义:使用私钥进行签名后的内容   示例:"1aa0767ef1ca4c1ee5cee6b68a7f0d95754b2f12332c2c0165e2f47532541b874ce24a18b6d0f03ee59fd6904935ac7cb16b859f0b48546afb92ba6a8d69161c"

        响应参数:
            
            result  类型:boolean 含义:签名结果,为true说明签名有效;false签名无效  示例:true  
            txid    类型:string 长度:64 含义:交易ID 示例:"6c06696109f81d82d99039acdf89db30c84db0538dd5fbf2db26c9ca9194a95e" 
        '''
        serializer = ANCClaimSignSerializer(data=request.data)
        if serializer.is_valid():
            ac = WT.get_ancclaim(serializer.data['id'])
            response_dict = {'result':True, 'txid':ac.txid}
            return Response(response_dict, status=status.HTTP_201_CREATED)
        else:
            if serializer.errors.has_key('non_field_errors'):
                errors = {'result':False, 'error':serializer.errors['non_field_errors'][0]}
                return Response(errors, status=status.HTTP_400_BAD_REQUEST)
            r = {'result':False,'error':''}
            for key,v in serializer.errors.items():
                r['error'] += key+':'+''.join(v)
            return Response(r, status=status.HTTP_400_BAD_REQUEST)

class ICOCheckPasswordViewSet(viewsets.GenericViewSet):
    queryset = ICO.objects.all()
    serializer_class = ICOCheckPasswordSerializer
    def create(self, request, format=None):
        '''
        校验ICO口令
        ---
        请求参数：

            id          类型:integer                    含义:ICO ID                     示例:9 
            password    类型:string     长度:64         含义:口令                       示例:"whoareyou?"

        响应参数:
            
            result  类型:boolean 含义:签名结果,为true说明签名有效;false签名无效  示例:true  
        '''
        serializer = ICOCheckPasswordSerializer(data=requests.data)
        if serializer.is_valid():
            return Response({'result':True}, status=status.HTTP_201_CREATED)
        else:
            return Response({'result':False}, status=status.HTTP_400_BAD_REQUEST)

class ICOOrderListViewSet(viewsets.ViewSet):
    lookup_url_kwarg = 'address'
    def list(self, request, address, format=None):
        '''
        获取指定地址下的订单
        ---
        请求参数:
            
            address 类型:string 长度:34 含义:小蚁地址 示例:"AHZDq78w1ERcDYVBWjU5owWcbFZKLvhg7X"

        响应参数:

            data 类型:数组 含义:卖单列表  
                id 类型:integer 含义:订单ID 示例:7
                address 类型:string 长度:34 含义:小蚁地址 示例:"AHZDq78w1ERcDYVBWjU5owWcbFZKLvhg7X"  
                name 类型:string 最大长度:64 含义:资产名称 示例:"小蚁股"  
                assetId 类型:string 长度:64 含义:资产ID 示例:"602c79718b16e442de58778e148d0b1084e3b2dffd5de6b7b16cee7969282de7"  
                valueId 类型:string 长度:64 含义:资产ID 示例:"602c79718b16e442de58778e148d0b1084e3b2dffd5de6b7b16cee7969282de7"  
                amount 类型:string 最大长度:20 含义:投入量 示例:"999.1234"  
                price  类型:string 最大长度:20 含义:价格 示例:"0.001"  
                baseAmount 类型:string 最大长度:20 含义:获取ico资产基本量 示例:"0.001"  
                earlyBird 类型:string 最大长度:20 含义:早鸟奖励 示例:"0.001"  
        '''
        aos = WT.get_waiting_for_match_agency_order_of_ico(address)
        aos_dict = {'data':[]}
        ico_dict = {}
        for ao in aos:
            if not ico_dict.has_key(str(ao.icoId)):
                ico_dict[str(ao.icoId)] = IT.get_ico_by_id(ao.icoId)
            response_dict = model_to_dict(ao, fields=['id','address','assetId','valueId','amount','price','earlyBird'])
            response_dict.update({
                            'name':WT.get_asset_name(ao.valueId),
                            'baseAmount':ao.icoAmount-ao.earlyBird
                    })
            response_dict['price'] = D('1')/response_dict['price']
            response_dict['canCancel'] = False if ico_dict[str(ao.icoId)].status in [ICOStatus.Proceeding.value,ICOStatus.WaitingForPromise.value] else True
            for key in ['amount','baseAmount','earlyBird','price']:
                response_dict[key] = remove_zero(str(response_dict[key]))
            aos_dict['data'].append(response_dict)
        return JsonResponse(aos_dict)

class ICOViewSet(viewsets.ViewSet):
    '''
    获取指定小蚁地址的资产详情
    '''
    lookup_url_kwarg = 'id'
    def retrieve(self, request, id, format=None):
        '''
        获取指定小蚁地址的资产详情
        ---
        请求参数:
            
            id          类型:integer                    含义:ICO ID                     示例:9 

        响应参数:

            title 类型:string 最大长度:64 含义:ICO项目名称 示例:"蓝鲸淘私募"  
            marketId 类型:string 长度:6 含义:交易市场代号 示例:"kacans"
            assetCapacity 类型:string 最大长度:20 含义:众筹发放资产总量 示例:"100000000"  
            amountForICO 类型:string 最大长度:20 含义:用于本次众筹的发放资产总量 示例:"15000000"  
            amountToICO 类型:string 最大长度:20 含义:本次众筹筹集资产数量 示例:"1500"  
            assetPerShare 类型:string 最大长度:20 含义:本次众筹发放资产每份数 示例:"1000000"  
            valuePerShare 类型:string 最大长度:20 含义:本次众筹筹集资产每份数 示例:"100"  
            totalShares 类型:string 最大长度:20 含义:本次众筹总份数 示例:"15"  
            currentShares 类型:string 最大长度:20 含义:本次当前众筹总份数 示例:"10"  
            adminAddress 类型:string 长度:34 含义:众筹发放资产地址 示例:"AHZDq78w1ERcDYVBWjU5owWcbFZKLvhg7X"  
            status 类型:string 长度:34 含义:状态 示例:"notStart"  
            startTime 类型:string 长度:20 含义:众筹开始时间 示例:"2017-05-25 10:00:00"  
            endTime 类型:string 长度:20 含义:众筹结束时间 示例:"2017-05-30 12:00:00"  
            backers 类型:string 长度:20 含义:支持人数 示例:500

        '''
        #Step 1:获取地址下的所有资产
        try:
            ico = IT.get_ico_by_id(id)
        except:
            raise serializers.ValidationError(u'无效值')
        response_dict = model_to_dict(ico, fields=['title','marketId','assetCapacity','amountForICO','amountToICO','assetPerShare','valuePerShare','totalShares','currentShares','adminAddress','txid'])
        for key in ['assetCapacity','amountForICO','amountToICO','assetPerShare','valuePerShare','totalShares','currentShares']:
            response_dict[key] = remove_zero(response_dict[key])
        response_dict['status'] = IT.get_status_string(ico.status)
        tz = pytz.timezone(TZ)
        if IT.is_ico_not_start(ico):
            response_dict['countdown'] = (ico.startTime - timezone.now()).total_seconds()
        elif IT.is_ico_proceeding(ico):
            response_dict['countdown'] = (ico.endTime - timezone.now()).total_seconds()
        else:
            response_dict['countdown'] = 0
        response_dict['startTime'] = ico.startTime.astimezone(tz).strftime('%Y-%m-%d %H:%M:%S')
        response_dict['endTime'] = ico.endTime.astimezone(tz).strftime('%Y-%m-%d %H:%M:%S')
        response_dict['backers'] = len(IT.get_ico_addresses(ico.id))
        return JsonResponse(response_dict)

class ICOSignViewSet(viewsets.GenericViewSet):
    queryset = AgencyOrder.objects.all()
    serializer_class = ICOSignatureSerializer 
    @transaction.atomic
    def create(self, request):
        '''
        对订单签名
        ---
        请求参数：

            id          类型:integer                    含义:订单ID                     示例:9 
            signature   类型:string     长度:128        含义:使用私钥进行签名后的内容   示例:"1aa0767ef1ca4c1ee5cee6b68a7f0d95754b2f12332c2c0165e2f47532541b874ce24a18b6d0f03ee59fd6904935ac7cb16b859f0b48546afb92ba6a8d69161c"

        响应参数:
            
            result  类型:boolean 含义:签名结果,为true说明签名有效;false签名无效  示例:true  
            txid    类型:string 长度:64 含义:交易ID 示例:"6c06696109f81d82d99039acdf89db30c84db0538dd5fbf2db26c9ca9194a95e" 
        '''
        serializer = ICOSignatureSerializer(data=request.data)
        if serializer.is_valid():
            ao = WT.get_agency_order(serializer.data['id'])
            response_dict = {'result':True,'txid':ao.prevHash}
            return Response(response_dict, status=status.HTTP_201_CREATED)
        else:
            if serializer.errors.has_key('non_field_errors'):
                errors = {'error':serializer.errors['non_field_errors'][0]}
                return Response(errors, status=status.HTTP_400_BAD_REQUEST)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ICOBidOrderViewSet(viewsets.GenericViewSet):
    queryset = AgencyOrder.objects.all()
    serializer_class = ICOBidOrderSerializer
    def create(self, request):
        '''
        众筹发起者兑现承诺
        ---
        请求参数:
            
            id 类型:integer 含义:ICO ID 示例:1  
            hexPubkey 类型:string 长度:130 含义:登录钱包时拿到的公钥 示例:"0483cdbc3f4d2213043c19d6bd041c08fbe0a3bacd43ef695500a1b33c609a9e8a180eee2ada65ddb65154863c57bac9ab1b89a61593235991d5fb6f627c0cadbd"

        响应参数:

            transaction 类型:string 最大长度:1024 含义:转账至合约地址的交易待签名部分 示例:"80000001c686a413df35c45620a33c44ba892ea4cfcc81f59573c96777a994e08bf6211e010002e72d286979ee6cb1b7e65dfddfb2e384100b8d148e7758de42e4168b71792c6020523d43170000003d8acd68cce2640a2bf00bfa06022fe98441380ce72d286979ee6cb1b7e65dfddfb2e384100b8d148e7758de42e4168b71792c60e0b68930cc000000138bb1207f869b6c08a6fbd911251fcbf8194aa9"  
            order 类型:字段对象 含义:新建的订单详情  
                id 类型:integer 含义:订单ID 示例:7  
                address 类型:string 长度:34 含义:小蚁地址 示例:"AHZDq78w1ERcDYVBWjU5owWcbFZKLvhg7X"  
                client 类型:string 长度:66 含义:请求参数address所对应的压缩版公钥 示例:"0383cdbc3f4d2213043c19d6bd041c08fbe0a3bacd43ef695500a1b33c609a9e8a"  
                assetId 类型:string 长度:64 含义:资产ID 示例:"602c79718b16e442de58778e148d0b1084e3b2dffd5de6b7b16cee7969282de7"  
                valueId 类型:string 长度:64 含义:资产ID 示例:"5fd33b8d1ff8185b30f59c35313e60663d026eb8351d0dd9fd6f60eb279b301a"  
                amount 类型:string 最大长度:20 含义:未成交数量 示例:"999.1234"  
                createdTime 类型:string 长度:20 含义:订单创建时间 示例:"2017-01-19T15:12:03Z"  
                modifiedTime 类型:string 长度:20 含义:订单最后修改时间 示例:"2017-01-19T15:12:03Z"  
        '''
        serializer = ICOBidOrderSerializer(data=request.data)
        if serializer.is_valid():
            ao = serializer.save()
            response_dict = {}
            response_dict['order'] = model_to_dict(ao, fields=['id','address','client','assetId','valueId','amount'])
            response_dict['order']['amount'] = str(response_dict['order']['amount'])
            response_dict['order'].update({'createdTime':ao.createdTime,'modifiedTime':ao.modifiedTime})
            baos = IT.get_ico_sellers(ao.icoId, MAX_ICO_BUYER)
            untran,txid = WT.generate_unsignature_transaction_for_ico(ao,baos)
            WT.update_agency_order_prevhash(ao,txid)
            cache.set(txid, untran)
            response_dict['transaction'] = untran
            return Response(response_dict, status=status.HTTP_201_CREATED)
        else:
            if serializer.errors.has_key('non_field_errors'):
                errors = {'error':serializer.errors['non_field_errors'][0]}
                return Response(errors, status=status.HTTP_400_BAD_REQUEST)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ICOAskOrderViewSet(viewsets.GenericViewSet):
    queryset = AgencyOrder.objects.all()
    serializer_class = ICOAskOrderSerializer
    def create(self, request):
        '''
        卖家参与众筹 
        ---
        请求参数:
            
            id 类型:integer 含义:ICO ID 示例:1  
            shares 类型:integer 含义:参与份额 示例:1  
            hexPubkey 类型:string 长度:130 含义:登录钱包时拿到的公钥 示例:"0483cdbc3f4d2213043c19d6bd041c08fbe0a3bacd43ef695500a1b33c609a9e8a180eee2ada65ddb65154863c57bac9ab1b89a61593235991d5fb6f627c0cadbd"
            password 类型:string 长度:64 含义:密码 示例:"theAnswerIs:42"

        响应参数:

            transaction 类型:string 最大长度:1024 含义:转账至合约地址的交易待签名部分 示例:"80000001c686a413df35c45620a33c44ba892ea4cfcc81f59573c96777a994e08bf6211e010002e72d286979ee6cb1b7e65dfddfb2e384100b8d148e7758de42e4168b71792c6020523d43170000003d8acd68cce2640a2bf00bfa06022fe98441380ce72d286979ee6cb1b7e65dfddfb2e384100b8d148e7758de42e4168b71792c60e0b68930cc000000138bb1207f869b6c08a6fbd911251fcbf8194aa9"  
            order 类型:字段对象 含义:新建的订单详情  
                id 类型:integer 含义:订单ID 示例:7  
                address 类型:string 长度:34 含义:小蚁地址 示例:"AHZDq78w1ERcDYVBWjU5owWcbFZKLvhg7X"  
                client 类型:string 长度:66 含义:请求参数address所对应的压缩版公钥 示例:"0383cdbc3f4d2213043c19d6bd041c08fbe0a3bacd43ef695500a1b33c609a9e8a"  
                assetId 类型:string 长度:64 含义:资产ID 示例:"602c79718b16e442de58778e148d0b1084e3b2dffd5de6b7b16cee7969282de7"  
                valueId 类型:string 长度:64 含义:资产ID 示例:"5fd33b8d1ff8185b30f59c35313e60663d026eb8351d0dd9fd6f60eb279b301a"  
                amount 类型:string 最大长度:20 含义:未成交数量 示例:"999.1234"  
                icoAmount 类型:string 最大长度:20 含义:未成交数量 示例:"999.1234"  
                createdTime 类型:string 长度:20 含义:订单创建时间 示例:"2017-01-19T15:12:03Z"  
                modifiedTime 类型:string 长度:20 含义:订单最后修改时间 示例:"2017-01-19T15:12:03Z"  
        '''
        serializer = ICOAskOrderSerializer(data=request.data)
        if serializer.is_valid():
            ao = serializer.save()
            response_dict = {}
            response_dict['order'] = model_to_dict(ao, fields=['id','address','client','assetId','valueId','amount','icoAmount'])
            response_dict['order']['amount'] = str(response_dict['order']['amount'])
            response_dict['order']['icoAmount'] = str(response_dict['order']['icoAmount'])
            response_dict['order'].update({'createdTime':ao.createdTime,'modifiedTime':ao.modifiedTime})
            untran,txid = WT.generate_unsignature_transaction(ao.id)
            if not untran or not txid:
                return Response({'error':'not match'}, status=status.HTTP_400_BAD_REQUEST)
            cache.set(txid,untran)
            WT.update_agency_order_prevhash(ao,txid)
            response_dict['transaction'] = untran
            return Response(response_dict, status=status.HTTP_201_CREATED)
        else:
            if serializer.errors.has_key('non_field_errors'):
                errors = {'error':serializer.errors['non_field_errors'][0]}
                return Response(errors, status=status.HTTP_400_BAD_REQUEST)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class OTCAskOrderViewSet(viewsets.GenericViewSet):
    queryset = History.objects.all()
    serializer_class = OTCAskOrderSerializer
    def create(self, request):
        '''
        挂卖单 
        ---
        请求参数:
            
            assetId 类型:string 长度:64 含义:way为true时,为卖方资产ID;way为false时,为买方资产ID 示例:"602c79718b16e442de58778e148d0b1084e3b2dffd5de6b7b16cee7969282de7"  
            price 类型:string 最大长度:20 含义:挂单价格 示例:"1.05"  
            amount 类型:string 最大长度:20 含义:未成交数量 示例:"999.1234"  
            valueId 类型:string 长度:64 含义:way为true时，为买方资产ID;way为false时,为卖方资产ID 示例:"5fd33b8d1ff8185b30f59c35313e60663d026eb8351d0dd9fd6f60eb279b301a"  
            hexPubkey 类型:string 长度:130 含义:登录钱包时拿到的公钥 示例:"0483cdbc3f4d2213043c19d6bd041c08fbe0a3bacd43ef695500a1b33c609a9e8a180eee2ada65ddb65154863c57bac9ab1b89a61593235991d5fb6f627c0cadbd"

        响应参数:

            transaction 类型:string 最大长度:1024 含义:转账至合约地址的交易待签名部分 示例:"80000001c686a413df35c45620a33c44ba892ea4cfcc81f59573c96777a994e08bf6211e010002e72d286979ee6cb1b7e65dfddfb2e384100b8d148e7758de42e4168b71792c6020523d43170000003d8acd68cce2640a2bf00bfa06022fe98441380ce72d286979ee6cb1b7e65dfddfb2e384100b8d148e7758de42e4168b71792c60e0b68930cc000000138bb1207f869b6c08a6fbd911251fcbf8194aa9"  
            order 类型:字段对象 含义:新建的订单详情  
                status 类型:integer 含义:订单状态值 示例:-3  
                assetId 类型:string 长度:64 含义:资产ID 示例:"602c79718b16e442de58778e148d0b1084e3b2dffd5de6b7b16cee7969282de7"  
                price 类型:string 最大长度:20 含义:挂单价格 示例:"1.05"  
                contractAddress 类型:string 长度:34 含义:代理合约地址 示例:"AGZg5De65ECTaVcE9VSyRMi2Azv9ghexo8"  
                agent 类型:string 长度:66 含义:代理人压缩版公钥 示例:"0383cdbc3f4d2213043c19d6bd041c08fbe0a3bacd43ef695500a1b33c609a9e8a"  
                amount 类型:string 最大长度:20 含义:未成交数量 示例:"999.1234"  
                client 类型:string 长度:66 含义:请求参数address所对应的压缩版公钥 示例:"0383cdbc3f4d2213043c19d6bd041c08fbe0a3bacd43ef695500a1b33c609a9e8a"  
                modifiedTime 类型:string 长度:20 含义:订单最后修改时间 示例:"2017-01-19T15:12:03Z"  
                way 类型:boolean 含义:true表示卖单，false表示买单 示例:true  
                address 类型:string 长度:34 含义:小蚁地址 示例:"AHZDq78w1ERcDYVBWjU5owWcbFZKLvhg7X"  
                createdTime 类型:string 长度:20 含义:订单创建时间 示例:"2017-01-19T15:12:03Z"  
                valueId 类型:string 长度:64 含义:资产ID 示例:"5fd33b8d1ff8185b30f59c35313e60663d026eb8351d0dd9fd6f60eb279b301a"  
                id 类型:integer 含义:订单ID 示例:7  
        '''
        serializer = OTCAskOrderSerializer(data=request.data)
        if serializer.is_valid():
            ao = serializer.save()
            response_dict = {}
            response_dict['order'] = model_to_dict(ao, fields=['id','address','agent','client','assetId','valueId','amount','price','way','status'])
            response_dict['order']['price'] = str(response_dict['order']['price'])
            response_dict['order']['amount'] = str(response_dict['order']['amount'])
            response_dict['order'].update({'createdTime':ao.createdTime,'modifiedTime':ao.modifiedTime,'contractAddress':ao.contractAddress})
            untran,txid = WT.generate_unsignature_transaction(ao.id)
            WT.update_agency_order_prevhash(ao,txid)
            cache.set(txid, untran)
            response_dict['transaction'] = untran
            return Response(response_dict, status=status.HTTP_201_CREATED)
        else:
            if serializer.errors.has_key('non_field_errors'):
                errors = {'error':serializer.errors['non_field_errors'][0]}
                return Response(errors, status=status.HTTP_400_BAD_REQUEST)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class OTCBidOrderViewSet(viewsets.GenericViewSet):
    queryset = History.objects.all()
    serializer_class = OTCBidOrderSerializer
    def create(self, request):
        '''
        挂买单 
        ---
        请求参数:
            
            assetId 类型:string 长度:64 含义:way为true时,为卖方资产ID;way为false时,为买方资产ID 示例:"602c79718b16e442de58778e148d0b1084e3b2dffd5de6b7b16cee7969282de7"  
            valueId 类型:string 长度:64 含义:way为true时，为买方资产ID;way为false时,为卖方资产ID 示例:"5fd33b8d1ff8185b30f59c35313e60663d026eb8351d0dd9fd6f60eb279b301a"  
            price 类型:string 最大长度:20 含义:挂单价格 示例:"1.05"  
            amount 类型:string 最大长度:20 含义:未成交数量 示例:"999.1234"  
            hexPubkey 类型:string 长度:130 含义:登录钱包时拿到的公钥 示例:"0483cdbc3f4d2213043c19d6bd041c08fbe0a3bacd43ef695500a1b33c609a9e8a180eee2ada65ddb65154863c57bac9ab1b89a61593235991d5fb6f627c0cadbd"

        响应参数:

            transaction 类型:string 最大长度:1024 含义:转账至合约地址的交易待签名部分 示例:"80000001c686a413df35c45620a33c44ba892ea4cfcc81f59573c96777a994e08bf6211e010002e72d286979ee6cb1b7e65dfddfb2e384100b8d148e7758de42e4168b71792c6020523d43170000003d8acd68cce2640a2bf00bfa06022fe98441380ce72d286979ee6cb1b7e65dfddfb2e384100b8d148e7758de42e4168b71792c60e0b68930cc000000138bb1207f869b6c08a6fbd911251fcbf8194aa9"  
            order 类型:字段对象 含义:新建的订单详情  
                status 类型:integer 含义:订单状态值 示例:-3  
                assetId 类型:string 长度:64 含义:资产ID 示例:"602c79718b16e442de58778e148d0b1084e3b2dffd5de6b7b16cee7969282de7"  
                price 类型:string 最大长度:20 含义:挂单价格 示例:"1.05"  
                contractAddress 类型:string 长度:34 含义:代理合约地址 示例:"AGZg5De65ECTaVcE9VSyRMi2Azv9ghexo8"  
                agent 类型:string 长度:66 含义:代理人压缩版公钥 示例:"0383cdbc3f4d2213043c19d6bd041c08fbe0a3bacd43ef695500a1b33c609a9e8a"  
                amount 类型:string 最大长度:20 含义:未成交数量 示例:"999.1234"  
                client 类型:string 长度:66 含义:请求参数address所对应的压缩版公钥 示例:"0383cdbc3f4d2213043c19d6bd041c08fbe0a3bacd43ef695500a1b33c609a9e8a"  
                modifiedTime 类型:string 长度:20 含义:订单最后修改时间 示例:"2017-01-19T15:12:03Z"  
                way 类型:boolean 含义:true表示卖单，false表示买单 示例:true  
                address 类型:string 长度:34 含义:小蚁地址 示例:"AHZDq78w1ERcDYVBWjU5owWcbFZKLvhg7X"  
                createdTime 类型:string 长度:20 含义:订单创建时间 示例:"2017-01-19T15:12:03Z"  
                valueId 类型:string 长度:64 含义:资产ID 示例:"5fd33b8d1ff8185b30f59c35313e60663d026eb8351d0dd9fd6f60eb279b301a"  
                id 类型:integer 含义:订单ID 示例:7  
        '''
        serializer = OTCBidOrderSerializer(data=request.data)
        if serializer.is_valid():
            ao = serializer.save()
            response_dict = {}
            response_dict['order'] = model_to_dict(ao, fields=['id','address','agent','client','assetId','valueId','amount','price','way','status'])
            response_dict['order']['price'] = str(response_dict['order']['price'])
            response_dict['order']['amount'] = str(response_dict['order']['amount'])
            response_dict['order'].update({'createdTime':ao.createdTime,'modifiedTime':ao.modifiedTime,'contractAddress':ao.contractAddress})
            untran,txid = WT.generate_unsignature_transaction(ao.id)
            WT.update_agency_order_prevhash(ao,txid)
            cache.set(txid, untran)
            response_dict['transaction'] = untran
            return Response(response_dict, status=status.HTTP_201_CREATED)
        else:
            if serializer.errors.has_key('non_field_errors'):
                errors = {'error':serializer.errors['non_field_errors'][0]}
                return Response(errors, status=status.HTTP_400_BAD_REQUEST)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class FreeBidOrderViewSet(viewsets.GenericViewSet):
    queryset = History.objects.all()
    serializer_class = FreeBidOrderSerializer
    def create(self, request):
        '''
        买家吃单 
        ---
        请求参数:
            
            id 类型:integer 含义:订单ID 示例:7  
            hexPubkey 类型:string 长度:130 含义:登录钱包时拿到的公钥 示例:"0483cdbc3f4d2213043c19d6bd041c08fbe0a3bacd43ef695500a1b33c609a9e8a180eee2ada65ddb65154863c57bac9ab1b89a61593235991d5fb6f627c0cadbd"

        响应参数:

            transaction 类型:string 最大长度:1024 含义:转账至合约地址的交易待签名部分 示例:"80000001c686a413df35c45620a33c44ba892ea4cfcc81f59573c96777a994e08bf6211e010002e72d286979ee6cb1b7e65dfddfb2e384100b8d148e7758de42e4168b71792c6020523d43170000003d8acd68cce2640a2bf00bfa06022fe98441380ce72d286979ee6cb1b7e65dfddfb2e384100b8d148e7758de42e4168b71792c60e0b68930cc000000138bb1207f869b6c08a6fbd911251fcbf8194aa9"  
            order 类型:字段对象 含义:新建的订单详情  
                id 类型:integer 含义:订单ID 示例:7  
                address 类型:string 长度:34 含义:小蚁地址 示例:"AHZDq78w1ERcDYVBWjU5owWcbFZKLvhg7X"  
                agent 类型:string 长度:66 含义:代理人压缩版公钥 示例:"0383cdbc3f4d2213043c19d6bd041c08fbe0a3bacd43ef695500a1b33c609a9e8a"  
                client 类型:string 长度:66 含义:请求参数address所对应的压缩版公钥 示例:"0383cdbc3f4d2213043c19d6bd041c08fbe0a3bacd43ef695500a1b33c609a9e8a"  
                assetId 类型:string 长度:64 含义:资产ID 示例:"602c79718b16e442de58778e148d0b1084e3b2dffd5de6b7b16cee7969282de7"  
                valueId 类型:string 长度:64 含义:资产ID 示例:"5fd33b8d1ff8185b30f59c35313e60663d026eb8351d0dd9fd6f60eb279b301a"  
                amount 类型:string 最大长度:20 含义:未成交数量 示例:"999.1234"  
                price 类型:string 最大长度:20 含义:挂单价格 示例:"1.05"  
                way 类型:boolean 含义:true表示卖单，false表示买单 示例:true  
                createdTime 类型:string 长度:20 含义:订单创建时间 示例:"2017-01-19T15:12:03Z"  
                modifiedTime 类型:string 长度:20 含义:订单最后修改时间 示例:"2017-01-19T15:12:03Z"  
        '''
        serializer = FreeBidOrderSerializer(data=request.data)
        if serializer.is_valid():
            ao = serializer.save()
            response_dict = {}
            response_dict['order'] = model_to_dict(ao, fields=['id','address','agent','client','assetId','valueId','amount','price','way'])
            response_dict['order']['price'] = str(response_dict['order']['price'])
            response_dict['order']['amount'] = str(response_dict['order']['amount'])
            response_dict['order'].update({'createdTime':ao.createdTime,'modifiedTime':ao.modifiedTime})
            untran,txid = WT.get_transaction_for_otc(ao)
            cache.set(txid,untran)
            if not untran or not txid:
                return Response({'error':'not match'}, status=status.HTTP_400_BAD_REQUEST)
            WT.update_agency_order_prevhash(ao,txid)
            response_dict['transaction'] = untran
            return Response(response_dict, status=status.HTTP_201_CREATED)
        else:
            if serializer.errors.has_key('non_field_errors'):
                errors = {'error':serializer.errors['non_field_errors'][0]}
                return Response(errors, status=status.HTTP_400_BAD_REQUEST)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class FreeAskOrderViewSet(viewsets.GenericViewSet):
    queryset = History.objects.all()
    serializer_class = FreeAskOrderSerializer
    def create(self, request):
        '''
        卖家吃单 
        ---
        请求参数:
            
            id 类型:integer 含义:订单ID 示例:7  
            hexPubkey 类型:string 长度:130 含义:登录钱包时拿到的公钥 示例:"0483cdbc3f4d2213043c19d6bd041c08fbe0a3bacd43ef695500a1b33c609a9e8a180eee2ada65ddb65154863c57bac9ab1b89a61593235991d5fb6f627c0cadbd"

        响应参数:

            transaction 类型:string 最大长度:1024 含义:转账至合约地址的交易待签名部分 示例:"80000001c686a413df35c45620a33c44ba892ea4cfcc81f59573c96777a994e08bf6211e010002e72d286979ee6cb1b7e65dfddfb2e384100b8d148e7758de42e4168b71792c6020523d43170000003d8acd68cce2640a2bf00bfa06022fe98441380ce72d286979ee6cb1b7e65dfddfb2e384100b8d148e7758de42e4168b71792c60e0b68930cc000000138bb1207f869b6c08a6fbd911251fcbf8194aa9"  
            order 类型:字段对象 含义:新建的订单详情  
                id 类型:integer 含义:订单ID 示例:7  
                address 类型:string 长度:34 含义:小蚁地址 示例:"AHZDq78w1ERcDYVBWjU5owWcbFZKLvhg7X"  
                agent 类型:string 长度:66 含义:代理人压缩版公钥 示例:"0383cdbc3f4d2213043c19d6bd041c08fbe0a3bacd43ef695500a1b33c609a9e8a"  
                client 类型:string 长度:66 含义:请求参数address所对应的压缩版公钥 示例:"0383cdbc3f4d2213043c19d6bd041c08fbe0a3bacd43ef695500a1b33c609a9e8a"  
                assetId 类型:string 长度:64 含义:资产ID 示例:"602c79718b16e442de58778e148d0b1084e3b2dffd5de6b7b16cee7969282de7"  
                valueId 类型:string 长度:64 含义:资产ID 示例:"5fd33b8d1ff8185b30f59c35313e60663d026eb8351d0dd9fd6f60eb279b301a"  
                amount 类型:string 最大长度:20 含义:未成交数量 示例:"999.1234"  
                price 类型:string 最大长度:20 含义:挂单价格 示例:"1.05"  
                way 类型:boolean 含义:true表示卖单，false表示买单 示例:true  
                createdTime 类型:string 长度:20 含义:订单创建时间 示例:"2017-01-19T15:12:03Z"  
                modifiedTime 类型:string 长度:20 含义:订单最后修改时间 示例:"2017-01-19T15:12:03Z"  
        '''
        serializer = FreeAskOrderSerializer(data=request.data)
        if serializer.is_valid():
            ao = serializer.save()
            response_dict = {}
            response_dict['order'] = model_to_dict(ao, fields=['id','address','agent','client','assetId','valueId','amount','price','way'])
            response_dict['order']['price'] = str(response_dict['order']['price'])
            response_dict['order']['amount'] = str(response_dict['order']['amount'])
            response_dict['order'].update({'createdTime':ao.createdTime,'modifiedTime':ao.modifiedTime})
            untran,txid = WT.get_transaction_for_otc(ao)
            cache.set(txid,untran)
            if not untran or not txid:
                return Response({'error':'not match'}, status=status.HTTP_400_BAD_REQUEST)
            WT.update_agency_order_prevhash(ao,txid)
            response_dict['transaction'] = untran
            return Response(response_dict, status=status.HTTP_201_CREATED)
        else:
            if serializer.errors.has_key('non_field_errors'):
                errors = {'error':serializer.errors['non_field_errors'][0]}
                return Response(errors, status=status.HTTP_400_BAD_REQUEST)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#区块相关
class BlockCountViewSet(viewsets.ViewSet):
    def list(self, request, format=None):
        '''
        获取最新区块数
        '''
        response_dict = {'height':cache.get('height')}
        return Response(response_dict)

#转账历史
class TransferHistoryViewSet(viewsets.ViewSet):
    lookup_url_kwarg = 'address'
    def list(self, request, address):
        '''
        获取指定地址下的转账记录
        ---
        请求参数:
            
            address 类型:string 长度:34 含义:小蚁地址 示例:"AHZDq78w1ERcDYVBWjU5owWcbFZKLvhg7X"
            *active 类型：number 含义：当前页 默认值：1
            *length 类型：number 含义：每页数量 默认值：7

        响应参数:

            page_num 类型：number 含义：总页数
            item_num 类型：number 含义：总条数
            data 类型：数组
                dest 类型:string 长度:34 含义:接收方地址    示例:"AGZg5De65ECTaVcE9VSyRMi2Azv9ghexo8"  
                name 类型:string 最大长度:64 含义:资产名称 示例:"小蚁股"  
                amount 类型:string 最大长度:20 含义:转账数量 示例:"999.1234"  
                time 类型:string 长度:20 含义:转账时间 示例:"2017-01-19T15:12:03Z"  
                txid 类型:string 长度:64 含义:交易ID 示例:"6c06696109f81d82d99039acdf89db30c84db0538dd5fbf2db26c9ca9194a95e" 
                confirm 类型：boolean 含义：是否确认
        '''
        tz = pytz.timezone(TZ)
        try:
            active = int(self.request.query_params.get('active',"1"))
            length = int(self.request.query_params.get('length',"7"))
        except:
            return Response({'error':u'参数有误!'},status=status.HTTP_400_BAD_REQUEST)
        if active*length <= 0:
            return Response({'error':u'参数有误!'},status=status.HTTP_400_BAD_REQUEST)
        trs = WT.get_transfer(address)
        count = len(trs)
        r_dict = {'data':[]}
        r_dict['page_num'] = int(ceil(count/(length*1.0)))
        r_dict['item_num'] = count
        if count > (active-1)*length:
            for tr in trs[(active-1)*length:active*length]:
                response_dict = model_to_dict(tr, fields=['dest','amount','txid','confirm'])
                response_dict.update({
                                'name':WT.get_asset_name(tr.assetId),
                                'time':tr.createdTime.astimezone(tz).strftime('%Y-%m-%d %H:%M:%S')
                        })
                r_dict['data'].append(response_dict)
        return Response(r_dict)

#取回资产
class RedeemSignatureViewSet(viewsets.GenericViewSet):
    queryset = History.objects.all()
    serializer_class = RedeemSignatureSerializer
    def create(self, request):
        '''
        对取回签名
        ---
        请求参数：

            id          类型:integer    含义:订单ID     示例:7  
            signature   类型:string     长度:128        含义:使用私钥进行签名后的内容   示例:"1aa0767ef1ca4c1ee5cee6b68a7f0d95754b2f12332c2c0165e2f47532541b874ce24a18b6d0f03ee59fd6904935ac7cb16b859f0b48546afb92ba6a8d69161c"

        响应参数:
            
            result  类型:boolean 含义:签名结果,为true说明签名有效;false签名无效  示例:true  
            txid    类型:string 长度:64 含义:交易ID 示例:"6c06696109f81d82d99039acdf89db30c84db0538dd5fbf2db26c9ca9194a95e" 
        '''
        serializer = RedeemSignatureSerializer(data=request.data)
        if serializer.is_valid():
            response_dict = {'result':True,'txid':WT.get_redeem_txid(request.data['id'])}
            return Response(response_dict, status=status.HTTP_201_CREATED)
        else:
            if serializer.errors.has_key('non_field_errors'):
                errors = {'error':serializer.errors['non_field_errors'][0]}
                return Response(errors, status=status.HTTP_400_BAD_REQUEST)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class RedeemCreateViewSet(viewsets.GenericViewSet):
    queryset = History.objects.all()
    serializer_class = RedeemCreateSerializer
    def create(self, request):
        '''
        获取取回交易 
        ---
        请求参数：

            id          类型:integer    含义:订单ID     示例:7  
            nonce       类型:string     长度:8          含义:随机字段                   示例:"7b83c412"  
            address     类型:string     长度:34         含义:小蚁地址                   示例:"AHZDq78w1ERcDYVBWjU5owWcbFZKLvhg7X"
            signature   类型:string     长度:128        含义:使用私钥进行签名后的内容   示例:"1aa0767ef1ca4c1ee5cee6b68a7f0d95754b2f12332c2c0165e2f47532541b874ce24a18b6d0f03ee59fd6904935ac7cb16b859f0b48546afb92ba6a8d69161c"

        响应参数:
            
            id          类型:integer    含义:订单ID     示例:7  
            transaction 类型:string 最大长度:1024 含义:取回资产待签名部分 示例:"80000001c686a413df35c45620a33c44ba892ea4cfcc81f59573c96777a994e08bf6211e010002e72d286979ee6cb1b7e65dfddfb2e384100b8d148e7758de42e4168b71792c6020523d43170000003d8acd68cce2640a2bf00bfa06022fe98441380ce72d286979ee6cb1b7e65dfddfb2e384100b8d148e7758de42e4168b71792c60e0b68930cc000000138bb1207f869b6c08a6fbd911251fcbf8194aa9"  
        '''
        serializer = RedeemCreateSerializer(data=request.data)
        if serializer.is_valid():
            response_dict = {'transaction':cache.get(str(request.data['id'])+'_redeem'),'id':request.data['id']}
            return Response(response_dict, status=status.HTTP_201_CREATED)
        else:
            if serializer.errors.has_key('non_field_errors'):
                errors = {'error':serializer.errors['non_field_errors'][0]}
                return Response(errors, status=status.HTTP_400_BAD_REQUEST)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class RedeemListViewSet(viewsets.ViewSet):
    lookup_url_kwarg = 'address'
    def list(self, request, address, format=None):
        '''
        获取指定地址的交易记录
        ---
        请求参数:
            
            address 类型:string 长度:34 含义:小蚁地址 示例:"AHZDq78w1ERcDYVBWjU5owWcbFZKLvhg7X"
            *active 类型：number 含义：当前页 默认值：1
            *length 类型：number 含义：每页数量 默认值：7

        响应参数:

            page_num 类型：number 含义：总页数
            item_num 类型：number 含义：总条数
            data 类型：数组
                id 类型:integer 含义:订单ID 示例:7  
                name 类型:string 最大长度:64 含义:交易对 示例:"KAC\ANS"  
                assetId 类型:string 长度:64 含义:资产ID 示例:"602c79718b16e442de58778e148d0b1084e3b2dffd5de6b7b16cee7969282de7"  
                amount 类型:string 最大长度:20 含义:未成交数量 示例:"999.1234"  
                price 类型:string 最大长度:20 含义:平均成交价价格 示例:"1.05"  
                time 类型:string 含义:时间 示例:"2017-02-26 12:30:42"
                redeem 类型:boolean 含义:取回(True)或未取回(False)
                way 类型:boolean 含义:true表示卖单，false表示买单 示例:true  
        '''
        tz = pytz.timezone(TZ)
        try:
            active = int(self.request.query_params.get('active',"1"))
            length = int(self.request.query_params.get('length',"7"))
            option = self.request.query_params.get('option','otc')
        except:
            return Response({'error':u'参数有误!'},status=status.HTTP_400_BAD_REQUEST)
        if active*length <= 0:
            return Response({'error':u'参数有误!'},status=status.HTTP_400_BAD_REQUEST)
        his = WT.get_address_history(address, None, option)
        count = len(his)
        r_dict = {'data':[]}
        r_dict['page_num'] = int(ceil(count/(length*1.0)))
        r_dict['item_num'] = count
        if count > (active-1)*length:
            response_list = []
            for h in his[(active-1)*length:active*length]:
                r = model_to_dict(h, fields=['id','assetId','amount','price','redeem','way'])
                #r['name']  = Asset.objects.get(asset_id=r['assetid']).name
                if Option.SellerOTC.value == h.option:
                    r['name']  = WT.market_to_user(h.marketId)
                else:
                    r['name'] = h.marketId
                    r['price'] = D('1')/r['price']
                    if r['way']:
                        r['way'] = False
                    else:
                        r['way'] = True
                r['time'] = h.createdTime.astimezone(tz).strftime('%Y-%m-%d %H:%M:%S')
                #r['redeem'] = False
                if r['way']:
                    r['amount'] = r['amount']/r['price']
                r['amount'] = remove_zero(str(r['amount'])) + ' ' + r['name'][:3]
                r['price'] = remove_zero(str(r['price'].quantize(D('.00000001'),rounding=ROUND_DOWN))) + ' ' + r['name'][-3:]
                response_list.append(r)
            r_dict['data'].extend(response_list)
        return Response(r_dict)

class UIDViewSet(viewsets.GenericViewSet):
    queryset = UID.objects.all()
    serializer_class = UIDSerializer
    lookup_url_kwarg = 'address'
    def list(self, requests, address):
        '''
        获取指定地址的UID
        ---
        请求参数:
            
            address 类型:string 长度:34 含义:小蚁地址 示例:"AHZDq78w1ERcDYVBWjU5owWcbFZKLvhg7X"

        响应参数:

            uid     类型:string 长度:6  含义:用户的唯一编号
            address 类型:string 长度:34 含义:小蚁地址 示例:"AHZDq78w1ERcDYVBWjU5owWcbFZKLvhg7X"
        '''
        serializer = UIDSerializer(data={'address':address})
        if serializer.is_valid():
            su = serializer.save()
            response_dict = model_to_dict(su, fields=['uid','address'])
            return Response(response_dict)
        else:
            if serializer.errors.has_key('non_field_errors'):
                errors = {'error':serializer.errors['non_field_errors'][0]}
                return Response(errors, status=status.HTTP_400_BAD_REQUEST)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class TransferViewSet(viewsets.GenericViewSet):
    queryset = Transfer.objects.all()
    serializer_class = TransferSerializer
    def create(self, request):
        '''
        转账
        ---
        请求参数：

            dest    类型:string 长度:34 含义:接收地址 示例:"AGZg5De65ECTaVcE9VSyRMi2Azv9ghexo8"  
            source  类型:string 长度:34 含义:转出地址 示例:"AHZDq78w1ERcDYVBWjU5owWcbFZKLvhg7X"  
            amount  类型:string 最大长度:20 含义:转出数量 示例:"999.1234"  
            assetId 类型:string 长度:64 含义:转出资产ID 示例:"602c79718b16e442de58778e148d0b1084e3b2dffd5de6b7b16cee7969282de7"  
            hexPubkey 类型:string 长度:130 含义:登录钱包时拿到的公钥 示例:"0483cdbc3f4d2213043c19d6bd041c08fbe0a3bacd43ef695500a1b33c609a9e8a180eee2ada65ddb65154863c57bac9ab1b89a61593235991d5fb6f627c0cadbd"

        响应参数:
            
            id          类型:integer                    含义:订单ID                     示例:9  
            nonce       类型:string     长度:8          含义:随机字段                   示例:"7b83c412"  
            transaction 类型:string 最大长度:1024 含义:转账交易待签名部分 示例:"80000001c686a413df35c45620a33c44ba892ea4cfcc81f59573c96777a994e08bf6211e010002e72d286979ee6cb1b7e65dfddfb2e384100b8d148e7758de42e4168b71792c6020523d43170000003d8acd68cce2640a2bf00bfa06022fe98441380ce72d286979ee6cb1b7e65dfddfb2e384100b8d148e7758de42e4168b71792c60e0b68930cc000000138bb1207f869b6c08a6fbd911251fcbf8194aa9"  
        '''
        serializer = TransferSerializer(data=request.data)
        if serializer.is_valid():
            tr = serializer.save()
            response_dict = model_to_dict(tr, fields=['id'])
            response_dict['transaction'] = cache.get(str(tr.id)+'_transfer')
            response_dict.update({'nonce':'a1b2c3e4'})
            response_dict['id'] = response_dict['id']*(-1)
            return Response(response_dict, status=status.HTTP_201_CREATED)
        else:
            if serializer.errors.has_key('non_field_errors'):
                errors = {'error':serializer.errors['non_field_errors'][0]}
                return Response(errors, status=status.HTTP_400_BAD_REQUEST)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class OrderCancelViewSet(viewsets.GenericViewSet):
    queryset = AgencyOrder.objects.all()
    serializer_class = OrderCancelSerializer
    def create(self, request):
        '''
        取消订单
        ---
        请求参数：

            id          类型:integer                    含义:订单ID                     示例:9 
            nonce       类型:string     长度:8          含义:随机字段                   示例:"7b83c412"  
            signature   类型:string     长度:128        含义:使用私钥进行签名后的内容   示例:"1aa0767ef1ca4c1ee5cee6b68a7f0d95754b2f12332c2c0165e2f47532541b874ce24a18b6d0f03ee59fd6904935ac7cb16b859f0b48546afb92ba6a8d69161c"

        响应参数:
            
            id          类型:integer                    含义:订单ID                     示例:9 
            nonce       类型:string     长度:8          含义:随机字段                   示例:"7b83c412"  
            transaction 类型:string 最大长度:1024 含义:转账至合约地址的交易待签名部分 示例:"80000001c686a413df35c45620a33c44ba892ea4cfcc81f59573c96777a994e08bf6211e010002e72d286979ee6cb1b7e65dfddfb2e384100b8d148e7758de42e4168b71792c6020523d43170000003d8acd68cce2640a2bf00bfa06022fe98441380ce72d286979ee6cb1b7e65dfddfb2e384100b8d148e7758de42e4168b71792c60e0b68930cc000000138bb1207f869b6c08a6fbd911251fcbf8194aa9"  
        '''
        serializer = OrderCancelSerializer(data=request.data)
        if serializer.is_valid():
            response_dict = {}
            order_id = serializer.data['id']
            nonce = serializer.data['nonce']
            response_dict['id'] = order_id
            response_dict['nonce'] = nonce
            try:
                untran,txid = WT.generate_unsignature_transaction_when_know_prevhash(order_id)
            except AssertionError:
                return Response({'error':'poor balances of the agency contract address'},status=status.HTTP_400_BAD_REQUEST)
            response_dict['transaction'] = untran
            cache.set(str(order_id)+'_cancel', untran)
            ao = WT.get_agency_order(order_id)
            ao.redeem_txid = txid
            ao.save()
            return Response(response_dict, status=status.HTTP_201_CREATED)
        else:
            if serializer.errors.has_key('non_field_errors'):
                errors = {'error':serializer.errors['non_field_errors'][0]}
                return Response(errors, status=status.HTTP_400_BAD_REQUEST)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class SignViewSet(viewsets.GenericViewSet):
    queryset = AgencyOrder.objects.all()
    serializer_class = SignSerializer
    @transaction.atomic
    def create(self, request):
        '''
        对订单签名
        ---
        请求参数：

            nonce       类型:string     长度:8          含义:随机字段                   示例:"7b83c412"  
            id          类型:integer                    含义:订单ID                     示例:9 
            signature   类型:string     长度:128        含义:使用私钥进行签名后的内容   示例:"1aa0767ef1ca4c1ee5cee6b68a7f0d95754b2f12332c2c0165e2f47532541b874ce24a18b6d0f03ee59fd6904935ac7cb16b859f0b48546afb92ba6a8d69161c"

        响应参数:
            
            result  类型:boolean 含义:签名结果,为true说明签名有效;false签名无效  示例:true  
            txid    类型:string 长度:64 含义:交易ID 示例:"6c06696109f81d82d99039acdf89db30c84db0538dd5fbf2db26c9ca9194a95e" 
        '''
        serializer = SignSerializer(data=request.data)
        if serializer.is_valid():
            if 0 > serializer.data['id']:
                tr = WT.get_transfer_by_id((-1)*serializer.data['id'])
                response_dict = {'result':True,'txid':tr.txid}
            else:
                ao = WT.get_agency_order(serializer.data['id'])
                response_dict = {'result':True,'txid':ao.prevHash}
                if MatchStatus.Cancelled.value == ao.status:
                    response_dict['txid'] = ao.redeemTxid
            return Response(response_dict, status=status.HTTP_201_CREATED)
        else:
            if serializer.errors.has_key('non_field_errors'):
                errors = {'error':serializer.errors['non_field_errors'][0]}
                return Response(errors, status=status.HTTP_400_BAD_REQUEST)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class OTCSignViewSet(viewsets.GenericViewSet):
    queryset = AgencyOrder.objects.all()
    serializer_class = OTCSignSerializer
    @transaction.atomic
    def create(self, request):
        '''
        对OTC订单签名
        ---
        请求参数：

            id          类型:integer                    含义:订单ID                     示例:9 
            signature   类型:string     长度:128        含义:使用私钥进行签名后的内容   示例:"1aa0767ef1ca4c1ee5cee6b68a7f0d95754b2f12332c2c0165e2f47532541b874ce24a18b6d0f03ee59fd6904935ac7cb16b859f0b48546afb92ba6a8d69161c"

        响应参数:
            
            result  类型:boolean 含义:签名结果,为true说明签名有效;false签名无效  示例:true  
            txid    类型:string 长度:64 含义:交易ID 示例:"6c06696109f81d82d99039acdf89db30c84db0538dd5fbf2db26c9ca9194a95e" 
        '''
        serializer = OTCSignSerializer(data=request.data)
        if serializer.is_valid():
            ao = WT.get_agency_order(serializer.data['id'])
            response_dict = {'result':True,'txid':ao.prevHash}
            return Response(response_dict, status=status.HTTP_201_CREATED)
        else:
            if serializer.errors.has_key('non_field_errors'):
                errors = {'error':serializer.errors['non_field_errors'][0]}
                return Response(errors, status=status.HTTP_400_BAD_REQUEST)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class NonceViewSet(viewsets.ViewSet):
    def list(self, request):
        '''
        生成随机字段        
        ---
        请求参数：

            (无)

        响应参数:

            nonce       类型:string     长度:8          含义:随机字段                   示例:"7b83c412"  
        '''
        return Response({'nonce':os.urandom(4).encode('hex')})

class OrderListViewSet(viewsets.ViewSet):
    lookup_url_kwarg = 'address'
    def list(self, request, address, format=None):
        '''
        获取指定地址下的订单
        ---
        请求参数:
            
            address 类型:string 长度:34 含义:小蚁地址 示例:"AHZDq78w1ERcDYVBWjU5owWcbFZKLvhg7X"
            *marketId       类型:string     长度:6      含义:交易市场代号   示例:"anscny"

        响应参数:

            asks 类型:数组 含义:卖单列表  
                id 类型:integer 含义:订单ID 示例:7
                name 类型:string 最大长度:64 含义:资产名称 示例:"小蚁股"  
                status 类型:integer 含义:订单状态值 示例:-3  
                assetId 类型:string 长度:64 含义:资产ID 示例:"602c79718b16e442de58778e148d0b1084e3b2dffd5de6b7b16cee7969282de7"  
                price 类型:string 最大长度:20 含义:挂单价格 示例:"1.05"  
                contractAddress 类型:string 长度:34 含义:代理合约地址 示例:"AGZg5De65ECTaVcE9VSyRMi2Azv9ghexo8"  
                agent 类型:string 长度:66 含义:代理人压缩版公钥 示例:"0383cdbc3f4d2213043c19d6bd041c08fbe0a3bacd43ef695500a1b33c609a9e8a"  
                amount 类型:string 最大长度:20 含义:未成交数量 示例:"999.1234"  
                client 类型:string 长度:66 含义:请求参数address所对应的压缩版公钥 示例:"0383cdbc3f4d2213043c19d6bd041c08fbe0a3bacd43ef695500a1b33c609a9e8a"  
                modifiedTime 类型:string 长度:20 含义:订单最后修改时间 示例:"2017-01-19T15:12:03Z"  
                way 类型:boolean 含义:true表示卖单，false表示买单 示例:true  
                address 类型:string 长度:34 含义:小蚁地址 示例:"AHZDq78w1ERcDYVBWjU5owWcbFZKLvhg7X"  
                createdTime 类型:string 长度:20 含义:订单创建时间 示例:"2017-01-19T15:12:03Z"  
                valueId 类型:string 长度:64 含义:资产ID 示例:"5fd33b8d1ff8185b30f59c35313e60663d026eb8351d0dd9fd6f60eb279b301a"  
            bids 类型:数组 含义:买单列表  
                (同asks)
        '''
        marketId = self.request.query_params.get('marketId',"ALL")
        aos = WT.get_waiting_for_match_agency_order_of_otc(address,marketId)
        aos_dict = {'asks':[],'bids':[]}
        for ao in aos:
            response_dict = model_to_dict(ao, fields=['id','address','agent','client','assetId','valueId','amount','price','way','status'])
            response_dict.update({
                            'name':WT.get_asset_name(ao.assetId),
                            'createdTime':ao.createdTime,
                            'modifiedTime':ao.modifiedTime,
                            'contractAddress':ao.contractAddress
                    })
            response_dict['amount'] = remove_zero(str(response_dict['amount']))
            response_dict['price'] = remove_zero(str(response_dict['price']))
            if response_dict['way']:
                aos_dict['asks'].append(response_dict)
            else:
                response_dict['amount'] = remove_zero(str((D(response_dict['amount'])/D(response_dict['price'])).quantize(D('.0001'),rounding=ROUND_DOWN)))
                aos_dict['bids'].append(response_dict)
        return JsonResponse(aos_dict)

class OrderBookViewSet(viewsets.ViewSet):
    '''
    订单相关API
    '''
    lookup_url_kwarg = 'marketId'
    #serializer_class = MarketSerializer
    def retrieve(self, request, marketId, format=None):
        '''
        获取指定市场的挂单
        ---
        请求参数:
            
            marketId       类型:string     长度:6      含义:交易市场代号   示例:"anscny"
            *active 类型：number 含义：当前页 默认值：1
            *length 类型：number 含义：每页数量 默认值：20

        响应参数:

            page_num 类型：number 含义：总页数
            item_num 类型：number 含义：总条数
            marketId       类型:string     长度:6      含义:交易市场代号   示例:"anscny"  
            assetId         类型:string     长度:64     含义:资产ID         示例:"602c79718b16e442de58778e148d0b1084e3b2dffd5de6b7b16cee7969282de7"  
            valueId    类型:string     长度:64     含义:资产ID         示例:"5fd33b8d1ff8185b30f59c35313e60663d026eb8351d0dd9fd6f60eb279b301a"  
            data 类型：数组
                asks            类型:数组       含义:卖单列表  
                    id      类型:integer    含义:订单ID     示例:7  
                    price   类型:string     最大长度:20     含义:挂单价格   示例:"1.05"  
                    amount  类型:string     最大长度:20     含义:未成交数量 示例:"999.1234"  
                bids            类型:数组       含义:买单列表  
                    (同asks)
        '''
        try:
            active = int(self.request.query_params.get('active',"1"))
            length = int(self.request.query_params.get('length',"7"))
        except:
            return Response({'error':u'参数有误!'},status=status.HTTP_400_BAD_REQUEST)
        if active*length <= 0:
            return Response({'error':u'参数有误!'},status=status.HTTP_400_BAD_REQUEST)
        limit = 100
        #verify marketId
        if not WT.market_exist(marketId):
            raise serializers.ValidationError(u'无效市场')
        current_time = int(time.time())
        market_datas = cache.get(marketId)
        asset,valueAsset = map(WT.get_asset_by_market_sign,[marketId[0:3],marketId[3:]])
        if (not market_datas) or (current_time - market_datas['time'] > 0.5):#0.5s缓存
            #sellers = MatchOrder.objects.filter(Q(marketId=marketId)&Q(status=MatchStatus.Normal.value)&Q(way=True)).order_by('price')[0:limit]
            #buyers = MatchOrder.objects.filter(Q(marketId=marketId)&Q(status=MatchStatus.Normal.value)&Q(way=False)).order_by('-price')[0:limit]
            sellers = WT.get_agency_order_seller(Option.SellerOTC.value,asset.assetId,valueAsset.assetId,MatchStatus.WaitingForMatch.value)
            buyers = WT.get_agency_order_buyer(Option.SellerOTC.value,asset.assetId,valueAsset.assetId,MatchStatus.WaitingForMatch.value)
            response_dict = {'asks':[],'bids':[]}
            for s in sellers:
                current_s = {}
                current_s = model_to_dict(s, fields=['id','price','amount'])
                current_s['price'] = remove_zero(str(current_s['price']))
                current_s['amount'] = remove_zero(str(current_s['amount']))
                response_dict['asks'].append(current_s)
            for b in buyers:
                current_b = {}
                current_b = model_to_dict(b, fields=['id','price','amount'])
                current_b['price'] = remove_zero(str(current_b['price']))
                current_b['amount'] = remove_zero(str((b.amount/b.price).quantize(D('.00000001'),rounding=ROUND_DOWN)))
                response_dict['bids'].append(current_b)
            response_dict['bids'].reverse()
            response_dict['marketId'] = marketId
            response_dict['assetId'] = asset.assetId
            response_dict['valueId'] = valueAsset.assetId
            cache.set(marketId,{'time':current_time,'market':response_dict},timeout=2)
        else:
            response_dict = market_datas['market']
        countAsk = len(response_dict['asks'])
        countBid = len(response_dict['bids'])
        r_dict = {'data':{'asks':[],'bids':[]}}
        r_dict['page_num_asks'] = int(ceil(countAsk/(length*1.0)))
        r_dict['page_num_bids'] = int(ceil(countBid/(length*1.0)))
        r_dict['item_num_asks'] = countAsk
        r_dict['item_num_bids'] = countBid
        r_dict['marketId'] = marketId
        r_dict['assetId'] = asset.assetId
        r_dict['valueId'] = valueAsset.assetId
        if countAsk > (active-1)*length:
            response_list = []
            for a in response_dict['asks'][(active-1)*length:active*length]:
                response_list.append(a)
            r_dict['data']['asks'].extend(response_list)
        if countBid > (active-1)*length:
            response_list = []
            for b in response_dict['bids'][(active-1)*length:active*length]:
                response_list.append(b)
            r_dict['data']['bids'].extend(response_list)
        return Response(r_dict)

class MarketViewSet(viewsets.ReadOnlyModelViewSet):
    '''
    市场相关API 
    '''
    lookup_url_kwarg = 'marketId'
    queryset = Market.objects.all()
    serializer_class = MarketSerializer
    def list(self, request):
        '''
        获取所有市场详情
        '''
        queryset = Market.objects.all()
        serializer = MarketSerializer(queryset, many=True)
        return Response(serializer.data)
    def retrieve(self, request, marketId, format=None):
        '''
        获取单一市场详情
        '''
        if not WT.market_exist(marketId):
            raise serializers.ValidationError(u'无效市场')
        current_time = time.time()
        market_datas = cache.get(marketId+'_datas')
        if (not market_datas) or (current_time - market_datas['time'] > 0.5):#0.5s缓存
            mk = WT.get_market(marketId)
            recent = WT.get_market_last_24_volumn(marketId)
            market_datas = {
                    'time':current_time,
                    'marketId':marketId,
                    'name':mk.name,
                    'price':remove_zero(str(mk.price)),
                    'volumnOfLast24Hours':remove_zero(str(recent[0])),
                    'rate':recent[1]
                    }
            cache.set(marketId+'_datas',market_datas, timeout=2)
        del market_datas['time']
        return Response(market_datas)

class BalanceViewSet(viewsets.ViewSet):
    '''
    获取指定小蚁地址的资产详情
    '''
    lookup_url_kwarg = 'address'
    def retrieve(self, request, address, format=None):
        '''
        获取指定小蚁地址的资产详情
        ---
        请求参数:
            
            address 类型:string 长度:34 含义:小蚁地址 示例:"AHZDq78w1ERcDYVBWjU5owWcbFZKLvhg7X"

        响应参数:

            address 类型:string 长度:34 含义:小蚁地址 示例:"AHZDq78w1ERcDYVBWjU5owWcbFZKLvhg7X"  
            balances 类型:数组 含义:用户资产详情列表  
                name 类型:string 最大长度:64 含义:资产名称 示例:"小蚁股"  
                frozen 类型:string 最大长度:20 含义:资产冻结量 示例:"100"  
                divisible 类型:boolean 含义:是否可分割,可分割时(True)，进行转账和交易时，最多可取4位小数；不可分割时(False),进行转账和交易时，只能取整数 示例:True  
                valid 类型:string 最大长度:20 含义:资产可用量 示例:"1000.1234"  
                assetId 类型:string 长度:64 含义:资产ID 示例:"602c79718b16e442de58778e148d0b1084e3b2dffd5de6b7b16cee7969282de7"  
                total 类型:string 最大长度:20 含义:资产总量，可用量和冻结量的总和 示例:"10100.1234"  
                assetType 类型:string 含义:资产类型:AntShare;AntCoin;Token;Share  
                marketSign 类型:string 含义:代号
        '''
        #Step 1:获取地址下的所有资产
        aa = AntAddress(address)
        balances = [{'assetId':a,'total':D(v),'frozen':D('0'),'valid':D(v)} for a,v in aa.balances.items()]
        balances_list = [b['assetId'] for b  in balances]
        #Step 2:过滤功能;小蚁原生货币，必须显示
        MUST_SUPPORT = [ANC_ASSET, ANS_ASSET, RMB_ASSET] if NEED_RMB else [ANC_ASSET, ANS_ASSET]
        vas = WT.get_valid_assets()
        for v in vas:
            if v not in MUST_SUPPORT:
                va = v.assetId
                if va not in MUST_SUPPORT:
                    MUST_SUPPORT.insert(0,va)
        for i in MUST_SUPPORT:
            a = WT.get_asset(i)
            if i not in balances_list:
                balances.insert(0,{'assetId':i,'name':a.name,'assetType':a.assetType,'total':D('0'),'frozen':D('0'),'valid':D('0'),'divisible':a.divisible,'marketSign':a.marketSign})
            else:
                me = filter(lambda x:x['assetId'] == i,balances)[0]
                me['name'] = a.name
                me['assetType'] = a.assetType 
                me['marketSign'] = a.marketSign
                balances = filter(lambda x:x['assetId'] != i,balances)
                balances.insert(0,me)
        else:
            balances = balances[:len(MUST_SUPPORT)]
        #计算冻结量
        for k in balances:
            assetId = k['assetId']
            uncons = WT.get_unconfirm_agency_order_of_address(address,assetId)
            #挂单还未确认
            if uncons:
                fc = sum([a.amount for a in uncons])
                k['frozen'] += fc
                k['valid'] -= fc
                #print 'unconfirm amount:%s' % fc
            #挂单还未成交
            atos_asks = WT.get_frozen_ask_agency_order(address,assetId,MatchStatus.WaitingForMatch.value)
            atos_bids = WT.get_frozen_bid_agency_order(address,assetId,MatchStatus.WaitingForMatch.value)
            atos = atos_asks + atos_bids
            if atos:
                fc = sum([a.amount for a in atos])
                k['frozen'] += fc
                #print 'waiting for match amount:%s' % fc
            #广播还未确认的 转账 需要冻结
            trs = WT.get_broadcast_uncomfirm_transfer(address,assetId)
            if trs:
                fc = sum([tr.amount for tr in trs])
                k['frozen'] = k['frozen'] + fc
                k['valid'] = k['valid'] - fc
            #成交还未取回
            reds = WT.get_unredeem_history_of_address_and_asset(address,assetId)
            if reds:
                fc = sum(r.amount for r in reds)
                k['frozen'] += fc
                k['total'] = k['valid'] + k['frozen']
            k['total'] = k['valid'] + k['frozen']
            k['divisible'] = WT.get_asset_divisible(assetId)
        del aa
        #额外处理
        for b in balances:
            b['total'] = remove_zero(str(b['total']))
            b['frozen'] = remove_zero(str(b['frozen']))
            b['valid'] = remove_zero(str(b['valid']))
            if ANC_ASSET == b['assetId']:
                b.update(WT.get_claims(address))
        return JsonResponse({'address':address, 'balances':balances})

class HistoryListViewSet(viewsets.ViewSet):
    lookup_url_kwarg = 'marketId'
    def list(self, request, marketId, format=None):
        '''
        获取指定市场的交易记录
        ---
        请求参数:
            
            marketId 类型:string 长度:6 含义:市场ID 示例:"anscny"
            *address 类型:string  长度:33-34 含义：地址
            *active 类型：number 含义：当前页 默认值：1
            *length 类型：number 含义：每页数量 默认值：7

        响应参数:

            page_num 类型：number 含义：总页数
            item_num 类型：number 含义：总条数
            data 类型：数组
                id 类型:integer 含义:订单ID 示例:7  
                name 类型:string 最大长度:64 含义:交易对 示例:"KAC\ANS"  
                assetId 类型:string 长度:64 含义:资产ID 示例:"602c79718b16e442de58778e148d0b1084e3b2dffd5de6b7b16cee7969282de7"  
                amount 类型:string 最大长度:20 含义:未成交数量 示例:"999.1234"  
                price 类型:string 最大长度:20 含义:平均成交价价格 示例:"1.05"  
                time 类型:string 含义:时间 示例:"2017-02-26 12:30:42"
                redeem 类型:boolean 含义:取回(True)或未取回(False)
                way 类型:boolean 含义:true表示卖单，false表示买单 示例:true  
        '''
        tz = pytz.timezone(TZ)
        try:
            active = int(self.request.query_params.get('active',"1"))
            length = int(self.request.query_params.get('length',"7"))
            address = self.request.query_params.get('address','')
        except:
            return Response({'error':u'参数有误!'},status=status.HTTP_400_BAD_REQUEST)
        if active*length <= 0:
            return Response({'error':u'参数有误!'},status=status.HTTP_400_BAD_REQUEST)
        if not WT.market_exist(marketId):
            return Response({'error':u'无效市场!'},status=status.HTTP_400_BAD_REQUEST)
        if address:
            his = WT.get_address_history(address,marketId,'otc')
        else:
            his = WT.get_market_history(marketId)
        count = len(his)
        r_dict = {'data':[]}
        r_dict['page_num'] = int(ceil(count/(length*1.0)))
        r_dict['item_num'] = count
        if count > (active-1)*length:
            response_list = []
            for h in his[(active-1)*length:active*length]:
                r = model_to_dict(h, fields=['id','assetId','amount','price','redeem','way'])
                #r['name']  = Asset.objects.get(asset_id=r['assetid']).name
                if Option.SellerOTC.value == h.option:
                    r['name']  = WT.market_to_user(h.marketId)
                else:
                    r['name'] = h.marketId
                    r['price'] = D('1')/r['price']
                    if r['way']:
                        r['way'] = False
                    else:
                        r['way'] = True
                r['time'] = h.createdTime.astimezone(tz).strftime('%Y-%m-%d %H:%M:%S')
                #r['redeem'] = False
                if r['way']:
                    r['amount'] = r['amount']/r['price']
                r['amount'] = remove_zero(str(r['amount'])) + ' ' + r['name'][:3]
                r['price'] = remove_zero(str(r['price'].quantize(D('.00000001'),rounding=ROUND_DOWN))) + ' ' + r['name'][-3:]
                response_list.append(r)
            r_dict['data'].extend(response_list)
        return Response(r_dict)

# bank bind
class BankBindViewSet(viewsets.GenericViewSet):
    queryset = Bank.objects.all()
    serializer_class = BankSerializer
    def create(self, request):
        '''
        绑定用户冲值卡 
        ---
        请求参数:
            sign 类型:string 长度:100 含义:签名 示例:"0"
            random 类型:string 长度:100 含义:随机数 示例:"0"
            publicKey 类型:string 长度:100 含义:公钥 示例:"0"

            type 类型:int 长度:10 含义:0  支付宝 1 微信 2 银行卡 示例:"0"
            uid  类型:string 长度:10 含义:用户id 示例:"0"
            name 类型:string 长度:10 含义:真实姓名 示例:"0"
            nickName 类型:string 长度:10 含义:昵称 示例:"0"
            account 类型:string 长度:10 含义:账号 示例:"0"
            blankName 类型:string 长度:10 含义:银行名称 示例:"中国银行"
            AccountWithBank 类型:string 长度:10 含义:开户地址 示例:"1"

        响应参数:
  
        '''
        logger.info(request.data)
        serializer = BankSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST) 
        
class BankQueryViewSet(viewsets.GenericViewSet):
    queryset = Bank.objects.all()
    serializer_class = BankSerializer
    def create(self,request):
        '''
        查询用户绑定信息
        ---
        请求参数
            sign 类型:string 长度:100 含义:签名 示例:"0"
            random 类型:string 长度:100 含义:随机数 示例:"0"
            publicKey 类型:string 长度:100 含义:公钥 示例:"0"
            type 类型:int 长度:10 含义:0  支付宝 1 微信 2 银行卡 示例:"0"
            uid  类型:string 长度:10 含义:用户id 示例:"0"

        响应参数

        '''
        logger.info(request.data['uid'])
        #logger.info(r)
        if  'type' in request.data and  'uid' in request.data:
            banks = Bank.objects.filter(type=request.data['type'],uid=request.data['uid'])
            serializer = BankSerializer(banks, many=True)
            return Response(serializer.data)
        if  'uid' in request.data:
            banks = Bank.objects.filter(uid=request.data['uid'])
            serializer = BankSerializer(banks, many=True)
            return Response(serializer.data)
            
  
    