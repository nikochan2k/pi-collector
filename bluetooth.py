#!/usr/bin/python2
# -*- encoding: utf-8 -*-

import pexpect
import subprocess
from datetime import datetime
import sys
import re
import pylru
import oui

devices = {}
txpowers = pylru.lrucache(100)


def get_vendor(address):
    vendor_id = address[:8]
    vendor = oui.VENDORS.get(vendor_id)
    if vendor is None:
        vendor = 'UNKNOWN'
    return vendor


def parse(line):
    now = datetime.now()

    try:
        device_position = line.index('Device')
    except ValueError:
        return None
    else:
        if device_position < 0:
            return None
        global devices
        global txpowers
        attribute_str = line[device_position:]
        attribute_list = attribute_str.split(' ')
        address = attribute_list[1].upper()
        content = devices.get(address)
        if content is None:
            vendor = get_vendor(address)
            with open('/proc/uptime', 'r') as f:
                uptime = f.readline().split()[0]
            content = {'uptime': uptime, 'date': now.strftime("%Y/%m/%d %H:%M:%S.%f"),
                    'sender': 'BT_Advertising', 'address': address, 'vendor': vendor}
            devices[address] = content

        if 'RSSI:' in attribute_str:
            content['rssi'] = int(attribute_list[3])
        elif 'TxPower:' in attribute_str:
            txpowers[address] = int(attribute_list[3])
        elif 'ManufacturerData' in attribute_str or 'UUIDs' in attribute_str:
            return None
        elif attribute_list[2].count('-') == 5:
            content['name'] = 'UNKNOWN'
        else:
            if 'Name:' in attribute_str or 'Alias:' in attribute_str:
                content['name'] = ' '.join(attribute_list[3:])
            else:
                content['name'] = ' '.join(attribute_list[2:])
        if content.get('name') and content.get('rssi'):
            try:
                txpower = txpowers[address]
                content['txpower'] = txpower
            except KeyError:
                pass
            return devices.pop(address)
        return None


def scan(queue = None):
    out = subprocess.check_output('rfkill unblock bluetooth', shell = True)
    p = pexpect.spawn('bluetoothctl', echo = False)
    p.send('scan on' + '\n')
    while True:
        try:
            p.expect(r'Device[^\r\n]+')
            content = parse(p.after)
            if content:
                if queue is None:
                    print(content)
                else:
                    queue.put(content)
        except KeyboardInterrupt:
            sys.exit(1)
        except pexpect.EOF:
            pass
        except pexpect.TIMEOUT:
            pass


if __name__ == '__main__':
    scan()
