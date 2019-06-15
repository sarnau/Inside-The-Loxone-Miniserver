#!/usr/bin/python3
# -*- coding: utf-8 -*-

import struct

# This file on the Miniserver contains the size of objects from the config in bytes
# It does create it by initializing every single object and measuring the memory
# usage of it. Index #1 for example is the Document object.
f = open('./sys/Sizes.bin', 'rb')
data = f.read()
f.close()

for val in range(0,len(data),4):
    print('#%3d : %d bytes' % (val/4,struct.unpack('<I', data[val:val+4])[0]))
