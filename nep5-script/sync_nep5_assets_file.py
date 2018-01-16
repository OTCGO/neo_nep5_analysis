#! /usr/bin/env python
# coding: utf-8
# qknow@蓝鲸淘
# Licensed under the MIT License.


from watchdog.observers import Observer
from watchdog.events import *
import time

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
            print("file created:{0}".format(event.src_path))
            # print os.path.basename(event.src_path)

            # data = JSONFileHandler.load(os.path.join(
            #     rootdir, os.path.basename(event.src_path)))

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
    return os.path.splitext(blockIndex[1])


# python sync_nep5_assets_file.py  -r /Users/wei/Desktop/otcgo/neo_wallet_analysis/nep5-script/test -d neo-otcgo -m mongodb://otcgo:u3fhhrPr@114.215.30.71:27017/?authSource=admin&replicaSet=rs1 

# python sync_nep5_assets_file.py -d neo-otc -r /home/wei/Desktop/neo-work/neo-cli/Notifications -m 127.0.0.1:27017


if __name__ == "__main__":

    try:
        # 定义操作
        transfer = '7472616e73666572'
        parser = argparse.ArgumentParser()
        parser.add_argument("-m", "--mongodb",
                            help="verify database name, default antshares")
        parser.add_argument("-d", "--db",
                            help="verify collections name, default antshares")                    
        parser.add_argument("-r", "--rootdir", default='/Notifications',
                            help="neo cli notifications finder")
        args = parser.parse_args()

        print args
        rootdir = args.rootdir
        listArr = FileHandle.fileList(rootdir)

        print 'file count', len(listArr)
        # 循环文件夹
        nep5 = NEP5Handler(args)
        for f in range(0, len(listArr)):
            # print os.path.join(rootdir, listArr[f])
            blockIndex, file_extension = get_block_index(listArr[f])
            if file_extension != '.json':
                continue

            print 'blockIndex', blockIndex
            data = JSONFileHandler.load(os.path.join(rootdir, listArr[f]))
            if data is not None:
                for item in data:
                    # print type(item)
                    # print item['txid']
                    item['blockIndex'] = blockIndex
                    if item['state']['value'][0]['value'] == transfer:
                        nep5.transfer(item)

        print 'success'

    except Exception as e:
        print e
