#!/usr/bin/env python3

# parses a disk image copied from the SD card and saved under
# the name `LOXONE_SD.cdr` next to this script. This is a proof of concept
# on how to parse the file system.

import binascii
import struct
import pprint
import sys
import datetime

pp = pprint.PrettyPrinter(indent=4)

# STM32 CRC32 calculation, e.g. used for updates.
# Always requires 4 byte-aligned packages!
stm32_crc_table = None
def stm32_crc32(bytes_arr):
    global stm32_crc_table
    if stm32_crc_table is None:
        stm32_crc_table = {}
        poly = 0x04C11DB7
        for i in range(256):
            c = i << 24
            for j in range(8):
                c = (c << 1) ^ poly if (c & 0x80000000) else c << 1
            stm32_crc_table[i] = c & 0xFFFFFFFF
    length = len(bytes_arr)
    crc = 0xFFFFFFFF
    k = 0
    while length > 0:
        v = 0
        v |= ((bytes_arr[k + 0]) << 24) & 0xFF000000
        if length > 1:
            v |= ((bytes_arr[k + 1]) << 16) & 0x00FF0000
        if length > 2:
            v |= ((bytes_arr[k + 2]) << 8) & 0x0000FF00
        if length > 3:
            v |= ((bytes_arr[k + 3]) << 0) & 0x000000FF
        crc = ((crc << 8) & 0xFFFFFFFF) ^ stm32_crc_table[0xFF & ((crc >> 24) ^ v)]
        crc = ((crc << 8) & 0xFFFFFFFF) ^ stm32_crc_table[
            0xFF & ((crc >> 24) ^ (v >> 8))
        ]
        crc = ((crc << 8) & 0xFFFFFFFF) ^ stm32_crc_table[
            0xFF & ((crc >> 24) ^ (v >> 16))
        ]
        crc = ((crc << 8) & 0xFFFFFFFF) ^ stm32_crc_table[
            0xFF & ((crc >> 24) ^ (v >> 24))
        ]
        k += 4
        length -= 4
    return crc

def readSector(sectorNumber):
    f = open('LOXONE_SD.cdr', 'rb')
    f.seek(sectorNumber*512, 0)
    sectorData = f.read(512)
    f.close()
    return sectorData
def formatData(data,n=64):
    str = binascii.hexlify(data).decode('utf-8')
    return '\n'.join([str[i:i+n] for i in range(0, len(str), n)])

def parseFSInfoStruct(data):
    if struct.unpack('<I', data[0x000:4])[0] != 0x41615252:
        return None
    if struct.unpack('<I', data[0x1FC:])[0] != 0xAA550000:
        return None
    if struct.unpack('<I', data[0x1E4:0x1E8])[0] != 0x61417272:
        return None
    rootOffset,imageOffset,filesystemOffset,filesystemLastSector,clusterSize = struct.unpack('<IIIII', data[0x1CC:0x1CC+20])
    return rootOffset,imageOffset,filesystemOffset,filesystemLastSector,clusterSize
    
def parseFirmwareHeader(data):
    magic,imageSectorCount,firmwareVersion,xorChecksum,imageCompressedSize,imageUncompressedSize = struct.unpack('<IIIIII', data[:7*4])
    if magic != 0xC2C101AC:
        return None
    return imageSectorCount,firmwareVersion,xorChecksum,imageCompressedSize,imageUncompressedSize

volumeOffset = 0
ll = parseFSInfoStruct(readSector(1))
if not ll:
    MBRSector = readSector(0)
    volumeOffset,volumeSize = struct.unpack('<II', MBRSector[0x1C6:0x1C6+4*2])
    if volumeOffset > 500000:
        sys.exit(-1)
    ll = parseFSInfoStruct(readSector(volumeOffset+1))
    if not ll:
        sys.exit(-2)
rootOffset,imageOffset,filesystemOffset,filesystemEndOffset,clusterSize = ll
rootOffset += volumeOffset
imageOffset += rootOffset
filesystemOffset += imageOffset
filesystemEndOffset += imageOffset
print("Root       #%#08x : %#010x" % (rootOffset, rootOffset*0x200))
print("Image      #%#08x : %#010x/%#08x/%#010x to %#010x" % (imageOffset, (imageOffset)*0x200, (imageOffset+0x4000)*0x200, (imageOffset+0x8000)*0x200, (imageOffset+rootOffset+0xC000)*0x200))
print("Filesystem #%#08x-#%#08x : %#010x-%#010x (%dmb)" % (filesystemOffset, filesystemEndOffset, (filesystemOffset)*0x200, (filesystemEndOffset)*0x200, (filesystemEndOffset-filesystemOffset)*0x200/0x400/0x400))

def dtstr(timesstamp):
    # 1230768000 = 1.1.2009 Loxone Starttime
    return datetime.datetime.fromtimestamp(timesstamp+1230768000)
def psector(sector,count=1):
    if True: # Offsets vs. Sectornumber and Offsets
        if count == 1:
            return '%#010x' % ((sector+filesystemOffset)*0x200)
        else:
            return '%#010x - %#010x (%d)' % ((sector+filesystemOffset)*0x200,(sector+filesystemOffset+count)*0x200-1,count)
    else:
        if count == 1:
            return '#%#08x/%#010x' % (sector,(sector+filesystemOffset)*0x200)
        else:
            return '#%#08x/%#010x - #%#08x/%#010x (%d)' % (sector,(sector+filesystemOffset)*0x200,sector+count-1,(sector+filesystemOffset+count)*0x200-1,count)
def loadSector(sector):
    data = readSector(sector)
    magic,versionHigh,versionLow,nextSector = struct.unpack('<IIII', data[:16])
    version = versionLow + (versionHigh << 32)
    magicStr = chr((magic>>24)&0xff)+chr((magic>>16)&0xff)+chr((magic>>8)&0xff)+chr((magic>>0)&0xff)
    crc = struct.unpack('<I', data[0x1fc:0x200])[0]
    if crc == binascii.crc32(data[:0x1fc]):
        return (magicStr,version,nextSector,data[0x10:0x1fc])
def loadSectorWithVersion(sector):
    s1 = loadSector(sector)
    s2 = loadSector(sector+1)
    if not s1 and not s2:
        return
    if s1:
        (magic1,version1,nextSector1,data1) = s1
    else:
        (magic1,version1,nextSector1,data1) = [0] * 4
    if s2:
        (magic2,version2,nextSector2,data2) = s2
    else:
        (magic2,version2,nextSector2,data2) = [0] * 4
    if version1 > version2:
        data = data1
        version = version1
        magic = magic1
        nextSector = nextSector1
        headerSector = sector
    else:
        data = data2
        version = version2
        magic = magic2
        nextSector = nextSector2
        headerSector = sector+1
    return (magic,version,headerSector,nextSector,data)
def loadRange(sector):
    s = loadSectorWithVersion(sector)
    if not s:
        return
    (magic,version,headerSector,nextSector,data) = s
    lastSector = sector
    bitmasks = []
    if magic == 'LXFA':
        bitmasks = struct.unpack('<122I', data[4:4+122*4])
        while nextSector != 0:
            s = loadSectorWithVersion(filesystemOffset+nextSector)
            if not s:
                break
            lastSector = nextSector
            (magic2,version2,headerSector2,nextSector,data2) = s
            bitmasks2 = struct.unpack('<122I', data2[4:4+122*4])
            bitmasks += bitmasks2
        clusters = bitmasks
    elif magic == 'LXFD':
        clusters = struct.unpack('<45I', data[0x138:0x138+45*4])
        while nextSector != 0:
            s = loadSectorWithVersion(filesystemOffset+nextSector)
            if not s:
                break
            lastSector = nextSector
            (magic2,version2,headerSector2,nextSector,data2) = s
            clusters2 = struct.unpack('<62I', data2[0xF4:0xF4+62*4])
            clusters += clusters2
    elif magic == 'LXFF' or magic == 'LXFR':
        clusters = struct.unpack('<86I', data[0x94:0x94+86*4])
        while nextSector != 0:
            s = loadSectorWithVersion(filesystemOffset+nextSector)
            if not s:
                break
            lastSector = nextSector
            (magic2,version2,headerSector2,nextSector,data2) = s
            clusters2 = struct.unpack('<123I', data2[:123*4])
            clusters += clusters2
    while len(clusters) >= 1 and clusters[-1]==0:
        clusters = clusters[:-1]
    return (magic,version,headerSector,lastSector,data,clusters)

magicDict = {
    'LXFD':'LxFs Directory',
    'LXFC':'LxFs Directory Extension',
    'LXFF':'LxFs File',
    'LXFE':'LxFs File Extension',
    'LXFR':'LxFs R (similar to File?)',
    'LXFT':'LxFs Transaction',
    'LXFA':'LxFs Allocation',
}

skip2Sector = -1
for sector in range(filesystemOffset,filesystemEndOffset,2):
    if sector <= skip2Sector+filesystemOffset:
        continue
    if sector >= 0x012545 and sector < 0x384c04:
        break
    s = loadSectorWithVersion(sector)
    if not s: # a sector without a system record (empty or file data)
        #print("%s - <empty>" % (psector(sector-filesystemOffset)))
        continue
    (magic,version,headerSector,nextSector,data) = s
    magic = magicDict.get(magic, magic)
    label = None

    if magic=='LxFs Directory':
        label = data[:0x80].decode('utf-8').rstrip('\0')
        parentSector,createTime = struct.unpack('<II', data[0x80:0x80+2*4])
        if parentSector == 0 and len(label)==0:
            label = '"/" (%s)' % (dtstr(createTime))
        else:
            label = '"%s" (%s %s)' % (label,psector(parentSector),dtstr(createTime))
        r = loadRange(sector)
        if r:
            (_,_,_,lastSector,_,clusters) = r
            cs = []
            for c in clusters:
                if not c:
                    continue
                cs.append(psector(c))
            label = label + ' [' + ' '.join(cs) + ']'
            skip2Sector = lastSector
    elif magic=='LxFs File':
        label = data[:0x80].decode('utf-8')
        parentSector,createTime,modifyTime,fileSize,maxFilesize = struct.unpack('<IIIII', data[0x80:0x80+5*4])
        if createTime == modifyTime:
            dstr = 'ts:%s' % (dtstr(modifyTime))
        else:
            dstr = 'tsc:%s tsm:%s' % (dtstr(createTime),dtstr(modifyTime))
        label = '"%s" (parent:%s %s size:%dkb maxsize:%dkb)' % (label,psector(parentSector),dstr,fileSize/0x400,maxFilesize/0x400)
        r = loadRange(sector)
        if r:
            (_,_,_,lastSector,_,clusters) = r
            cs = []
            for c in clusters:
                cs.append(psector(c))
            #label = label + ' [' + ' '.join(cs) + ']'
            skip2Sector = lastSector

    if label:
        print("%s - %5d - %s %s" % (psector(sector-filesystemOffset),version,magic,label))
    else:
        print("%s - %5d - %s" % (psector(sector-filesystemOffset),version,magic))

    if magic == 'LxFs Allocation':
        r = loadRange(sector)
        if r:
            (magic,version,headerSector,lastSector,data,clusters) = r
            skip2Sector = lastSector
            print('Allocation Table:')
            bitmaskStr = ''
            for bitmask in clusters:
                for bit in range(0,31):
                    if bitmask & (1<<bit):
                        bitmaskStr += '1'
                    else:
                        bitmaskStr += '0'
            #print(bitmaskStr)
            sector = 0
            while sector < len(bitmaskStr):
                isUsed = bitmaskStr[sector]
                startSector = sector
                while sector < len(bitmaskStr) and bitmaskStr[sector] == isUsed:
                    sector += 1
                if isUsed == '0':
                    isUsed = 'E'
                else:
                    isUsed = 'U'
                print('%c%7d : %s - %s' % (isUsed,sector-startSector,psector(startSector),psector(sector-1)))
