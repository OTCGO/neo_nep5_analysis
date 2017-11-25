#!/usr/bin/env python
# coding: utf8
import os
import sys

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "OTCGO.settings")

    import django
    django.setup()
    from datetime import datetime
    from decimal import Decimal as D
    from django.utils import timezone
    from wallet.models import ICO,EarlyBird
    from OTCGO.Enums import MatchStatus,Option,ICOStatus
    from OTCGO.settings import TESTNET,TIME_ZONE

    if TESTNET:
        SYS = 'bbb7a08e52a5242079487fead6753dd038d41197e04e342b6f7b7358936551ea'
    else:
        SYS = '30e9636bc249f288139651d60f67c110c3ca4c3dd30ddfa3cbcec7bb13f14fd4'
    ANS = 'c56f33fc6ecfcd0c225c4ab356fee59390af8560be0e930faebe74a6daff7c9b'
    icoId = 1
    ico = ICO()
    ico.title = u'申一科技'
    ico.id = icoId
    ico.marketId = 'SYSicoANS'
    ico.assetId = ANS
    ico.valueId = SYS
    ico.password = 'AmIPassword?'
    ico.assetCapacity = D('100000000')
    ico.amountForICO = D('10000')  #拿多少出来众筹
    ico.amountToICO = D('100')   #众筹多少小蚁股
    ico.totalShares = D('10')    #分为多少份
    ico.assetPerShare = ico.amountToICO/ico.totalShares
    ico.valuePerShare = ico.amountForICO/ico.totalShares
    ico.price = ico.valuePerShare/ico.assetPerShare
    ico.adminAddress = 'AHZDq78w1ERcDYVBWjU5owWcbFZKLvhg7X'
    #ico.adminAddress = 'AUkVH4k8gPowAEpvQVAmNEkriX96CrKzk9'
    #ico.adminAddress = 'AJnNUn6HynVcco1p8LER72s4zXtNFYDnys'
    ico.status = ICOStatus.NotStart.value
    ico.startTime = timezone.make_aware(datetime.strptime('2017-8-5 10:42:00', '%Y-%m-%d %H:%M:%S'), timezone.get_current_timezone())
    ico.endTime = timezone.make_aware(datetime.strptime('2017-9-07 23:59:30', '%Y-%m-%d %H:%M:%S'), timezone.get_current_timezone())
    ico.save()

    #early bird
    '''
    eb0 = EarlyBird()
    eb0.icoId = icoId
    eb0.startTime = ico.startTime
    eb0.endTime = timezone.make_aware(datetime.strptime('2017-6-01 21:59:00', '%Y-%m-%d %H:%M:%S'), timezone.get_current_timezone())
    eb0.rewardPerShare = 1
    eb0.save()
    '''
