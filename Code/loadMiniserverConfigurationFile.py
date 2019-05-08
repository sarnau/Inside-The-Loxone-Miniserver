#!/usr/bin/env python
# -*- coding: utf-8 -*-

import struct
import ftplib
import zipfile
import StringIO
import sys

# Load the most recent version of the currently active configuration file
# from the Miniserver via FTP.

loxoneMiniServerIP = '192.168.178.200'  # IP address of the Loxone Miniserver
adminUsername = '<<ADMIN USER>>'
adminPassword = '<<ADMIN PASSWORD>>'

ftp = ftplib.FTP(loxoneMiniServerIP)
ftp.login(adminUsername, adminPassword)

# find the most current configuration file on the server:
ftp.cwd('prog')
filelist = []
for line in ftp.nlst():
  filelist.append(line[38:]) # skip all the stuff in front of the filename
filename = sorted(filelist)[-1]

data = []
def handle_binary(more_data):
    data.append(more_data)

resp = ftp.retrbinary("RETR /prog/"+filename, callback=handle_binary)
data = "".join(data)
ftp.quit()

zf = zipfile.ZipFile(StringIO.StringIO(data))
with zf.open('sps0.LoxCC') as f:
    header, = struct.unpack('<L', f.read(4))
    if header == 0xaabbccee:    # magic word to detect a compressed file
        compressedSize,header3,header4, = struct.unpack('<LLL', f.read(12))
        # header3 is roughly the length of the uncompressed data, but it is a bit higher
        # header4 could be a checksum, I don't know
        data = f.read(compressedSize)
        index = 0
        resultStr = ''
        while index<len(data):
            # the first byte contains the number of bytes to copy in the upper
            # nibble. If this nibble is 15, then another byte follows with
            # the remainder of bytes to copy. (Comment: it might be possible that
            # it follows the same scheme as below, which means: if more than
            # 255+15 bytes need to be copied, another 0xff byte follows and so on)
            byte, = struct.unpack('<B', data[index:index+1])
            index += 1
            copyBytes = byte >> 4
            byte &= 0xf
            if copyBytes == 15:
                copyBytes += ord(data[index])
                index += 1
            if copyBytes > 0:
                resultStr += data[index:index+copyBytes]
                index += copyBytes
            if index >= len(data):
                break
            # Reference to data which already was copied into the result.
            # bytesBack is the offset from the end of the string
            bytesBack, = struct.unpack('<H', data[index:index+2])
            index += 2
            # the number of bytes to be transferred is at least 4 plus the lower
            # nibble of the package header.
            bytesBackCopied = 4 + byte
            if byte == 15:
                # if the header was 15, then more than 19 bytes need to be copied.
                while True:
                    val, = struct.unpack('<B', data[index:index+1])
                    bytesBackCopied += val
                    index += 1
                    if val != 0xff:
                        break
            # Duplicating the last byte in the buffer multiple times is possible,
            # so we need to account for that.
            while bytesBackCopied > 0:
                if -bytesBack+1 == 0:
                    resultStr += resultStr[-bytesBack:]
                else:
                    resultStr += resultStr[-bytesBack:-bytesBack+1]
                bytesBackCopied -= 1
        with open('Project.Loxone', "w") as f:
            f.write(resultStr)
