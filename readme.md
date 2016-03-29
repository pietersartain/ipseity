# Ipseity

*noun*
selfhood; individual identity, individuality

Ipseity is a clock-in, clock-out timekeeping app. It was designed to run in the gym I went to, to keep track of who was in the gym, when the arrived and how long they spent there.

This repo is the software part that is designed to run on a Raspberry Pi, coupled to an NFC reader and some LEDs.

# Installation
The instructions below assume you have a RasPi freshly installed with Raspbian (a circa 2014 version), but nothing else.

## Prepare the RasPi

 * Update hostname (current host bcf-whoishere)
 * Change password for default account "pi" (new password is: bK7NQbdS438dvR)
 * Sort out the networking:

Update /etc/wpa_supplicant/wpa_supplicant.conf

```
ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
#update_config=1

network={
priority=5
ssid="AndroidAP"
proto=RSN
key_mgmt=WPA-PSK
pairwise=CCMP TKIP
group=CCMP TKIP
psk="a959df7d1bc4"
}
```

Update /etc/network/interfaces, replace wlan0 info with the following:

```
allow-hotplug wlan0
auto wlan0
iface wlan0 inet dhcp
pre-up wpa_supplicant -Dwext -i wlan0 -c /etc/wpa_supplicant/wpa_supplicant.conf -B
```

 * Sort out the i2c

```
sudo vim /etc/modules
+i2c-bcm2708
+i2c-dev

sudo vim /etc/modprobe.d/raspi-blacklist.conf
-blacklist spi-bcm2708
-blacklist i2c-bcm2708
```

## Build & install dependancies on Raspbian

Use the setup-pi-python.sh script to:
 * Rebuild Python 2.7 with --enable-shared
 * Install distribute & pip
 * Install uwsgi (1.9.15)

## Optional / probably not used
 * Add /etc/apt/sources.list.d/quick2wire.list
```
# Quick2Wire Software
deb http://dist.quick2wire.com/raspbian wheezy main
deb-src http://dist.quick2wire.com/raspbian wheezy main
```
 * Install quick2wire
 * Install flask with `sudo CFLAGS=-I/usr/local/include/python2.7 pip install flask`

## Build & install ipseity

 * Copy the ipseity source directory to the Pi
 * dpkg-buildpackage -rfakeroot -b
 * dpkg -i ipseity_1.0_all.deb

# TODO

 * Fix reporting output (seems broken on live system)
 * Ability to specifically login/logout people
 * Configurable auto-logout (Local: auto log out user 5 hours after logging in)
 * Refactor to share DB code between NFCDaemon and core app
 * Investigate running nfcdaemon and ipseity as non-root users (Note this may require some fairly heavy rewriting on the nfcdaemon part because of the RPi GPIO things. Look at maybe quick2wire-gpio-admin and switching to that)
 * Build other deps as proper deb packages. We can use nginx and python3 in the debian/control file, but nearly all the other deps are built from source or pulled in via pip and should probably be turned into packages.
     * ipseity web interface (python 2.7):
         * python 2.7.5
         * uwsgi
         * flask
         * sqlite3
     * nfcdaemon (python 3.2):
         * sqlite3
 * Add unit tests (I know, I know. Really should've sorted this first ...)

# Copyright & Licensing

nfcdaemon and ipseity are both original works Copyright 2013-2016 Pieter Sartain, and released under the MIT license. See license.txt for details.

[quick2wire](https://github.com/quick2wire/quick2wire-python-api) included under the MIT license.

[py532lib](https://github.com/HubCityLabs/py532lib) included under the BSD 2 Clause license.

[daemon3x](https://github.com/metachris/python-posix-daemon) included under a (presumed) permissive license.
