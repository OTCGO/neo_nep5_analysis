#coding:utf8


def remove_zero(sciStr):
    '''科学计数法转换成字符串'''
    assert type('str')==type(sciStr),'invalid format'
    if 'E' in sciStr:
        s = '%.8f' % float(sciStr)
    else:
        s = sciStr
    while '0' == s[-1] and '.' in s:
        s = s[:-1]
    if '.' == s[-1]:
        s = s[:-1]
    return s

def remove_zero_old(x):
    '''old,will be delete'''
    x = str(x)
    if x.startswith('0E-'):
        return '0'
    if '.' not in x:
        return x
    else:
        x = x.rstrip('0')
        if x and x[-1] == '.':
            return x[:-1]
        if not x:
            return '0'
        return x
