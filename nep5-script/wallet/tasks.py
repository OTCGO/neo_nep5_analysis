#coding:utf8
from __future__ import absolute_import

from time import sleep
from OTCGO.celery import app
from django.db import transaction
from OTCGO.Enums import MatchStatus
from django.core.cache import cache
from .Browser import Browser
from .WalletTool import WalletTool as WT

@app.task(queue='default')
@transaction.atomic
def confirm_transaction(oid):
    '''判断交易是否确认,为避免出现死循环，最多进行100次确认'''
    txid = WT.get_agency_order_prevhash(oid)
    tranHeight = cache.get('height')
    confirmations = 0
    while cache.get('height')==tranHeight:
        sleep(0.1)
    while True:
        exist = Browser().transaction(txid)
        if exist:
            break
        else:
            sleep(0.1)
    WT.update_agency_order_status(oid,MatchStatus.WaitingForMatch.value)
