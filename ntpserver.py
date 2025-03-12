#!/usr/bin/env python3
#20200301
#Jan Mojzis
#Public domain.

# To test:
# ntpdate -dq 127.0.0.1
# faketime '2025-01-01 00:00:00' python3 -c "from ntpserver import currtime; print(currtime())"

import socket
import time
import os
import struct
from pwd import getpwnam
from grp import getgrnam

NTPFORMAT = ">3B b 3I 4Q"
NTPDELTA = 2208988800.0
precision = -29

def s2n(t = 0.0):       # System to NTP
        t += NTPDELTA
        return (int(t) << 32) + int(abs(t - int(t)) * (1<<32))

def currtime():
        return time.time()

def main():
        nobody_uid = getpwnam('nobody').pw_uid
        nogroup_gid = getgrnam('nogroup').gr_gid

        # chroot
        root = '/var/lib/ntpserver'
        os.makedirs(root, mode=0o700, exist_ok=True)
        os.chroot(root)

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
                        serverrecv = s2n(currtime())
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
                        res[0] = version << 3 | 4      # Leap, Version, Mode
                        res[1] = 1                     # Stratum
                        res[2] = 0                     # Poll
                        res[3] = precision             # Precision
                        res[4] = 0                     # Synchronizing Distance
                        res[5] = 0                     # Synchronizing Dispersion
                        res[6] = 0                     # Reference Clock Identifier
                        res[7] = serverrecv            # Reference Timestamp
                        res[8] = clienttx              # Originate Timestamp
                        res[9] = serverrecv            # Receive Timestamp
                        res[10] = s2n(currtime())      # Transmit Timestamp

                        # send the response
                        data = struct.pack(NTPFORMAT, *res)
                        s.sendto(data, addr)

                except Exception as e:
                        print(f"{addr[0]}: failed: {e}")
                else:
                        print(f'{addr[0]}: ok')


if __name__ == "__main__":
        main()
