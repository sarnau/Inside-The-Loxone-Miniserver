#!/usr/bin/env python
# -*- coding: utf-8 -*-

import struct
import ftplib
import sys
import binascii

loxoneMiniServerIP = '192.168.178.200'  # IP address of the Loxone Miniserver
adminUsername = '<<ADMIN USER>>'
adminPassword = '<<ADMIN PASSWORD>>'

ftp = ftplib.FTP(loxoneMiniServerIP)
ftp.login(adminUsername, adminPassword)

data = []
def handle_binary(more_data):
    data.append(more_data)

ftp.retrbinary("RETR /sys/Secret.txt", callback=handle_binary)
print(binascii.a2b_base64(data[0]))

ftp.quit()
