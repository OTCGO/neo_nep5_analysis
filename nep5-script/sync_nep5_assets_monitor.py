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
import os.path
import json
import binascii
import argparse
from time import strftime, gmtime
from NEP5Handler import NEP5Handler


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
            # print("file created:{0}".format(event.src_path))
            # print os.path.basename(event.src_path)

            # data = JSONFileHandler.load(os.path.join(
            #     rootdir, os.path.basename(event.src_path)))
            blockIndex = get_block_index(os.path.basename(event.src_path))
            print 'blockIndex', blockIndex
            data = JSONFileHandler.load(event.src_path)
            nep5 = NEP5Handler(args)
            if data is not None:
                for item in data:
                    # print type(item)
                    # print item['txid']
                    item['blockIndex'] = blockIndex
                    if item['state']['value'][0]['value'] == transfer:
                        nep5.transfer(item)
            # print data

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


class JSONFileHandler(object):

    @staticmethod
    def store(path, data):
        with open(path, 'w') as json_file:
            json_file.write(json.dumps(data))

    @staticmethod
    def load(path):
        with open(path) as json_file:
            data = json.load(json_file)
            return data


class FileHandle(object):
    @staticmethod
    def fileList(path):
        list = os.listdir(path)  # 列出文件夹下所有的目录与文件
        return list


def get_block_index(filename):
    blockIndex = re.split(r'-', filename)
    return os.path.splitext(blockIndex[1])[0]


# python sync_nep5_assets_monitor.py -d neo-otc -r /Users/wei/Desktop/otcgo/neo_wallet_analysis/nep5-script/test -m 127.0.0.1:27017

# python sync_nep5_assets_monitor.py - d neo - otc - r / home / wei / Desktop / neo - work / neo - cli / Notifications - m 127.0.0.1: 27017


if __name__ == "__main__":
    try:
        # 定义操作
        transfer = '7472616e73666572'

        # rootdir = '/Users/wei/Desktop/otcgo/neo_wallet_analysis/nep5-script/test'

        parser = argparse.ArgumentParser()
        parser.add_argument("-d", "--db", default='neo-otc',
                            help="verify database name, default antshares")
        parser.add_argument("-r", "--rootdir", default='/Notifications',
                            help="neo cli notifications finder")
        args = parser.parse_args()
        print args

        # 监控文件夹
        observer = Observer()
        event_handler = FileEventHandler()
        observer.schedule(event_handler, args.rootdir, True)
        observer.start()
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            time.sleep(1)
            observer.start()
        observer.join()

    except Exception as e:
        print e
