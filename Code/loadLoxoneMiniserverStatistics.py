#!/usr/bin/env python
# -*- coding: utf-8 -*-

import struct
import ftplib
import datetime
import sys

loxoneMiniServerIP = '192.168.178.200'  # IP address of the Loxone Miniserver
adminUsername = '<<ADMIN USER>>'
adminPassword = '<<ADMIN PASSWORD>>'

ftp = ftplib.FTP(loxoneMiniServerIP)
ftp.login(adminUsername, adminPassword)

# find the most current configuration file on the server:
ftp.cwd('stats')
filelist = []
for line in ftp.nlst():
  filelist.append(line[38:]) # skip all the stuff in front of the filename

def handle_binary(more_data):
    data.append(more_data)

# the stored values are rounded up
def numberOfValues(entryCount):
    if entryCount > 7: valueCount = 10
    elif entryCount > 3: valueCount = 7
    elif entryCount > 1: valueCount = 3
    else: valueCount = 1
    return 8 + valueCount * 8 # the size of an entry

for filename in sorted(filelist):
    data = []
    # the filename contains the UUID, month/year
    uuid = filename[:-7] # format: %08x-%04x-%04x-%16x
    year = int(filename[-6:-2])
    month = int(filename[-2:])

    # download the statistic file
    resp = ftp.retrbinary("RETR /stats/"+filename, callback=handle_binary)
    filedata = "".join(data)

    # the first 4 32-words LSB are the header, followed by the name (zero-terminated)
    valueCount,controlType,nameLength = struct.unpack('<III', filedata[:12])
    # control type is the type of the object in the Loxone Config file, it is a value >0 and smaller than 600.
    topBit = (valueCount & 0x80000000) == 0x80000000 # always set, might have been a version flag?
    valueCount &= 0x7FFFFFFF
    entrySize = numberOfValues(valueCount) # the size of the entry is rounded up depending on the number of values (up to 10)
    # the entries are aligned by the size of an entry
    firstPos = ((12 + nameLength + 1 + entrySize - 1) / entrySize) * entrySize
    print('%d %d %3d %2d.%d %s %s' % (topBit, valueCount,controlType,month,year,uuid,filedata[12:12+nameLength]))
    for entryPos in range(firstPos,len(filedata),entrySize):
        entry = filedata[entryPos:entryPos+entrySize]
        values = list(struct.unpack('<HHI%dd' % valueCount, entry[:2*4+valueCount*8]))
        # values[1], values[0] are 16-bit values, part of the UUID of the object (the 2nd and 3rd 16-bit group, see above)
        # values[2] is the unsigned 32-bit Loxone timestamp, which is a UNIX-UTC-timestamp, which starts at 1.1.2009,
        # resulting in an 1230768000 offset to the UNIX starttime 1.1.1970.
        # Up to ten 64-bit double values are following
        valStr = ''
        for value in values[3:]:
            valStr += '%f ' % value
        print('%04x-%04x %s %s' % (values[1],values[0],datetime.datetime.fromtimestamp(values[2]+1230768000), valStr))
#        break
ftp.quit()
