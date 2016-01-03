# Ipseity

*noun*
selfhood; individual identity, individuality

Ipseity is a clock-in, clock-out timekeeping app. It was designed to run in the gym I went to, to keep track of who was in the gym, when the arrived and how long they spent there.

This repo is the software part that is designed to run on a Raspberry Pi, coupled to an NFC reader and some LEDs.

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
