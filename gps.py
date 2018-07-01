#!/usr/bin/python2
# -*- encoding: utf-8 -*-

import time
from datetime import datetime
from datetime import timedelta
import sys
import micropyGPS
import os
import math

LATITUDE = 0
LONGITUDE = 1
ALTITUDE = 2
SPEED = 3
COURSE = 4
HDOP = 5
VDOP = 6
GPS = 7

last_timestamp = None

def output(gps):
    gps_status = 0
    if gps.valid is True:
        gps_status = 1
    data = {'latitude':gps.latitude[0], 'longigude':gps.longitude[0],'altitude':gps.altitude,
            'speed':gps.speed[0],'course':gps.course, 'gps':gps_status,
            'hdop':gps.hdop, 'vdop':gps.vdop}
    print(data)


def set_clock(gps, set_clock_minutes):
    if set_clock_minutes < 0:
        return

    global last_timestamp
    sec = math.modf(gps.timestamp[2])
    second = int(sec[1])
    microsecontd_tmp = int(str(sec[0])[2:])
    microsecond = int('{:<06d}'.format(microsecontd_tmp))
    now = datetime(2000+gps.date[2], gps.date[1], gps.date[0], 
         gps.timestamp[0], gps.timestamp[1], second, microsecond)
    if last_timestamp == None or last_timestamp <= (now - timedelta(minutes=set_clock_minutes)):
        last_timestamp = now
        now_str = now.strftime('%Y-%m-%d %H:%M:%S.%f')
        date_command = "date --set='%s' --utc" % now_str
        os.system(date_command)
        print('set system clock to %s UTC' % now_str)


def receive(gpsdev, fields = None, set_clock_minutes = 60):
    gps = micropyGPS.MicropyGPS(0, 'dd')

    with open(gpsdev, 'r') as f:
        while True:
            try:
                line = f.readline()
                if len(line) == 0:
                    continue
                if line[0] != '$':
                    continue
                for c in line:
                    stat = gps.update(c)
                    if stat is None:
                        continue
                    if fields is None:
                        output(gps)
                        continue
                    if gps.valid is False:
                        fields[GPS] = 0.0
                        continue
                    else:
                        fields[LATITUDE] = gps.latitude[0]
                        fields[LONGITUDE] = gps.longitude[0]
                        fields[ALTITUDE] = gps.altitude
                        fields[SPEED] = gps.speed[0]
                        fields[COURSE] = gps.course
                        fields[HDOP] = gps.hdop
                        fields[VDOP] = gps.vdop
                        fields[GPS] = 1.0
                    if gps.date[2] != 0:
                        set_clock(gps, set_clock_minutes)
                        continue
            except KeyboardInterrupt:
                sys.exit(1)


if __name__ == '__main__':
    args = sys.argv
    if len(args) < 2 or not os.path.exists(args[1]):
        print('gps.py [gps_device]')
        sys.exit(1)
    receive(args[1])
