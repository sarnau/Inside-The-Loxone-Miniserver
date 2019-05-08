#!/usr/bin/python
# -*- coding: utf-8 -*-

import struct,os,sys,binascii

# This script takes a Miniserver update file and unpacks it as a folder structure
# in the current directory. It validates the checksum and applies the special
# decompression.

updateFilename = "10020326_Miniserver.upd"


# decompress a file inside the update image
def FDecompress(compressedData):
    destBuffer = bytearray()
    index = 0
    while index < len(compressedData):
        packageHeaderByte = ord(compressedData[index])
        index += 1
        if packageHeaderByte > 0x1F:
            byteCount = packageHeaderByte >> 5
            if byteCount == 7:
                byteCount += ord(compressedData[index])
                index += 1
            byteCount += 2
            byteOffset = ((packageHeaderByte & 0x1F) << 8) + ord(compressedData[index])
            index += 1
            backindex = len(destBuffer) - byteOffset - 1
            while byteCount > 0:
                destBuffer.append(destBuffer[backindex])
                backindex += 1
                byteCount -= 1
        else:
            while packageHeaderByte >= 0:
                destBuffer.append(compressedData[index])
                index += 1
                packageHeaderByte -= 1
    return destBuffer

f = open(updateFilename, "rb") # notice the b for binary mode
updateFileData = f.read()
f.close()
fileSize = len(updateFileData)

print "File length                 : %ld bytes" % fileSize
fileHeaderSize = 0x0200 # the header is always 512 bytes long
header,blockCount,version,checksum,comprByteCount,byteCount = struct.unpack_from("<6L", updateFileData, 0)
if header != 0xc2c101ac:
    print "Miniserver Update Header not detect"
    sys.exit(-1)
fileOffset = blockCount * 0x200 + fileHeaderSize
print "Update files offset         : 0x%lx" % (fileOffset)
print "Firmware Version            : %ld" % version
print "Firmware Compressed Bytes   : %ld bytes" % comprByteCount
print "Firmware Uncompressed Bytes : %ld bytes" % byteCount

# the image of the firmware is directly after the header
firmwareData = updateFileData[fileHeaderSize:fileHeaderSize+comprByteCount]

# the checksum is a trivial little endian XOR32 over the data
xorValue = 0x00000000
alignedFirmwareData = firmwareData + b'\0\0\0' # make sure the data allows 4-byte aligned access for the checksum
for offset in range(0, len(firmwareData), 4):
    xorValue ^= struct.unpack_from("<L", alignedFirmwareData, offset)[0]
if xorValue == checksum:
    newFile = open(os.path.splitext(updateFilename)[0] + ".bin", "wb")
    newFile.write(FDecompress(firmwareData))
else:
    print "Firmware Checksum WRONG     : %#08lx != %#08lx" % (checksum,xorValue)

# iterate over the other files in the update image
while fileOffset < fileSize:
    header,uncompressedSize,compressedSize = struct.unpack_from("<3L", updateFileData, fileOffset)
    headerUnscrambled = (header+0x6E7E5D4D) & 0xFFFFFFFF
    if headerUnscrambled > 1: # header valid?
        break
    fileOffset += 12
    # the full (UNIX-style) pathname after the header plus a single zero byte to terminate the string
    pathname = ''
    while ord(updateFileData[fileOffset]) != 0:
        pathname += updateFileData[fileOffset]
        fileOffset += 1
    fileOffset += 1
    pathname = '.' + pathname # prefix a '.' to the pathname to make it relative (otherwise we would try to write into root)
    directory,filename = os.path.split(pathname)
    if compressedSize: # file is compressed?
        filedata = FDecompress(updateFileData[fileOffset:fileOffset+compressedSize])
        fileOffset += compressedSize
        print 'Write %s [%d bytes, %d compressed bytes]' % (pathname, uncompressedSize, compressedSize)
        if not os.path.exists(directory):
            os.makedirs(directory)
        newFile = open(pathname, "wb")
        newFile.write(filedata)
    elif uncompressedSize: # file not compressed?
        filedata = updateFileData[fileOffset:fileOffset+uncompressedSize]
        fileOffset += uncompressedSize
        print 'Write %s [%d bytes, uncompressed]' % (pathname, uncompressedSize)
        if not os.path.exists(directory):
            os.makedirs(directory)
        newFile = open(pathname, "wb")
        newFile.write(filedata)
    elif headerUnscrambled == 1: # delete files in the Miniserver filesystem (used to e.g. flush caches)
        print 'Delete %s' % pathname
# we really don't want an update file deleting stuff on our disk...
#        if os.path.exists(pathname):
#            os.remove(pathname)
    else: # headerUnscrambled == 0 # create empty directories
        print 'Create %s' % pathname
        if not os.path.exists(directory):
            os.makedirs(directory)
    # round to the next 32-bit
    fileOffset = ((fileOffset + 3) & ~3)
