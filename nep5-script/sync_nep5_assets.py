#! /usr/bin/env python
# coding: utf-8
# qknow@蓝鲸淘
# Licensed under the MIT License.


from watchdog.observers import Observer
from watchdog.events import *
import time
import pymongo
from AntShares.Wallets.Wallet import Wallet
from AntShares.Fixed8 import Fixed8


class FileEventHandler(FileSystemEventHandler):
    def __init__(self):
        FileSystemEventHandler.__init__(self)

    def on_moved(self, event):
        if event.is_directory:
            print("directory moved from {0} to {1}".format(
                event.src_path, event.dest_path))
        else:
            print("file moved from {0} to {1}".format(
                event.src_path, event.dest_path))

    def on_created(self, event):
        if event.is_directory:
            print("directory created:{0}".format(event.src_path))
        else:
            print("file created:{0}".format(event.src_path))

    def on_deleted(self, event):
        if event.is_directory:
            print("directory deleted:{0}".format(event.src_path))
        else:
            print("file deleted:{0}".format(event.src_path))

    def on_modified(self, event):
        if event.is_directory:
            print("directory modified:{0}".format(event.src_path))
        else:
            print("file modified:{0}".format(event.src_path))


class NEP5Handler(object):
    def __init__(self):
        self.client  = pymongo.MongoClient("192.168.31.9", 27017)
        self.db = self.client['neo-otcgo']
        self.collection = self.db.nep5
        self.wallet = Wallet()

    def transfer(self):
        print self.collection
        self.collection.insert_one({
            "blockIndex": '',
            "txid": "0x54e9364599c92d3915070414385ac8b1210c8f58faf6db7399acb47857951175",
            "contract": "0xecc6b20d3ccac1ee9ef109af5a7cdb85706b1df9",
            "operation": "transfer",
            # 转出
            "from": self.wallet.toAddress('89b82241f7d214516a4b517b5c6792d5ec867e1d'),
            # 输入
            "to": self.wallet.toAddress('03e5bf5e49fbd3b2bdafe712869ff6d01af5361f'),
            "value": Fixed8.getNumStr('00e40b5402')
        })


# def transfer_Handler():
#     wallet = Wallet()
#     client = pymongo.MongoClient("192.168.31.9", 27017)
#     db = client['neo-otcgo']


if __name__ == "__main__":
    observer = Observer()
    event_handler = FileEventHandler()
    observer.schedule(event_handler,"./test",True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
    # try:
    #     NEP5Handler().transfer()
    # except Exception as e:
    #     print e
    