#!/usr/bin/python3
# -*- coding: utf-8 -*-

import struct
import gzip
import zipfile
import os

def uncompressArchive(filename, rootpath):
    _,extension = os.path.splitext(filename)
    if extension == '.agz':
        with open(filename, 'rb') as f:
            foffset = 0
            while True:
                f.seek(foffset)
                entry = f.read(0x100)
                offset,size = struct.unpack("<LL", entry[-8:])
                if offset == 0:
                    break
                pathname = entry[0:-8].decode('utf8').rstrip('\0')
                print("- %s %08x %d" % (pathname, offset, size))
                foffset += 0x100
                f.seek(offset)
                data = f.read(size)
                dpath = os.path.join(rootpath, pathname)
                directory = os.path.dirname(dpath)
                if directory:
                    if not os.path.exists(directory):
                        os.makedirs(directory)
                fo = open(dpath, 'wb')
                fo.write(gzip.decompress(data))
                fo.close()
    elif extension == '.zip':
        with zipfile.ZipFile(filename, 'r') as zip: 
            for info in zip.infolist():
                print('- %s' % info.filename)
                zip.extract(info, path=rootpath)

uncompressArchive('commonv2.agz', 'web')
uncompressArchive('images.zip', 'web')
