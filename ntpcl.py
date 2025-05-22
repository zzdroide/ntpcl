#!/usr/bin/env python3
#20200301
#Jan Mojzis
#Public domain.

# To test:
# Computer B (test):
#   sudo systemctl stop systemd-timesyncd.service
#   timedatectl set-timezone Europe/Moscow
# Computer A (dev):
#   sudo faketime @1680404340 ./ntpcl.py
# Computer B:
#   run "sudo ntpdate -v 10.0.0.4" repeatedly, with Computer A's IP

import socket
import time
import os
import struct
import json
import urllib.request
from pwd import getpwnam
from grp import getgrnam

NTPFORMAT = ">3B b 3I 4Q"
NTPDELTA = 2208988800.0
precision = -29
UTCp3 = 10800  # UTC+03:00

# CH899 query limit: 21:50
# DST advance: 00:00 - 21:50 = 2:10
dst_advance_secs = (2*60 + 10) * 60

def load_config():
        try:
                with open('config.json') as f:
                        return json.load(f)
        except FileNotFoundError:
                return {}

def ping_healthcheck(url):
        if url:
                urllib.request.urlopen(url, timeout=10)

def s2n(t = 0.0):       # System to NTP
        t += NTPDELTA
        return (int(t) << 32) + int(abs(t - int(t)) * (1<<32))

def currtime(ch899):
        seconds = time.time()
        gmtoff = time.localtime((seconds + dst_advance_secs) if ch899 else seconds).tm_gmtoff
        return seconds + gmtoff - UTCp3
        # To test:
        # faketime @1672531200 python3 -c "from ntpcl import currtime; print(currtime(False)); print(currtime(True))"
        # faketime @1685577600 python3 -c "from ntpcl import currtime; print(currtime(False)); print(currtime(True))"
        # faketime @1680397200 python3 -c "from ntpcl import currtime; print(currtime(False)); print(currtime(True))"

def main():
        config = load_config()
        clocks = config.get('clocks', {})

        nobody_uid = getpwnam('nobody').pw_uid
        nogroup_gid = getgrnam('nogroup').gr_gid

        # create socket
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.bind(("0.0.0.0", 123))

        # drop privileges
        os.setgid(nogroup_gid)
        os.setuid(nobody_uid)

        print('Listening')

        while True:
                try:
                        # receive the query
                        req_raw, addr = s.recvfrom(struct.calcsize(NTPFORMAT))
                        clock = clocks.get(addr[0], {})
                        serverrecv = s2n(currtime(clock.get('CH899')))
                        if len(req_raw) != struct.calcsize(NTPFORMAT):
                                raise Exception("Invalid NTP packet: packet too short: %d bytes" % (len(req_raw)))
                        try:
                                req_struct = struct.unpack(NTPFORMAT, req_raw)
                        except struct.error:
                                raise Exception("Invalid NTP packet: unable to parse packet")
                        req = list(req_struct)

                        # parse the NTP query (only Version, Mode, Transmit Timestamp)
                        version = req[0] >> 3 & 0x7
                        if (version > 4):
                                raise Exception("Invalid NTP packet: bad version %d" % (version))
                        mode = req[0] & 0x7
                        if (mode != 3):
                                raise Exception("Invalid NTP packet: bad client mode %d" % (mode))
                        clienttx = req[10]

                        # create the NTP response
                        res = [0] * 11
                        res[0] = version << 3 | 4                   # Leap, Version, Mode
                        res[1] = 1                                  # Stratum
                        res[2] = 0                                  # Poll
                        res[3] = precision                          # Precision
                        res[4] = 0                                  # Synchronizing Distance
                        res[5] = 0                                  # Synchronizing Dispersion
                        res[6] = 0                                  # Reference Clock Identifier
                        res[7] = serverrecv                         # Reference Timestamp
                        res[8] = clienttx                           # Originate Timestamp
                        res[9] = serverrecv                         # Receive Timestamp
                        res[10] = s2n(currtime(clock.get('CH899'))) # Transmit Timestamp

                        # send the response
                        data = struct.pack(NTPFORMAT, *res)
                        s.sendto(data, addr)

                except Exception as e:
                        print(f"{addr[0]}: failed: {e}")

                else:
                        ch899_marker = ' (ch899)' if clock.get('CH899') else ''

                        hc_error = ''
                        try:
                                ping_healthcheck(clock.get('healthcheck'))
                        except Exception as e:
                                hc_error = f' (HC PING FAILED: {e})'

                        print(f'{addr[0]}: ok{ch899_marker}{hc_error}')


if __name__ == "__main__":
        main()
