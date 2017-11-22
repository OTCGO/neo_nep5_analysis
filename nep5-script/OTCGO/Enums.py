#coding:utf8

from enum import IntEnum,unique

@unique
class MatchRole(IntEnum):
    Buyer = 1
    Seller = 2

@unique
class MatchStatus(IntEnum):
    MergeToExist = -5                   #合并同价单
    Unconfirmation = -4                 #挂单未确认
    WaitingForSignature = -3            #等待签名
    WaitingSendToAgencyContract= -2     #等待发送至合约
    WaitingForBroadcast= -1             #等待广播交易
    WaitingForMatch = 0                 #等待撮合
    Normal = 1                          #正常
    Unnormal = 2                        #异常
    WaitingForDoubleSpentChecking =3    #等待双花检测
    DoubleSpentChecking = 4             #双花检测中
    Finish = 5                          #已完成
    Cancelled = 6                       #已取消
    UnconfirmCancel = 7                 #取消未确认
    #For Recharge
    UnReceiveToken = 50                 #未收到代币
    ReceiveToken = 51                   #收到代币
    UnReceiveCash = 52                  #未收到现金
    #For Withdraw
    UnSignature = 70                    #未签名
    UnConfirmTransaction = 71           #交易未确认

@unique
class Option(IntEnum):
    AgencyTrade = 0                     #超导交易
    SellerOTC = 1                       #卖方超导, OTC
    BuyerICO = 2                        #买方超导，ICO

@unique
class ICOStatus(IntEnum):
    NotStart = 0                        #未开始
    Proceeding = 1                      #进行中
    WaitingForPromise = 2               #等待管理员兑现
    Success = 3                         #成功
    Failure = 4                         #失败
    BreakOff = 5                        #终止
    Dead = 6                            #死亡

@unique
class ClaimStatus(IntEnum):
    WaitingForSignature = 0             #待签名
    Unconfirmation = 1                  #待确认
    Finish = 2                          #已完成
