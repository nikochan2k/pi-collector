#!/usr/bin/python2
# -*- encoding: utf-8 -*-

import time
import argparse
import sys
import sqlite3
import os
import codecs
from multiprocessing import Queue, Array, Process

import wifi
import bluetooth
import gps

NAME = 'collect'
DESCRIPTION = "A tool for logging Wifi and Blutooth packet"
VERSION = '0.1'

LATITUDE = 0
LONGITUDE = 1
ALTITUDE = 2
SPEED = 3
COURSE = 4
HDOP = 5
VDOP = 6
GPS = 7

def write(out, content):
    with open(out, 'a') as f:
        f.write(content['uptime'])
        f.write(',')
        f.write(content['date'])
        f.write(',')
        f.write(str(content['latitude']))
        f.write(',')
        f.write(str(content['longitude']))
        f.write(',')
        f.write(str(content['altitude']))
        f.write(',')
        f.write(str(content['speed']))
        f.write(',')
        f.write(str(content['course']))
        f.write(',')
        f.write(str(content['hdop']))
        f.write(',')
        f.write(str(content['vdop']))
        f.write(',')
        f.write(str(content['gps']))
        f.write(',')
        f.write(content['address'])
        f.write(',"')
        f.write(content.get('vendor') or '')
        f.write('","')
        f.write(content.get('name') or '')
        f.write('",')
        f.write(str(content.get('rssi') or ''))
        f.write(',')
        f.write(content.get('ap_address') or '')
        f.write(',"')
        f.write(content.get('ap_vendor') or '')
        f.write('","')
        f.write(content.get('ap_name') or '')
        f.write('",')
        f.write(str(content.get('ap_rssi') or ''))
        f.write(',')
        f.write(content['sender'])
        f.write(',')
        f.write(content.get('channel') or '')
        f.write(',')
        f.write(str(content.get('txpower') or ''))
        f.write('\r\n')


def main(args):
    if args.out and not os.path.exists(args.out):
        with open(args.out, 'w') as f:
            f.write(codecs.BOM_UTF8)
            f.write('uptime,timestamp,latitude,longitude,altitude,speed,course,hdop,vdop,gps,address,vendor,name,rssi,ap_address,ap_vendor,ap_name,ap_rssi,sender,channel,txpower\r\n')

    if args.gps.startswith('/dev/'):
        fields = Array('d', range(8))
        fields[LATITUDE] = 0
        fields[LONGITUDE] = 0
        fields[ALTITUDE] = 0
        fields[SPEED] = 0
        fields[COURSE] = 0
        fields[HDOP] = 0
        fields[VDOP] = 0
        fields[GPS] = 0
        p_gps = Process(target=gps.receive, args=(args.gps, fields,))
        p_gps.daemon = True
        p_gps.start()
    else:
        latlon = args.gps.split(',')
        fields = (float(latlon[0]), float(latlon[1]), 0.0, 0.0, 0.0, 0.0, 0,0, 0.0)

    q = Queue()

    channels = args.channels.split(',')
    p_wifi = Process(target=wifi.scan, args=(args.wifi, args.sta, channels, q,))
    p_wifi.daemon = True

    p_bluetooth = Process(target=bluetooth.scan, args=(q,))
    p_bluetooth.daemon = True

    p_wifi.start()
    p_bluetooth.start()

    while True:
        try:
            content = q.get()
            content['latitude'] = fields[LATITUDE]
            content['longitude'] = fields[LONGITUDE]
            content['altitude'] = fields[ALTITUDE]
            content['speed'] = fields[SPEED]
            content['course'] = fields[COURSE]
            content['hdop'] = fields[HDOP]
            content['vdop'] = fields[VDOP]
            content['gps'] = int(fields[GPS])
            if args.out:
                write(args.out, content)
            else:
                print(content)
        except KeyboardInterrupt:
            p_wifi.terminate()
            p_bluetooth.terminate()
            p_gps.terminate()
            sys.exit(1)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=DESCRIPTION)
    parser.add_argument('-c', '--channels', default='1,6,11,2,7,12,3,8,13,4,9,14,5,10', help="the channels to listen on")
    parser.add_argument('-o', '--out', help="output csv file name, output console if nothing")
    parser.add_argument('-w', '--wifi', required=True,
                        help="the capture wifi interface to use")
    parser.add_argument('-s', '--sta', type=int, default=1, help="0: AP mode, 1:STA mode")
    parser.add_argument('-g', '--gps', required=True,
                        help="GPS device path or fixed position [lat,lon]")
    args = parser.parse_args()

    main(args)

# vim: set et ts=4 sw=4:
