#!/usr/bin/env python
# coding: utf8
import os
import sys

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "OTCGO.settings")

    import django
    django.setup()
    import json
    import gevent
    from time import sleep
    from datetime import datetime
    from django.core.cache import cache
    from OTCGO.Enums import MatchStatus,Option,ClaimStatus
    from wallet.Browser import Browser
    from wallet.WalletTool import WalletTool as WT
    BR = Browser()
    GEVENT_MAX = 100

    def get_fixed_slice(arr, step):
        for i in xrange(0,len(arr),step):
            yield arr[i:i+step]
    
    def get_current_height():
        bc = BR.height()['height']
        return bc

    def update_agency_order_state(ao):
        tx = ao.prevHash
        r = BR.transaction(tx)
        if r:
            #OTC
            if Option.SellerOTC.value == ao.option:
                if ao.contractAddress:
                    WT.update_agency_order_status(ao.id, MatchStatus.WaitingForMatch.value)
                else:
                    WT.update_agency_order_status(ao.id, MatchStatus.Finish.value)
            #ICO
            if Option.BuyerICO.value == ao.option:
                if ao.way:
                    WT.update_agency_order_status(ao.id, MatchStatus.WaitingForMatch.value)
                else:
                    WT.update_agency_order_status(ao.id, MatchStatus.Finish.value)
            #Free Match
            print 'update agency order %s' % ao.id

    def update_transfer_state(tr):
        tx = tr.txid
        r = BR.transaction(tx)
        if r:
            x = cache.get(tx)
            if not x:
                cache.set(tx,json.dumps(r))
            tr.confirm = True
            tr.save()
            print 'update transfer %s' % tr.id

    def update_unredeem_history_state(h):
        tx = h.txid
        r = BR.transaction(tx)
        if r:
            h.confirm = True
            h.save()
            print 'update history %s' % h.id

    def update_redeem_history_state(h):
        tx = h.redeemTxid
        r = BR.transaction(tx)
        if r:
            h.confirm = True
            h.save()
            print 'update history %s' % h.id

    def update_ancclaim_state(a):
        tx = a.txid
        r = BR.transaction(tx)
        if r:
            a.status = ClaimStatus.Finish.value
            a.save()
            print 'update ancclaim %s' % a.id
        elif 0<a.height and cache.get('height') - a.height>5:
            a.delete()


    while True:
        current_bc = get_current_height()
        #print 'current block height:%s' % current_bc
        bc = cache.get('height')
        #print 'cache block height:%s' % bc
        if not bc or current_bc > bc:
            cache.set('height', current_bc)
            print '%s set cache block height:%s' % (datetime.now(),current_bc)
            #update status
            aos = WT.get_unconfirm_agency_order()
            trs = WT.get_unconfirm_transfer()
            his = WT.get_unredeem_unconfirm_history()
            his2 = WT.get_redeem_unconfirm_history()
            acls = WT.get_unconfirm_ancclaims()
            for ass in get_fixed_slice(aos,GEVENT_MAX):
                threads = []
                for ao in ass:
                    threads.append(gevent.spawn(update_agency_order_state, ao))
                gevent.joinall(threads)
            for tss in get_fixed_slice(trs, GEVENT_MAX):
                threads = []
                for tr in tss:
                    threads.append(gevent.spawn(update_transfer_state, tr))
                gevent.joinall(threads)
            for hss in get_fixed_slice(his, GEVENT_MAX):
                threads = []
                for h in hss:
                    threads.append(gevent.spawn(update_unredeem_history_state, h))
                gevent.joinall(threads)
            for hss in get_fixed_slice(his2, GEVENT_MAX):
                threads = []
                for h in hss:
                    threads.append(gevent.spawn(update_redeem_history_state, h))
                gevent.joinall(threads)
            for acl in get_fixed_slice(acls, GEVENT_MAX):
                threads = []
                for a in acl:
                    threads.append(gevent.spawn(update_ancclaim_state, a))
                gevent.joinall(threads)
        sleep(0.05)
