#coding:utf8

from decimal import Decimal as D,ROUND_DOWN

def consult_price(ask_price, bid_price, way):
    '''
    参数说明：
        ask_price   卖出数量
        bid_price   买入数量
        way         身份，True为卖方，False为买方
    返回值：
        ask_return  卖出价
        bid_return  买入价
    '''
    if way:
        if ask_price >= bid_price:
            price = ask_price
        else:
            price = bid_price
    else:
        if ask_price >= bid_price:
            price = bid_price
        else:
            price = ask_price
    return price

def consult_amount(ask_amount, bid_amount, price, divisible):
    '''
    参数说明：
        ask_amount  卖出数量
        bid_amount  买入数量
        price       价格
        divisible   卖出量是否可分割
    返回值：
        ask_return  卖出协商值
        bid_return  买入协商值
    '''
    ask_return = D('0')
    bid_return = D('0')
    bid_max = ask_amount * price
    if bid_max >= bid_amount:
        ask_return = bid_amount/price
        if divisible:
            ask_return = ask_return.quantize(D('1.'),rounding=ROUND_DOWN)
        else:
            ask_return = ask_return.quantize(D('.0001'),rounding=ROUND_DOWN)
        bid_return = ask_return * price
    else:
        ask_return = ask_amount
        bid_return = ask_amount * price
    return ask_return,bid_return


if __name__ == "__main__":
    print '-----test consult price-----'
    print 'ask price:%s, bid price:%s, way:%s' % (D('10.2'), D('8.3'), True)
    print 'consult price: ', consult_price(D('10.2'), D('8.3'), True)
    print 'ask price:%s, bid price:%s, way:%s' % (D('10.2'), D('11.3'), True)
    print 'consult price: ', consult_price(D('10.2'), D('11.3'), True)
    print 'ask price:%s, bid price:%s, way:%s' % (D('10.2'), D('8.3'), False)
    print 'consult price: ', consult_price(D('10.2'), D('8.3'), False)
    print 'ask price:%s, bid price:%s, way:%s' % (D('10.2'), D('11.3'), False)
    print 'consult price: ', consult_price(D('10.2'), D('11.3'), False)
    print
    print '-----test consult amount-----'
    ask_amount = D('11')
    bid_amount = D('100.2345')
    price = D('8.3333')
    divisible = True
    print 'ask amount:',ask_amount
    print 'bid amount:',bid_amount
    print 'price:',price
    print 'divisible:',consult_amount(ask_amount, bid_amount, price, divisible)
    divisible = False
    print 'undivisible:',consult_amount(ask_amount, bid_amount, price, divisible)
