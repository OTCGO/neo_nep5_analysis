#!/usr/bin/env python
# coding: utf8
import os
import sys

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "OTCGO.settings")

    import django
    django.setup()
    from wallet.models import Asset,MatchOrder,Market
    from OTCGO.Enums import MatchStatus
    import requests
    from decimal import Decimal as D
    from bs4 import BeautifulSoup as BSP
    from OTCGO.settings import TESTNET


    url = 'http://testnet.antcha.in/tokens' if TESTNET else 'http://antcha.in/tokens'
    r = requests.get(url)
    soup = BSP(r.content, 'lxml')
    trs = [tr for tr in soup.tbody.children]
    trs = [trs[i] for i in range(len(trs)) if i%2==1]
    d = [[unicode(tr.div.a.string).strip(),
        unicode(tr.td.next_sibling.next_sibling.string).strip(),
        unicode(tr.td.next_sibling.next_sibling.next_sibling.next_sibling.string).strip()] for tr in trs]
    for i in d:
        a = Asset.objects.filter(assetId=i[0])
        if not len(a):
            at = Asset(assetId=i[0],name=i[1])
            if '602c79718b16e442de58778e148d0b1084e3b2dffd5de6b7b16cee7969282de7' ==  at.assetId:
                at.marketSign = 'anc'
                at.assetType = 'AntCoin'
                at.save()
            if 'c56f33fc6ecfcd0c225c4ab356fee59390af8560be0e930faebe74a6daff7c9b' == at.assetId:
                at.marketSign = 'ans'
                at.divisible = False
                at.assetType = 'AntShare'
                at.save()
            #testnet tec
            if '0c092117b4ba47b81001712425e6e7f760a637695eaf23741ba335925b195ecd' == at.assetId:
                at.marketSign = 'tec'
                at.assetType = 'Token'
                at.save()
            #mainnet tec
            if '025d82f7b00a9ff1cfe709abe3c4741a105d067178e645bc3ebad9bc79af47d4' == at.assetId:
                at.marketSign = 'tec'
                at.assetType = 'Token'
                at.save()
            #testnet kac
            if 'b426d50907c2b1ff91a8d5c8f1da3bea77e79ada05885719130d99cabae697c0' == at.assetId:
                at.marketSign = 'kac'
                at.assetType = 'Token'
                at.save()
            #mainnet kac
            if '07de511668e6ecc90973d713451c831d625eca229242d34debf16afa12efc1c1' == at.assetId:
                at.marketSign = 'kac'
                at.assetType = 'Token'
                at.save()
            #mainnet lzc
            if '0ab0032ade19975183c4ac90854f1f3c3fc535199831e7d8f018dabb2f35081f' == at.assetId:
                at.marketSign = 'lzj'
                at.assetType = 'Token'
                at.divisible = False
                at.save()
            #testnet lzc
            if 'beb6f821b9141269f06ee5205531a13777be727ec005c53334f2ea82585426fb' == at.assetId:
                at.marketSign = 'lzj'
                at.assetType = 'Token'
                at.divisible = False
                at.save()
            #mainnet lzs
            if '1b504c5fb070aaca3d57c42b5297d811fe6f5a0c5d4cd4496261417cf99013a5' == at.assetId:
                at.marketSign = 'lzg'
                at.assetType = 'Share'
                at.divisible = False
                at.save()
            #testnet lzs
            if 'ab84419d6a391b50400dc6f5ab63528ea8ecb32b81addfb4c7f8afe44be6c1ac' == at.assetId:
                at.marketSign = 'lzg'
                at.assetType = 'Share'
                at.divisible = False
                at.save()
            #testnet cny
            if '2dbd5d6be093f6bdd7e59d1faedfd2656422aaf749719903e8dab412b4349e81' == at.assetId:
                at.marketSign = 'cny'
                at.assetType = 'Token'
                at.save()
            #testnet sys
            if 'bbb7a08e52a5242079487fead6753dd038d41197e04e342b6f7b7358936551ea' == at.assetId:
                at.marketSign = 'sys'
                at.assetType = 'Share'
                at.divisible = False
                at.save()
            #mainnet sys
            if '30e9636bc249f288139651d60f67c110c3ca4c3dd30ddfa3cbcec7bb13f14fd4' == at.assetId:
                at.marketSign = 'sys'
                at.assetType = 'Share'
                at.divisible = False
                at.save()
            #testnet syc
            if 'e13440dccae716e16fc01adb3c96169d2d08d16581cad0ced0b4e193c472eac1' == at.assetId:
                at.marketSign = 'syc'
                at.assetType = 'Token'
                at.save()
            #mainnet syc
            if 'a52e3e99b6c2dd2312a94c635c050b4c2bc2485fcb924eecb615852bd534a63f' == at.assetId:
                at.marketSign = 'syc'
                at.assetType = 'Token'
                at.save()
    del soup
    del d
    

    wfs = MatchOrder.objects.filter(status = MatchStatus.WaitingForSignature.value)
    if not wfs: 
        waiting_for_signature_match_order = MatchOrder()
        waiting_for_signature_match_order.status = MatchStatus.WaitingForSignature.value
        waiting_for_signature_match_order.save()
    wfm = MatchOrder.objects.filter(status = MatchStatus.WaitingForMatch.value)
    if not wfm:
        waiting_for_match_order = MatchOrder()
        waiting_for_match_order.status = MatchStatus.WaitingForMatch.value
        waiting_for_match_order.save()
    cal = MatchOrder.objects.filter(status = MatchStatus.Cancelled.value)
    if not cal:
        cancelled_order = MatchOrder()
        cancelled_order.status = MatchStatus.Cancelled.value
        cancelled_order.save()
    unf = MatchOrder.objects.filter(status = MatchStatus.Unconfirmation.value)
    if not unf:
        unconfirm_order = MatchOrder()
        unconfirm_order.status = MatchStatus.Unconfirmation.value
        unconfirm_order.save()
    mte = MatchOrder.objects.filter(status = MatchStatus.MergeToExist.value)
    if not mte:
        merge_order = MatchOrder()
        merge_order.status = MatchStatus.MergeToExist.value
        merge_order.save()
    fin = MatchOrder.objects.filter(status = MatchStatus.Finish.value)
    if not fin:
        finish_order = MatchOrder()
        finish_order.status = MatchStatus.Finish.value
        finish_order.save()
    
    #market
    try:
        ms = Market.objects.get(marketId='kacans')
    except Market.DoesNotExist:
        m = Market(marketId='kacans',name=u'开拍币-小蚁股', price=D('0'))
        m.save()
    try:
        ms = Market.objects.get(marketId='lzglzj')
    except Market.DoesNotExist:
        m = Market(marketId='lzglzj',name=u'量子股份-量子积分', price=D('0'))
        m.save()
    try:
        ms = Market.objects.get(marketId='anccny')
    except Market.DoesNotExist:
        m = Market(marketId='anccny',name=u'小蚁币-人民币', price=D('0'))
        m.save()
    try:
        ms = Market.objects.get(marketId='anscny')
    except Market.DoesNotExist:
        m = Market(marketId='anscny',name=u'小蚁股-人民币', price=D('0'))
        m.save()
    '''
    try:
        ms = Market.objects.get(marketId='sysans')
    except Market.DoesNotExist:
        m = Market(marketId='sysans',name=u'申一股份-小蚁股', price=D('0'))
        m.save()
    try:
        ms = Market.objects.get(marketId='sycans')
    except Market.DoesNotExist:
        m = Market(marketId='sycans',name=u'申一币-小蚁股', price=D('0'))
        m.save()
    '''
