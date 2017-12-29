#!/usr/bin/env python
# coding: utf8

from pymongo import MongoClient

if __name__ == "__main__":
    db = MongoClient('mongodb://otcgo:u3fhhrPr@114.215.30.71:27017/?authSource=admin&replicaSet=rs1')['neo-otcgo']
    db['nep5_m_addresses'].find_one()