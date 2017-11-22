#!/usr/bin/env python
# coding: utf8
import os
import sys

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "OTCGO.settings")

    import django
    django.setup()
    import gevent
    from time import sleep
    from django.utils import timezone
    from OTCGO.Enums import ICOStatus
    from wallet.ICOTool import ICOTool as IT
    GEVENT_MAX = 100

    def get_fixed_slice(arr, step):
        for i in xrange(0,len(arr),step):
            yield arr[i:i+step]

    def update_ico_state(ico):
        currentTime = timezone.now()
        if currentTime >= ico.startTime and currentTime < ico.endTime and ICOStatus.NotStart.value == ico.status:
            IT.update_ico_status(ico.id, ICOStatus.Proceeding.value)
            print 'start ico:%s status' % ico.id
        if ico.endTime <= currentTime and ICOStatus.NotStart.value == ico.status:
            IT.update_ico_status(ico.id, ICOStatus.Dead.value)
            print 'kill ico:%s status' % ico.id
        if ico.endTime <= currentTime and ICOStatus.Proceeding.value == ico.status:
            IT.update_ico_status(ico.id, ICOStatus.Failure.value)
            print 'failure ico:%s status' % ico.id


    while True:
        unstart = IT.get_unstart_icos()
        for us in get_fixed_slice(unstart, GEVENT_MAX):
            threads = []
            for ui in us:
                threads.append(gevent.spawn(update_ico_state, ui))
            gevent.joinall(threads)
        sleep(10)
