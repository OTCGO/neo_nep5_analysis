#coding:utf8
import tornado.ioloop
import tornado.web
from pymongo import MongoClient
from datetime import datetime
from functools import partial
from fabric.api import local
import argparse
import json
from AntShares.Network.RemoteNode import RemoteNode

MC = MongoClient('mongodb://127.0.0.1:27017', maxPoolSize=200)


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("""<h1>Simple AntShares BlockChain Browser!</h1>
                    <ul>
                        <li>/{net}/height</li>
                        <li>/{net}/block/{block}</li>
                        <li>/{net}/transaction/{txid}</li>
                        <li>/{net}/address/{address}</li>
                        <li>/{net}/claim/{address}</li>
                    </ul>
                    """)

class BrowserHandler(tornado.web.RequestHandler):
    def get(self,xid):
        print '%s %s' % (datetime.now(),self.request.path),
        db,table = self.request.path.split('/')[1:3]
        if 'block' == table:
            xid = int(xid)
        table = MC[db][table+'s'] if table!='address' else MC[db][table+'es']
        result = table.find_one({'_id':xid})
        if result:
            print 'True'
            self.write(json.dumps(result))
        else:
            print 'False'
            self.write(json.dumps({}))

class HeightHandler(tornado.web.RequestHandler):
    def get(self):
        db = MC[self.request.path.split('/')[1]]
        h = db.blocks.count()
        print '%s %s' % (datetime.now(),self.request.path),'True'
        self.write(json.dumps({'height':h}))

application = tornado.web.Application([
        (r'/', MainHandler),
        (r'/testnet/address/(\w{33,34})', BrowserHandler),
        (r'/mainnet/address/(\w{33,34})', BrowserHandler),
        (r'/testnet/claim/(\w{33,34})', BrowserHandler),
        (r'/mainnet/claim/(\w{33,34})', BrowserHandler),
        (r'/testnet/transaction/(\w{64})', BrowserHandler),
        (r'/mainnet/transaction/(\w{64})', BrowserHandler),
        (r'/testnet/block/(\d{1,10})', BrowserHandler),
        (r'/mainnet/block/(\d{1,10})', BrowserHandler),
        (r'/testnet/height', HeightHandler),
        (r'/mainnet/height', HeightHandler),
        ])

def get_last_height(net):
    assert net in ['testnet','mainnet'],'Wrong Net'
    netPortDit = {'testnet':'20332','mainnet':'10332'}
    seeds = ['seed'+'%s' % i for i in range(1,6)]
    heights = []
    for seed in seeds:
        rn = RemoteNode('http://'+seed+'.neo.org:'+netPortDit[net])
        try:
            height = rn.getBlockCount()
        except:
            height = 0
        heights.append(height)
    print 'heights:%s' % heights
    return max(heights)

def check(monitor = 'both'):
    assert monitor in ['testnet','mainnet','both'],'Wrong Monitor'
    netList = []
    if monitor in ['testnet','both']:
        netList.append('testnet')
    if monitor in ['mainnet','both']:
        netList.append('mainnet')
    for k in netList:
        h = MC[k].blocks.count()
        rh = get_last_height(k)
        print '%s %s --> %s vs %s' % (datetime.now(), k, h,rh)
        if rh - h >= 2:
            print 'will restart %s' % k
            local('supervisorctl restart %s_node' % k)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-m", "--monitor", default='both', help="monitor which net,eg:mainnet,testnet,default both")
    args = parser.parse_args()
    application.listen(8888)
    tornado.ioloop.PeriodicCallback(partial(check, monitor=args.monitor), 500000).start()
    tornado.ioloop.IOLoop.instance().start()
