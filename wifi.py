#!/usr/bin/python2
# -*- encoding: utf-8 -*-

import threading
from datetime import datetime
import sys
import os
from scapy.all import *
from radiotap import radiotap_parse
import oui

last_address = None
last_ap_address = None

def output(queue, content):
    address = content.get('address')
    if address:
        if address.startswith('33:33') or address == 'FF:FF:FF:FF:FF:FF':
            return

    ap_address = content.get('ap_address')
    if ap_address:
        if ap_address.startswith('33:33') or ap_address == 'FF:FF:FF:FF:FF:FF':
            return

    if queue is None:
        print(content)
    else:
        queue.put(content)


def get_vendor(address):
    vendor_id = address[:8]
    vendor = oui.VENDORS.get(vendor_id)
    if vendor is None:
        vendor = 'UNKNOWN'
    return vendor


def create_packet_callback(channel, sta, queue):

    def packet_callback(packet):
        if not packet.haslayer(Dot11):
            return

        with open('/proc/uptime', 'r') as f:
            uptime = f.readline().split()[0]
        now = datetime.now()

        address = None
        ap_address = None
        if packet.type == 0:
            if sta and packet.subtype == 0:
                sender = 'STA_AssoReq'
                ap_address = packet.addr1
                address = packet.addr2
            elif sta and packet.subtype == 1:
                sender = 'AP_AssoResp'
                address = packet.addr1
                ap_address = packet.addr2
            elif sta and packet.subtype == 2:
                sender = 'STA_ReassoResp'
                ap_address = packet.addr1
                address = packet.addr2
            elif sta and packet.subtype == 3:
                sender = 'AP_ReassoResp'
                address = packet.addr1
                ap_address = packet.addr2
            elif sta and packet.subtype == 4:
                sender = 'STA_ProbeReq'
                address = packet.addr2
            elif sta and packet.subtype == 5:
                sender = 'AP_ProbeResp'
                address = packet.addr1
                ap_address = packet.addr2
            elif not sta and packet.subtype == 8:
                sender = 'AP_Beacon'
                ap_address = packet.addr2
            elif sta and packet.subtype == 9:
                sender = 'AP_ATIM'
                address = packet.addr1
                ap_address = packet.addr2
            elif sta and packet.subtype == 10:
                sender = 'AP_Disas'
                address = packet.addr1
                ap_address = packet.addr2
            elif sta and packet.subtype == 11:
                sender = 'STA_Auth'
                ap_address = packet.addr1
                address = packet.addr2
            elif sta and packet.subtype == 12:
                sender = 'STA_Deauth'
                ap_address = packet.addr1
                address = packet.addr2
            else:
                return
        elif sta and packet.type == 2 and packet.subtype == 0:
            ds = packet.FCfield & 0x3
            # to_ds = (ds & 0x1) != 0
            # from_ds = (ds & 0x2) != 0
            if ds == 1: # STA to AP
                sender = 'STA_Data'
                ap_address = packet.addr1
                address = packet.addr2
            elif ds == 2: # AP to STA
                address = packet.addr1
                sender = 'AP_Data'
                ap_address = packet.addr2
            else:
                return
        else:
            return

        global last_address, last_ap_address
        if address == last_address and ap_address == last_ap_address:
            return
        last_address = address
        last_ap_address = ap_address

        content = {'uptime': uptime, 'date': now.strftime("%Y/%m/%d %H:%M:%S"), 'sender': sender, 'channel': channel}
        if address:
            content['address'] = address.upper()
            content['vendor'] = get_vendor(address)

        if ap_address:
            content['ap_address'] = ap_address.upper()
            content['ap_vendor'] = get_vendor(ap_address)
            try:
                content['ap_name'] = packet.info.decode('utf-8', errors='replace')
            except UnicodeEncodeError:
                content['ap_name'] = packet.info
            except AttributeError:
                pass

        offset, headers = radiotap_parse(str(packet))
        if sender.startswith('STA_'):
            content['rssi'] = headers['dbm_antsignal'] 
        else:
            content['ap_rssi'] = headers['dbm_antsignal'] 

        output(queue, content)

    return packet_callback


def _sniff(interface, channel, queue, sta):
    sniff(iface=interface, prn=create_packet_callback(channel, queue, sta), timeout=10,
            store=0, filter='link[26] = 0x40')


def scan(interface, sta, channels, queue = None):
    while True:
        for channel in channels:
            try:
                # sniff on specified channel
                os.system('ifconfig wlan0 down')
                os.system('nexutil -k' + str(channel))
                os.system('ifconfig mon0 up')
                t = threading.Thread(target=_sniff, args=(interface, channel, sta, queue,))
                t.daemon = True
                t.start()
                t.join()
            except KeyboardInterrupt:
                sys.exit(1)


if __name__ == '__main__':
    args = sys.argv
    if len(args) < 2:
        print('wifi.py [wifi_dev]')
        sys.exit(1)

    sta = 1
    if 3 <= len(args):
        sta = int(args[2])

    channels = (1,6,11,2,7,12,3,8,13,4,9,14,5,10)
    if 4 <= len(args):
        channels = args[3].split(',')

    scan(args[1], sta, channels, None)

