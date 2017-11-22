#coding:utf8
import requests
from decimal import Decimal as D
from OTCGO.settings import TESTNET,BROWSER,BROWSER_PORT
from core.Helper import remove_zero


class Browser(object):
    def __init__(self):
        if TESTNET:
            base_url = 'http://%s:%s/'+'testnet'
        else:
            base_url = 'http://%s:%s/'+'mainnet'
        self.base_url = base_url % (BROWSER, BROWSER_PORT)

    def address(self, address):
        try:
            url = self.base_url + '/address/' + address
            return requests.get(url).json()
        except:
            return None

    def transaction(self, txid):
        try:
            url = self.base_url + '/transaction/' + txid
            return requests.get(url).json()
        except:
            return None

    def block(self, num):
        try:
            url = self.base_url + '/block/' + str(num)
            return requests.get(url).json()
        except:
            return None

    def height(self):
        try:
            url = self.base_url + '/height'
            return requests.get(url).json()
        except:
            return None

    def claim(self, address, detail=False):
        decrementInterval = 2000000
        generationAmount = [8, 7, 6, 5, 4, 3, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1] 
        try:
            url = self.base_url + '/claim/' + address
            result = requests.get(url).json()
            if not result:
                if detail:
                    return {'enable':'0','disable':'0','claims':[]}
                else:
                    return {'enable':'0','disable':'0'}
            del result['_id']
            height = self.height()['height']
            enable = disable = D('0')
            for k,v in result.items():
                if 0 == v['stopIndex']:
                    v['stopIndex'] = height
                    v['status'] = False
                else:
                    v['status'] = True
                amount = D('0')
                ustart = v['startIndex'] / decrementInterval
                if ustart < len(generationAmount):
                    istart = v['startIndex'] % decrementInterval
                    uend =   v['stopIndex'] / decrementInterval
                    iend =   v['stopIndex'] % decrementInterval
                    if uend >= len(generationAmount):
                        uend = len(generationAmount)
                        iend = 0
                    if 0 == iend:
                        uend -= 1
                        iend = decrementInterval
                    while ustart < uend:
                        amount += (decrementInterval - istart) * generationAmount[ustart]
                        ustart += 1
                        istart = 0
                    assert ustart == uend,'error X'
                    amount += (iend - istart) * generationAmount[ustart]
                if v['startIndex'] > 0:
                    amount += D(self.block(v['stopIndex']-1)['sys_fee']) - D(self.block(v['startIndex'])['sys_fee'])
                else:
                    amount += D(self.block(v['stopIndex']-1)['sys_fee'])
                if v['status']:
                    enable += D(v['value']) / 100000000 * amount
                else:
                    disable += D(v['value']) / 100000000 * amount
            base = {'enable':remove_zero(str(enable)),'disable':remove_zero(str(disable))}
            if detail:
                base['claims'] = [i.split('_') for i in result.keys() if result[i]['stopHash']]
            return base
        except Exception as e:
            print 'error:',e
            return None
