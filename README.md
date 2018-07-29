# WiFi & Bluetooth mac address collector

## Shopping List

* Buy Raspberry Pi Zero W, Raspberry Pi 3 or Raspberry Pi 3+.
* Buy a GPS module. https://www.robotshop.com/en/catalogsearch/result/?q=gps

## Setup

* Download RASPBIAN STRETCH LITE from https://www.raspberrypi.org/downloads/raspbian/ and install.
  * After installation, hit "apt-get update && apt-get upgrade"
* Download NEXMON from https://github.com/seemoo-lab/nexmon and setup. See the section "Build patches for bcm43430a1 on the RPI3/Zero W or bcm434355c0 on the RPI3+ using Raspbian (recommended)"
  * For setup, hit "apt-get install raspberrypi-kernel-headers git libgmp3-dev gawk qpdf bison flex make"
* setup Python modules
  * get-pip.py
    * wget https://bootstrap.pypa.io/get-pip.py
    * python get-pip.py
  * scapy
    * pip install scapy
  * micropyGPS
    * git clone https://github.com/inmcm/micropyGPS
    * cd ~/micropyGPS/
    * python setup.py install

## Usage
* To hit "python collect.py" will show usage.

