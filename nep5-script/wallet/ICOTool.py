#coding:utf8
from datetime import datetime
from django.utils import timezone
from OTCGO.Enums import ICOStatus
from wallet.models import ICO,EarlyBird,AgencyOrder


class ICOTool:
    @staticmethod
    def get_ico_by_id(icoId):
        '''通过id找到ICO'''
        return ICO.get_by_id(icoId)
    @staticmethod
    def get_lock_ico(icoId):
        return ICO.lock_to_update(icoId)
    @staticmethod
    def ico_exist_by_id(icoId):
        '''ICO是否存在'''
        return ICO.exist(icoId)
    @staticmethod
    def get_current_shares(icoId):
        '''获得已筹集份额'''
        return ICO.get_current_shares_by_id(icoId)
    @staticmethod
    def get_total_shares(icoId):
        '''获得众筹目标份额数'''
        return ICO.get_total_shares_by_id(icoId)
    @classmethod
    def ico_is_active(cls, icoId):
        '''ICO市场正在众筹，status=Proceeding'''
        if not cls.ico_exist_by_id(icoId):
            return False
        return ICO.is_active(icoId)
    @classmethod
    def shares_acceptable(cls, icoId, shares):
        '''份额可接受，即份额是否已超过最大值'''
        cs = cls.get_current_shares(icoId)
        ts = cls.get_total_shares(icoId)
        if cs + shares <= ts:
            return True
        return False
    @staticmethod
    def get_early_bird(ico,shares):
        '''计算早鸟奖励'''
        currentTime = timezone.now()
        earlyBird = EarlyBird.get_by_icoid_and_time(ico.id, currentTime)
        if earlyBird:
            return earlyBird.rewardPerShare*shares
        return 0
    @staticmethod 
    def ico_sellers_are_all_confirm(icoId):
        return AgencyOrder.ico_sellers_are_all_confirm(icoId)
    @staticmethod 
    def ico_buyers_are_all_confirm(icoId):
        return AgencyOrder.ico_buyers_are_all_confirm(icoId)
    @staticmethod
    def ico_sellers_are_all_finish(icoId):
        return AgencyOrder.ico_sellers_are_all_finish(icoId)
    @classmethod
    def get_ico_sellers(cls, icoId, limit=0):
        ico = cls.get_ico_by_id(icoId)
        if ICOStatus.Success.value == ico.status:
            return AgencyOrder.get_ico_sellers_on_finish(icoId)
        if ico.status in [ICOStatus.Proceeding.value, ICOStatus.WaitingForPromise.value]:
            return AgencyOrder.get_ico_sellers_on_waiting_for_match(icoId,limit)
        return []
    @classmethod
    def get_ico_addresses(cls, icoId):
        buyers = cls.get_ico_sellers(icoId)
        return list(set([b.address for b in buyers]))
    @staticmethod
    def ico_is_waiting_promise(icoId):
        return ICO.is_waiting_promise(icoId)
    @staticmethod
    def get_status_string(status):
        if ICOStatus.NotStart.value == status:
            return 'notStart'
        if ICOStatus.Proceeding.value == status:
            return 'proceeding'
        if ICOStatus.WaitingForPromise.value == status:
            return 'waitingForPromise'
        if ICOStatus.Success.value == status:
            return 'success'
        if ICOStatus.Failure.value == status:
            return 'failure'
        if ICOStatus.BreakOff.value == status:
            return 'breakOff'
        if ICOStatus.Dead.value == status:
            return 'dead'
        return 'unknown'
    @staticmethod
    def get_unstart_icos():
        return ICO.get_unstarts()
    @staticmethod
    def update_ico_status(icoId, status):
        ICO.update_status(icoId, status)
    @classmethod
    def can_cancel(cls, ao):
        ico = cls.get_ico_by_id(ao.icoId)
        if ico.status in [ICOStatus.Failure.value,ICOStatus.BreakOff.value,ICOStatus.Dead.value]:
            return True
        return False
    @staticmethod
    def is_ico_not_start(ico):
        return ICOStatus.NotStart.value == ico.status
    @staticmethod
    def is_ico_proceeding(ico):
        return ICOStatus.Proceeding.value == ico.status
    @staticmethod
    def ico_password_correct(icoId, pwd):
        return ICO.password_correct(icoId, pwd)
