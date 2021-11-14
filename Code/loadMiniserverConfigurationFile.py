#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import struct
import ftplib
import zipfile
import zlib
from io import BytesIO

# Load the most recent version of the currently active configuration file
# from the Miniserver via FTP.

loxoneMiniServerIP = '192.168.178.200'  # IP address of the Loxone Miniserver
adminUsername = '<<ADMIN USER>>'
adminPassword = '<<ADMIN PASSWORD>>'

ftp = ftplib.FTP(loxoneMiniServerIP)
ftp.login(adminUsername, adminPassword)

# find the most current configuration file on the server:

# Ignore all the special cases, because the Miniserver does load in this order:
#
# 1. /prog/Emergency.LoxCC (only if several reboots within 10 minutes happen!)
# 2. /prog/sps_new.zip
# 3. /prog/sps_new.LoxCC
# 4. all `/prog/sps_vers_yyyymmddhhmmss.zip`
#    or `/prog/sps_vers_yyyymmddhhmmss.LoxCC` files with `vers` less
#    or equal the max. version allowed for the Miniserver
#    (148 = 09030326; 162 = 10020326)
# 5. /prog/sps.zip
# 6. /prog/sps_old.zip
# 7. /prog/sps.LoxPLAN (a very old fileformat)
# 8. /prog/Default.Loxone or /prog/DefaultGo.Loxone, depending on the type of the Miniserver

ftp.cwd('prog')
filelist = []
for line in ftp.nlst():
  filename = line[38:]
  if filename.startswith('sps_') and (filename.endswith('.zip') or filename.endswith('.LoxCC')):
      filelist.append(filename)
filename = sorted(filelist)[-1]

download_file = BytesIO()
ftp.retrbinary("RETR /prog/"+filename, download_file.write)
download_file.seek(0)
ftp.quit()

#with open(filename, "wb") as f:
#   f.write(download_file.read())

zf = zipfile.ZipFile(download_file)
with zf.open('sps0.LoxCC') as f:
    header, = struct.unpack('<L', f.read(4))
    if header == 0xaabbccee:    # magic word to detect a compressed file
        compressedSize,uncompressedSize,checksum, = struct.unpack('<LLL', f.read(12))
        data = f.read(compressedSize)
        index = 0
        resultStr = bytearray()
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
                while True:
                    addByte = data[index]
                    copyBytes += addByte
                    index += 1
                    if addByte != 0xff:
                        break
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
        if checksum != zlib.crc32(resultStr):
            print('Checksum is wrong')
            sys.exit(1)
        if len(resultStr) != uncompressedSize:
            print('Uncompressed filesize is wrong %d != %d' % (len(resultStr),uncompressedSize))
            sys.exit(1)
        with open('Project.Loxone', "wb") as f:
            f.write(resultStr)
