#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import struct
import serial
import binascii
import time
import random
import crcmod
import copy
import Crypto.Cipher.AES
from enum import IntEnum

from LoxoneAESKeys import *

def getDeviceType(devType):
    if devType == 0x01:
        return "Extension" # CBusLoxMOREHandler
    elif devType == 0x02:
        return "Dimmer Extension" # CBusLoxDIMMHandler
    elif devType == 0x03:
        return "EnOcean Extension" # CBusLoxCENOHandler
    elif devType == 0x04:
        return "DMX Extension" # CBusLoxCDMXHandler
    elif devType == 0x05:
        return "1-Wire Extension" # CBusLoxC1WRHandler
    elif devType == 0x06:
        return "RS232 Extension" # CBusLoxC232Handler
    elif devType == 0x07:
        return "RS485 Extension" # CBusLoxC232Handler
    elif devType == 0x08:
        return "IR Extension" # CBusLoxC485IHandler
    elif devType == 0x09:
        return "Modbus Extension" # CBusLoxC485MHandler
    elif devType == 0x0A:
        return "Fröling Extension" # CBusLoxC485MHandler (it's a Modbus device)
    elif devType == 0x0B:
        return "Relay Extension" # CBusLoxRELHandler
    elif devType == 0x0C:
        return "Air Base Extension" # CBusLoxCAIRHandler
    elif devType == 0x0D:
        return "Dali Extension" # CBusLoxDaliHandler
    elif devType == 0x0E:
        return "Modbus 232 Extension" # unknown
    elif devType == 0x0F:
        return "Fröling Extension"
    # CBusLoxC485VHandler seems to be related to valves, I have no idea what legacy extension uses it. It's "Comm485" with Protocol "4"

    # the following are not devices on the bus itself,
    # but rather reserved device types
    elif devType == 0x00:
        return "-Miniserver-"
    elif devType == 0x10:
        return "-NAT device-"
    elif devType == 0x1F:
        return "-Legacy Software Update-"
    # the following are NAT devices, because legacy devices
    # only use 4 bit for the device type
    elif devType == 0x12:
        return "Internorm Extension" # CBusLoxInternormHandler
    elif devType == 0x13:
        return "Tree Base Extension" # CBusTreeHandler
    elif devType == 0x14:
        return "DI Extension" # CBusLoxDigInHandler
    elif devType == 0x15:
        return "KNX Extension" # CBusKNXHandler
    elif devType == 0x16:
        return "AI Extension"
    elif devType == 0x17:
        return "AO Extension"
    return "device[0x%02X]" % devType
def getDeviceSubType(devType):
    #  if devType==1: return "Air Base"
    #  elif devType==2: return "Air MultiExtension"
    #  elif devType==4: return "Air WindowIntegral"
    #  elif devType==5: return "Air SmartSocket"
    #  elif devType==6: return "Air RoomSensor"
    #  elif devType==7: return "Air NanoIO Keypad Or Touch"
    #  elif devType==8: return "Air Presence"
    #  elif devType==9: return "Air Valve"
    #  elif devType==0xA: return "Air Rgbw Dimmer"
    #  elif devType==0xB: return "Air Pool Alarm"
    #  elif devType==0xC: return "Air Remote"
    #  elif devType==0xD: return "Air Touch Relay"
    #  elif devType==0xE: return "Air Pendant Ligh RGBW"
    #  elif devType==0xF: return "Air Viking"
    #  elif devType==0x11: return "Air Ir"
    #  elif devType==0x12: return "Air Universal"
    #  elif devType==0x13: return "Air Firealarm"
    #  elif devType==0x14: return "Air US Air Switch"
    #  elif devType==0x15: return "Air Shelf Control"
    #  elif devType==0x16: return "Air Touch"
    #  elif devType==0x18: return "Air Meter Int"
    #  elif devType==0x19: return "Air Tubemotor"
    #  elif devType==0x1A: return "Air Dali Air"
    #  elif devType==0x1B: return "Air Backwash Valve"
    #  elif devType==0x1C: return "Air Vent"
    #  elif devType==0x1D: return "Air Geiger Remote"
    #  elif devType==0x1E: return "Air Window Handle"
    #  elif devType==0x1F: return "Air Window Sensor"
    #  elif devType==0x20: return "Air Water Sensor"
    #  elif devType==0x21: return "Air NanoDimmer Keypad Or Touch"
    #  elif devType==0x22: return "Air Blind Motor"
    #  elif devType==0x23: return "Air Touch Pure"
    #  elif devType==0x24: return "Air Steak Thermo"
    #  elif devType==0x25: return "Air Corridor Light"
    #  elif devType==0x26: return "Air Obd Sniffer"
    #  elif devType==0x27: return "Air Touch Stone"
    #  elif devType==0x28: return "Air Weather Station"
    #  elif devType==0x29: return "Air Sun Wind Guard"
    #  elif devType==0x30: return "Air RoomSensor CO2"
    #  elif devType==0x31: return "Air Keypad"
    #  elif devType==0x32: return "Air Remote Air4GG"
    #  elif devType==0x33: return "Air Shade Actuator"
    #  elif devType==0x34: return "Air Noisemaker"
    #  elif devType==0x35: return "Air AmbientLight"
    #  elif devType==0x36: return "Air Leaf"
    #  elif devType==0x37: return "Air Leaf Touch"
    #  elif devType==0x38: return "Air Zipmotor"
    #  elif devType==0x39: return "Air Internorm Fan"
    if devType == 0x8001:
        return "Valve Actuator Tree"
    elif devType == 0x8002:
        return "Motion Sensor Tree"
    elif devType == 0x8003:
        return "Touch Tree"
    elif devType == 0x8004:
        return "Universal Tree"
    elif devType == 0x8005:
        return "Touch Pure Tree"
    elif devType == 0x8006:
        return "LED Ceiling Light Tree"
    elif devType == 0x8007:
        return "LED Surface Mount Spot RGBW Tree"
    elif devType == 0x8008:
        return "LED Spot RGBW Tree Gen 1"
    elif devType == 0x8009:
        return "NFC Code Touch Tree Gen 1"
    elif devType == 0x800A:
        return "Weather Station Tree"
    elif devType == 0x800B:
        return "Nano DI Tree"
    elif devType == 0x800C:
        return "RGBW 24V Dimmer Tree"
    elif devType == 0x800D:
        return "Touch Surface Tree"
    elif devType == 0x800E:
        return "LED Surface Mount Spot WW Tree"
    elif devType == 0x800F:
        return "LED Spot WW Tree Gen 1"
    elif devType == 0x8010:
        return "Room Comfort Sensor Tree"
    elif devType == 0x8011:
        return "LED Pendulum Slim RGBW Tree"
    elif devType == 0x8012:
        return "Alarm Siren Tree"
    elif devType == 0x8013:
        return "Damper Tree"
    elif devType == 0x8014:
        return "Leaf Tree"
    elif devType == 0x8015:
        return "Integrated Window Contact Tree"
    elif devType == 0x8016:
        return "LED Spot RGBW Tree"
    elif devType == 0x8017:
        return "LED Spot WW Tree"
    elif devType == 0x8018:
        return "Power Tree"
    elif devType == 0x8019:
        return "Nano 2 Relay Tree"
    elif devType == 0x801a:
        return "Ahri Tree"
    elif devType == 0x801b:
        return "Magnus Tree"
    elif devType == 0x801c:
        return "NFC Code Touch Tree"
    if devType & 0x8000:
        return "treeDev[0x%04X]" % devType
    else:
        return getDeviceType(devType)

###############################################################################
# Various hashing routines
###############################################################################

# 1-Wire CRC8 calculation
def onewire_crc8(data):
    crc = 0
    for i in range(len(data)):
        byte = data[i]
        for b in range(8):
            fb_bit = (crc ^ byte) & 0x01
            if fb_bit == 0x01:
                crc = crc ^ 0x18
            crc = (crc >> 1) & 0x7F
            if fb_bit == 0x01:
                crc = crc | 0x80
            byte = byte >> 1
    return crc


# CRC8 used for several simple 1-byte checksums
CRC8_function = crcmod.mkCrcFun(0x185, initCrc=0x00, rev=False, xorOut=0x00)

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

# RC6 encryption/decryption <https://en.wikipedia.org/wiki/RC6>
def ROR(x, n, bits=32):
  """rotate right input x, by n bits"""
  mask = (2**n) - 1
  mask_bits = x & mask
  return (x >> n) | (mask_bits << (bits - n))
def ROL(x, n, bits=32):
  """rotate left input x, by n bits"""
  return ROR(x, bits - n,bits)
def RC6_PrepareKey(str):
  key = 0
  for c in str:
    key += ord(c)
  return key | 0xFEED0000
def RC6_GenerateKey(initKey):
  """generate key s[0... 2r+3] from given input userkey"""
  L = (((initKey << 8) & 0x100) | (initKey << 24) | (initKey >> 24) | ((initKey >> 8) & 0x10)) & 0xFFFFFFFF
  r=16 # rounds
  w=32 # width in bits
  modulo = 2**32
  context_s=(2*r+4)*[0]
  context_s[0]=0xB7E15163
  for i in range(1,2*r+4):
    context_s[i]=(context_s[i-1]+0x9E3779B9)%(2**w)
  l = [L]
  enlength = 1
  v = 3*max(enlength,2*r+4)
  A=B=i=j=0
  for index in range(0,v):
    A = context_s[i] = ROL((context_s[i] + A + B)%modulo,3)
    B = l[j] = ROL((l[j] + A + B)%modulo,(A+B)%32) 
    i = (i + 1) % (2*r + 4)
    j = (j + 1) % enlength
  return context_s
def RC6_EncryptBlock(context,encoded):
  A,B,C,D = struct.unpack('<IIII', encoded)
  r=16
  w=32
  modulo = 2**32
  lgw = 5
  C = (C - context[2*r+3])%modulo
  A = (A - context[2*r+2])%modulo
  for j in range(1,r+1):
    i = r+1-j
    (A, B, C, D) = (D, A, B, C)
    u_temp = (D*(2*D + 1))%modulo
    u = ROL(u_temp,lgw)
    t_temp = (B*(2*B + 1))%modulo 
    t = ROL(t_temp,lgw)
    tmod=t%32
    umod=u%32
    C = (ROR((C-context[2*i+1])%modulo,tmod)  ^u)  
    A = (ROR((A-context[2*i])%modulo,umod)   ^t) 
  D = (D - context[1])%modulo 
  B = (B - context[0])%modulo
  return struct.pack('<IIII', A,B,C,D)
def RC6_DecryptBlock(context,encoded):
  A,B,C,D = struct.unpack('<IIII', encoded)
  r=16
  w=32
  modulo = 2**32
  lgw = 5
  B = (B + context[0])%modulo
  D = (D + context[1])%modulo 
  for i in range(1,r+1):
    t_temp = (B*(2*B + 1))%modulo 
    t = ROL(t_temp,lgw)
    u_temp = (D*(2*D + 1))%modulo
    u = ROL(u_temp,lgw)
    tmod=t%32
    umod=u%32
    A = (ROL(A^t,umod) + context[2*i])%modulo 
    C = (ROL(C^u,tmod) + context[2*i+ 1])%modulo
    (A, B, C, D)  =  (B, C, D, A)
  A = (A + context[2*r + 2])%modulo 
  C = (C + context[2*r + 3])%modulo
  return struct.pack('<IIII', A,B,C,D)
def RC6_Encrypt(context,data):
  blockSize = 16
  data += '\0' * (blockSize-1)
  data = data[:(len(data) / blockSize) * blockSize]
  result = ''
  for block in [data[i:i+blockSize] for i in range(0, len(data), blockSize)]:
    result += RC6_EncryptBlock(context,block)
  return result
def RC6_Decrypt(context,data):
  blockSize = 16
  result = ''
  for block in [data[i:i+blockSize] for i in range(0, len(data), blockSize)]:
    result += RC6_DecryptBlock(context,block)
  return result

def RSHash(key):
    # it seems a and b are switched by Loxone
    a = 63689
    hash = 0
    for i in range(len(key)):
        hash = hash * a + ord(key[i])
        hash = hash & 0xFFFFFFFF
        a = a * 378551
    return hash

def JSHash(key):
    hash = 1315423911
    for i in range(len(key)):
        hash ^= (hash >> 2) + ord(key[i]) + (hash * 32)
        hash = hash & 0xFFFFFFFF
    return hash

def DJBHash(key):
    hash = 5381
    for i in range(len(key)):
        hash += hash * 32 + ord(key[i])
        hash = hash & 0xFFFFFFFF
    return hash

def DEKHash(key):
    hash = len(key)
    for i in range(len(key)):
        hash = ((hash << 5) ^ (hash >> 27)) ^ ord(key[i])
        hash = hash & 0xFFFFFFFF
    return hash

def BPHash(key):
    hash = 0
    for i in range(len(key)):
        hash = (hash << 7) ^ ord(key[i])
        hash = hash & 0xFFFFFFFF
    return hash

###############################################################################
# A CAN bus message for the Loxone system
###############################################################################
fragmentPool = dict()
class LoxMessageFragment(object):
    # this is used to be forwarded all arriving messages,
    # which allows to combine fragmented packages
    @classmethod
    def fragmentForMessage(cls, message):
        global fragmentPool
        hashValue = 0
        if type(message) is LoxCanLegacyMessage:
            hashValue = (message.serial & 0x0FFFFFFF) | (int(message.isServerMessage != 0) << 28)
        else:
            hashValue = (message.deviceNAT) | (message.extensionNAT << 8) | (int(message.isServerMessage != 0) << 16)
        if hashValue not in fragmentPool:
            fragment = LoxMessageFragment()
            fragmentPool[hashValue] = fragment
        else:
            fragment = fragmentPool[hashValue]
        return fragment

    def __init__(self):
        self.Command = None  # the command is part of a fragmented package
        self.Size = None
        # depending on the format of the fragmented package,
        # this can be up to 64kb large.
        self.Checksum = None
        # legacy messages have a 16-bit sum checksum, NAT messages have
        # a STM32 CRC32 instead. This is used to confirm that the message
        # was fully received
        self.Data = None  # bytearray() of all the data

class LoxCanMessage(object):
    def __init__(self):
        # 29-bit CAN identifier
        self.address = 0x00000000
        # 8 bytes CAN data field
        self.data = bytearray([0x00] * 8)

    def __repr__(self):
        return "<LoxCanMessage address:%08x %s>" % (self.address, binascii.hexlify(self.data))

    # this is used to be forwarded all arriving messages,
    # which allows to combine fragmented packages
    @classmethod
    def addMessage(cls, fragment, message):
        pass

    @property
    def type(self):
        return (self.address >> 24) & 0x1F

    @type.setter
    def type(self, type):
        self.address = (self.address & 0x00FFFFFF) | (type << 24)

    @property
    def val8(self):
        return self.data[1]

    @val8.setter
    def val8(self, val8):
        self.data[1] = val8

    # data[2/3] are often a 16-bit value
    @property
    def val16(self):
        return self.data[2] + (self.data[3] << 8)

    @val16.setter
    def val16(self, val16):
        self.data[2] = val16 & 0xFF
        self.data[3] = (val16 >> 8) & 0xFF

    # data[4-8] are often a 32-bit value
    @property
    def val32(self):
        return self.data[4] + (self.data[5] << 8) + (self.data[6] << 16) + (self.data[7] << 24)

    @val32.setter
    def val32(self, val32):
        self.data[4] = val32 & 0xFF
        self.data[5] = (val32 >> 8) & 0xFF
        self.data[6] = (val32 >> 16) & 0xFF
        self.data[7] = (val32 >> 24) & 0xFF

    @classmethod
    def serialString(cls, serial):
        return "%08X" % (serial)

    @classmethod
    def versionString(cls, version):
        v1 = version / 1000000
        v2 = (version / 10000) % 100
        v3 = (version / 100) % 100
        v4 = version % 100
        return "%d.%d.%d.%d" % (v1, v2, v3, v4)

    @property
    def dateTimeString(self):
        return "%d/%d/%d, %ldms %d:%02d:%02d.%04d" % (
            ((self.data[2] & 0x7F) << 8) | (self.data[1]),
            (self.data[3] & 7) * 2 + (self.data[2] >> 7),
            int(self.data[3] / 8),
            self.val32,
            self.val32 / (60 * 60 * 1000),
            (self.val32 / (60 * 1000)) % 60,
            (self.val32 / 1000) % 60,
            self.val32 % 1000,
        )

class LoxCanLegacyMessage(LoxCanMessage):

    # this is not working, it is here just for reference
    def getFragmentedPackage(self, address, cmd, data):
        if cmd == 0x00:
            return "# Air send container %s" % (binascii.hexlify(data))
        elif cmd == 0x01:
            return "# Air send MAC container %s" % (binascii.hexlify(data))
        elif cmd == 0x02:  # C485V
            pass
        elif cmd == 0x04:
            external = (data[3] << 24) | (data[2] << 16) | (data[1] << 8) | (data[0])
            page = (data[5] << 8) | (data[4])
            crc = (data[9] << 24) | (data[8] << 16) | (data[7] << 8) | (data[6])
            return "# Send Page Crc External:%#08x pageCRC:%#08x page #%d" % ( external, crc, page)
        elif cmd == 0x05:  # send 8 bytes of an update file
            external = (data[3] << 24) | (data[2] << 16) | (data[1] << 8) | (data[0])
            address = ((data[7] << 24) | (data[6] << 16) | (data[5] << 8) | (data[4])) * 8
            return "# Send Retry Page External:%#08x address:%08X %s" % (external, address, binascii.hexlify(data[8:]))
        elif cmd == 0x06:
            return "# Send Config Data %s" % (binascii.hexlify(data))
        elif cmd == 0x07:  # Dali
            pass
        elif cmd == 0x08:  # Dali
            pass
        elif cmd == 0x09:
            offset = 0
            if data[0] == 0x00 and data[1] == 0x00 and data[2] == 0x00 and data[3] == 0x00:
                offset += 4
            packageSize = data[offset]
            if packageSize > 1:  # Zero-Byte at the end of the string is ignored anyway
                printfStr = data[offset + 1:-1].decode()
                return '# Send Webservice Request "%s"' % (printfStr)
            else:
                return '# Send Webservice Request ""'
        elif cmd == 0x0A:  # C232
            pass
        elif cmd == 0x0B:  # C485V
            return "# Send Webservice %s" % (binascii.hexlify(data))
        elif cmd == 0x0C:
            return "# Air NAT entry %s" % (binascii.hexlify(data))
        elif cmd == 0x0D:
            return "# DMX Send Actor Type:%d, Slewrate:%d, Gamma:%s DMX Address:%d, Data:%d %d %d %d" % (
                data[0],
                data[1] & 0x7F,
                "yes" if data[1] & 0x80 else "no",
                data[2] + (data[3] << 8) + 1,
                data[4],data[5],data[6],data[7],
            )
        elif cmd == 0x0E:
            return "# DMX Send Dimming Type:%d, Slewrate:%d, Gamma:%s DMX Address:%d, Data:%d %d %d %d, DeviceId:%08X" % (
                data[0],
                data[1] & 0x7F,
                "yes" if data[1] & 0x80 else "no",
                data[2] + (data[3] << 8) + 1,
                data[4],data[5],data[6],data[7],
                data[8] | (data[9] << 8) | (data[10] << 16) | (data[11] << 24),
            )
        elif cmd == 0x0F:
            return (
                "# DMX RDM Init. Slewrate:%d %d %d %d, Gamma:%d %d %d %d, RGB:%d %d %d %d, DMX Address:%d, DeviceId:%#08x"
                % (
                    data[0],
                    data[1],
                    data[2],
                    data[3],
                    data[4],
                    data[5],
                    data[6],
                    data[7],
                    data[8],
                    data[9],
                    data[10],
                    data[11],
                    data[12] | (data[13] << 8),
                    data[14] | (data[15] << 8) | (data[16] << 16) | (data[17] << 24),
                )
            )
        elif cmd == 0x13:
            time = (data[8] + (data[9] << 8)) & 0xFFF
            if data[9] & 0x40:
                time *= 10.0
            percentStr = ""
            if data[9] & 0x80:
                percentStr = "/100%"
            return (
                "# DMX Composite Actor Type:%d, DMX Address:%d, Data:%d %d %d %d, %.1fsec%s"
                % (
                    data[0],
                    data[2] + (data[3] << 8) + 1,
                    data[4],
                    data[5],
                    data[6],
                    data[7],
                    time * 0.1,
                    percentStr,
                )
            )
        else:
            return "# cmd %02x %s" % (cmd, binascii.hexlify(data))

    # The legacy commands are a bit messy, some of them are even reused in different ways depending on the hardware type
    class LoxCmd(IntEnum):
        send_identify = 0x0
        software_update = 0x1
        BootExtension = 0x2
        update_verify = 0x3
        ACKCFG = 0x4
        BC_ACK = 0x5
        BC_NAK = 0x6
        RequestStart = 0x7
        identity_led = 0x8
        alive_request = 0x9
        software_update_modules = 0xA
        identify_unknown_extensions = 0xB
        set_extension_offline = 0xC
        send_sync = 0xD
        SendBlinkPos = 0xE
        alive_reply = 0xF
        AnalogInputSensitivity0 = 0x10
        AnalogInputSensitivity1 = 0x11
        debug_send_printf = 0x12
        debug_crashreport = 0x13
        C485I_14 = 0x14
        C485I_15 = 0x15
        C485I_16 = 0x16
        C485I_17 = 0x17
        C485I_18 = 0x18
        command_19 = 0x19
        AirAliveRequestForFrequencyChange = 0x1A
        AirSendParam = 0x1B
        SendDebug = 0x1C
        RequestStatistics = 0x1D
        command_1E = 0x1E
        OtauRxPacket = 0x1F
        AnalogInputValue0 = 0x20
        EnoceanCmd = 0x21
        Enocean_22 = 0x22
        LearnEnocean = 0x23
        ValueFromEnocean = 0x24
        Enocean_25 = 0x25
        Enocean_26 = 0x26
        Enocean_27 = 0x27
        InitConfirm = 0x28
        Enocean_29 = 0x29
        Enocean_2A = 0x2A
        Enocean_2B = 0x2B
        DIMM_2C = 0x2C
        send_sync_package = 0x2D
        HandleQueueLevel = 0x2E
        HandleChannelUtilization = 0x2F
        AnalogOutputValue0 = 0x30
        AnalogOutputInit = 0x31
        DataGetChecksum = 0x32
        command_33 = 0x33
        SendRetryPage = 0x34
        SendLogLevel = 0x35
        CheckCfgCrc = 0x36
        ParkExtension = 0x37
        LinkDiagnosisRx = 0x38
        request_CAN_diagnosis_packet = 0x39
        command_3A = 0x3A
        command_3B = 0x3B
        command_3C = 0x3C
        command_3D = 0x3D
        command_3E = 0x3E
        command_3F = 0x3F
        DigitalInputSensitivity0 = 0x40
        DigitalInputSensitivity1 = 0x41
        DigitalInputSensitivity2 = 0x42
        DigitalInputSensitivity3 = 0x43
        SendFragmented = 0x44
        SendFragmentedLargeDataData = 0x45
        SendFragmentedLargeDataStart = 0x46
        DIMM_47 = 0x47
        command_48 = 0x48
        command_49 = 0x49
        command_4A = 0x4A
        command_4B = 0x4B
        command_4C = 0x4C
        command_4D = 0x4D
        command_4E = 0x4E
        command_4F = 0x4F
        ValueFromDigInputs = 0x50
        ValueFrequency = 0x51
        command_52 = 0x52
        command_send_temperature = 0x53
        SendPageCrc = 0x54
        command_55 = 0x55
        command_56 = 0x56
        command_57 = 0x57
        BootAirBase = 0x58
        command_59 = 0x59
        command_5A = 0x5A
        MuteExtension = 0x5B
        ValueFromC232C485SensorA = 0x5C
        C485M_5D = 0x5D
        C485M_5E = 0x5E
        C485M_5F = 0x5F
        set_DigOutputs = 0x60
        Enocean_61 = 0x61
        Enocean_62 = 0x62
        iButtonInit = 0x63
        SetMonitor = 0x64
        C1WR_SEARCH = 0x65
        AnalogValue1Wire = 0x66
        Air_67 = 0x67
        command_68 = 0x68
        C232_69 = 0x69
        LearnIR = 0x6A
        DaliValueReceived = 0x6B
        Dali_6C = 0x6C
        ChangeDaliAddresse = 0x6D
        DaliMonitorData = 0x6E
        DaliState = 0x6F
        ValueFromC232C485SensorB = 0x70
        C232_71 = 0x71
        C1WR_72 = 0x72
        C1WR_73 = 0x73
        LearnDMX = 0x74
        ValueFromUnknownSensor1 = 0x75
        ValueFromUnknownSensor2A = 0x76
        ValueFromUnknownSensor2B = 0x77
        ValueChecksum = 0x78
        RequestChecksum = 0x79
        Arrive1Wire = 0x7A
        Depart1Wire = 0x7B
        C232_7C = 0x7C
        command_7D = 0x7D
        command_7E = 0x7E
        command_7F = 0x7F

    def __init__(self):
        LoxCanMessage.__init__(self)
        self.fragmentCommand = 0
        self.fragmentSize = 0
        self.fragmentCRC = 0
        self.fragmentData = []

    def __repr__(self):
        if self.isServerMessage:
            typeStr = "S"
        else:
            typeStr = "E"
        return "<Legacy %s:%s %02x %s %s>" % (
            typeStr,
            LoxCanMessage.serialString(self.serial),
            int(self.command),
            binascii.hexlify(self.data[1:]),
            self.commandDescription,
        )

    @classmethod
    def addMessage(cls, message):
        fragment = LoxMessageFragment.fragmentForMessage(message)
        message.isFragmentedPackage = False
        if message.command == LoxCanLegacyMessage.LoxCmd.SendFragmented:  # Fragmented package - up to 1530 bytes large (6 bytes * 255 packages)
            packageIndex = message.data[1]  # 0=header, 1…255=packages
            if packageIndex == 0x00:  # header
                fragment.Command = LoxCanLegacyMessage.LoxCmd(message.data[2])
                fragment.Size = message.val32 & 0xFFFF
                fragment.Checksum = (message.val32 >> 16) & 0xFFFF  # actually a SUM16 over all bytes, not a CRC
                fragment.Data = '\0' * fragment.Size
            elif fragment.Data != None:
                fragment.Data = fragment.Data[:(packageIndex-1)*6] + message.data[2:] + fragment.Data[packageIndex*6:]
                if packageIndex * 6 >= fragment.Size and fragment.Size > 0:
                    fragment.Data = fragment.Data[: fragment.Size]
                    # add the complete command to the message
                    message.data = chr(0) + fragment.Data
                    message.isFragmentedPackage = True
                    message.command = fragment.Command
                    fragment.Command = 0x00
                    fragment.Size = 0
                    fragment.Checksum = 0
                    fragment.Data = None
        elif message.command == LoxCanLegacyMessage.LoxCmd.SendFragmentedLargeDataData:  # Large fragmented package header (less than 64kb package size)
            fragment.Command = LoxCanLegacyMessage.LoxCmd(message.data[2])
            fragment.Size = message.val32 & 0xFFFF
            fragment.Checksum = (message.val32 >> 16) & 0xFFFF  # actually a SUM16 over all bytes, not a CRC
        elif message.command == LoxCanLegacyMessage.LoxCmd.SendFragmentedLargeDataStart:  # Large fragmented package
            if fragment.Data:
                fragment.Data += message.data
            else:
                fragment.Data = message.data
            if len(fragment.Data) >= fragment.Size:
                fragment.Data = fragment.Data[: fragment.Size]
                # add the complete command to the message
                message.data = chr(0) + fragment.Data
                message.command = fragment.Command
                message.isFragmentedPackage = True
                fragment.Command = 0x00
                fragment.Size = 0
                fragment.Checksum = 0
                fragment.Data = None

    @property
    def isServerMessage(self):
        return ((self.address >> 28) & 1) != 0

    @isServerMessage.setter
    def isServerMessage(self, isServerMessage):
        commandByte = self.data[0] & 0x7F
        if not isServerMessage:
            commandByte |= 0x80  # messages from a device have bit 7 always set in the command
        self.data[0] = commandByte
        self.address = (self.address & 0x0FFFFFFF) | (int(isServerMessage != 0) << 28)

    @property
    def type(self):
        return (self.address >> 24) & 0x0F

    @type.setter
    def type(self, type):
        self.address = (self.address & 0xF0FFFFFF) | ((type & 0xF) << 24)

    @property
    def command(self):
        return LoxCanLegacyMessage.LoxCmd(self.data[0] & 0x7F)

    @command.setter
    def command(self, command):
        #if not isinstance(command, LoxCanLegacyMessage.LoxCmd):
        #    raise TypeError("command must be set to an LoxCmd")
        commandByte = int(command)
        if not self.isServerMessage:
            commandByte |= 0x80  # messages from a device have bit 7 always set in the command
        self.data[0] = commandByte

    @property
    def serial(self):
        return self.address & 0x0FFFFFFF

    @serial.setter
    def serial(self, serial):
        self.address = (self.address & 0xF0000000) | (serial & 0xFFFFFFF)

    @property
    def extensionNAT(self):
        raise AttributeError
        return 0

    @extensionNAT.setter
    def extensionNAT(self, extensionNAT):
        raise AttributeError

    @property
    def flags(self):
        raise AttributeError
        return 0

    @flags.setter
    def flags(self, flags):
        raise AttributeError

    @property
    def deviceNAT(self):
        raise AttributeError
        return 0

    @deviceNAT.setter
    def deviceNAT(self, deviceNAT):
        raise AttributeError

    @property
    def commandDescription(self):
        # Software update commands
        # Process:
        # - cmd 0x01 (3 times)
        # - send firmware data
        # - send CRCs
        # - send verification
        # - reboot extension
        if self.type == 0x1F:  # send firmware data to extension
            devTypeStr = getDeviceType((self.address >> 16) & 0xFF)
            if (self.address & 0xFFFF) == 0xFFFF:
                return 'Send update for "%s" END' % (devTypeStr)
            else:
                return 'Send update for "%s" packet #%d' % (devTypeStr, self.address & 0xFFFF)
        if self.isFragmentedPackage:
            return self.getFragmentedPackage(self.address, self.command, self.data[1:])

        if self.command == LoxCanLegacyMessage.LoxCmd.send_identify:  # used to request a 0x07 package, unmutes the extension
            return "Identify Request"
        if self.command == LoxCanLegacyMessage.LoxCmd.software_update or self.command == LoxCanLegacyMessage.LoxCmd.software_update_modules:  # Start Software Update process, Extension returns either ACK (update accepted) or NAK (update ignored)
            moduleStr = ""
            if self.val16 == 0xDEAD:
                moduleStr += " (forced)"
            if self.command == LoxCanLegacyMessage.LoxCmd.software_update_modules:
                moduleStr += " (update modules)"
            return "Update init%s, version:%s hardwareVersion:%d" % (moduleStr, LoxCanMessage.versionString(self.val32), self.data[1])
        elif self.command == LoxCanLegacyMessage.LoxCmd.BootExtension:  # Reboot after the update, also unmutes it
            if self.val16 == 0xDEAD:
                return "Forced reboot extension"
            else:
                return "Reboot extension, if different from new version"
        elif self.command == LoxCanLegacyMessage.LoxCmd.update_verify:  # Request update verification (send 0x54 if an CRC occured)
            moduleStr = ""
            if self.data[1] & 0x01:
                moduleStr += " (forced) "
            if self.data[1] & 0x02:
                moduleStr += " (modules) "
            return "Verify update%s version:%s pages:%d" % (moduleStr, LoxCanMessage.versionString(self.val32), self.val16)
        elif self.command == LoxCanLegacyMessage.LoxCmd.ACKCFG:
            return "Config Acknowledge 0x%04X version:%s" % (self.val16, LoxCanMessage.versionString(self.val32))
        elif self.command == LoxCanLegacyMessage.LoxCmd.BC_ACK:
            return "Update ACK"
        elif self.command == LoxCanLegacyMessage.LoxCmd.BC_NAK:
            return "Update NAK"
        elif self.command == LoxCanLegacyMessage.LoxCmd.RequestStart:  # send when the Miniserver is not reachable or after an "Identify Request" (not send when extension muted)
            return "Start version:%s configVersion:%d hardwareVersion:%d" % (LoxCanMessage.versionString(self.val32), self.val16, self.data[1])
        elif self.command == LoxCanLegacyMessage.LoxCmd.identity_led:  # fast LED blinking of an extension or device for identification
            return "Identify LED"
        elif self.command == LoxCanLegacyMessage.LoxCmd.alive_request:  # from an extension (every 360s + lower 6 bits of the serial number, DMX: every 400s), followed by temperature warning to be send back, if triggered
            if self.isServerMessage:
                return "Alive Request" # expects a 0x0f command with the current firmware version back
            else:
                return "Alive version:%s configVersion:%d hardwareVersion:%d" % (LoxCanMessage.versionString(self.val32), self.val16, self.data[1])
        elif self.command == LoxCanLegacyMessage.LoxCmd.identify_unknown_extensions:
            # the data seems to contain garbage (from the previous 0x87 package the server received)
            return "Identify unknown extensions"
        elif self.command == LoxCanLegacyMessage.LoxCmd.set_extension_offline:
            return "set extension offline"
        elif self.command == LoxCanLegacyMessage.LoxCmd.send_sync:  # send heartbeat onto the CAN bus, used to synchronize the LED blinking
            if self.address == 0 or self.address & 0x10000000:
                return "Send Sync Time: Difference to last sync: %dms" % (self.val32)
            else:  # send during a LED identify request
                return "Send Sync reply, version:%s" % (LoxCanMessage.versionString(self.val32))
        elif self.command == LoxCanLegacyMessage.LoxCmd.SendBlinkPos:  # forces a temperature warning to be send back, if triggered
            return "Set LED blink position #%d" % (self.val32)
        elif self.command == LoxCanLegacyMessage.LoxCmd.alive_reply:  # sending this with an old version will trigger an update
            #    if self.data[2]==0xF0: # IR Module (C485I)
            #      return 'Module %#08x online: %d' % (self.val32, self.val16)
            #    else:
            if self.isServerMessage:
                return "Alive Reply from Miniserver"
            else:
                return "Alive Reply from Extension, version %d" % (self.val32)
        elif self.command == LoxCanLegacyMessage.LoxCmd.AnalogInputSensitivity0 or self.command == LoxCanLegacyMessage.LoxCmd.AnalogInputSensitivity1:
            inputOffset = 0
            if self.command == LoxCanLegacyMessage.LoxCmd.AnalogInputSensitivity1:
                inputOffset = 2

            def minAvgStr(value):
                if value > 1000:
                    if value == 1001:
                        avgTime = 1 * 60 * 1000
                    elif value == 1002:
                        avgTime = 5 * 60 * 1000
                    elif value == 1003:
                        avgTime = 10 * 60 * 1000
                    elif value == 1004:
                        avgTime = 30 * 60 * 1000
                    elif value == 1005:
                        avgTime = 60 * 60 * 1000
                    elif value == 1006:
                        avgTime = 1 * 1000
                    elif value == 1007:
                        avgTime = 5 * 1000
                    elif value == 1008:
                        avgTime = 10 * 1000
                    elif value == 1009:
                        avgTime = 30 * 1000
                    else:
                        avgTime = 60 * 1000  # all other (illegal) cases
                    return "avgTime(%ds)" % (avgTime / 1000)
                else:
                    return "minChange(%.2f)" % (value * 0.01)

            def convertValueToMilliseconds(value):
                msValue = value >> 3
                expValue = value & 7
                if expValue == 0:
                    return msValue
                elif expValue == 1:
                    return msValue * 10  # 10ms
                elif expValue == 2:
                    return msValue * 100  # 100ms
                elif expValue == 3:
                    return msValue * 1000  # 1s
                elif expValue == 4:
                    return msValue * 10000  # 10s
                elif expValue == 5:
                    return msValue * 60000  # 1min
                elif expValue == 6:
                    return msValue * 600000  # 10min
                elif expValue == 7:
                    return msValue * 3600000  # 1hour
                pass

            analogInDelayValues0 = self.data[4] | (((self.data[1] >> 0) & 3) << 8)
            analogInDelayValues1 = self.data[6] | (((self.data[1] >> 4) & 3) << 8)
            analogInMinTimeChangeValues0 = convertValueToMilliseconds(self.data[5] | (((self.data[1] >> 2) & 3) << 8))
            analogInMinTimeChangeValues1 = convertValueToMilliseconds(self.data[7] | (((self.data[1] >> 6) & 3) << 8))
            return "Analog Input Sensitivity 0x%4.4X #%d:%s %.3fs #%d:%s %.3fs" % (
                self.val16,
                inputOffset + 1,
                minAvgStr(analogInDelayValues0),
                analogInMinTimeChangeValues0 * 0.001,
                inputOffset + 2,
                minAvgStr(analogInDelayValues1),
                analogInMinTimeChangeValues1 * 0.001,
            )
        #  elif self.command==LoxCanLegacyMessage.LoxCmd.debug_send_printf: # despite the message 'C1WR', this seems to be DMX related
        #    p1 = (self.data[6] << 8) + self.data[7]
        #    return 'Value C1WR Search (%4.4X:%08x)' % (p1,self.val32)
        elif self.command == LoxCanLegacyMessage.LoxCmd.debug_crashreport:
            if self.type == 0x05:  # 1Wire
                return "Value 1Wire device found (%02X:%04X:%08X:CRC)" % (self.data[2], self.val16, self.val32)
            elif self.type == 0x04:  # DMX
                return "Value DMX device found (%#08x)" % ((self.data[4] << 24) + (self.data[3] << 16) + (self.data[2] << 8) + self.data[1])
            elif self.type == 0x08:  # I485
                return "Value I485 device found (%#06x)" % (((self.data[3] << 16) + (self.data[2] << 8) + self.data[1]) | 0xF000)
        elif self.command == LoxCanLegacyMessage.LoxCmd.AirSendParam:
            # self.data[1] : 0 = set parameter (self.data[2]=parameter, self.data[3]=?)
            # self.data[1] : 1 = get parameter (# in self.data[3], value in self.data[4…7])
            # self.data[1] : 2 = air MAC statistics (self.data[2]=0, self.data[3]=0)
            # self.data[1] : 3 = air trace (self.data[2]=?, self.data[3]=0)
            # self.data[2] : parameter
            # self.data[3] : new value
            return "Send param to Air Extension cmd:%02x parameter:#%d %02x" % (self.data[1], self.data[2], self.data[3])
        elif self.command == LoxCanLegacyMessage.LoxCmd.SendDebug:
            return "Send debug flag %d" % self.data[1]
        elif self.command == LoxCanLegacyMessage.LoxCmd.RequestStatistics:  # Statistics only seem to exist for 1-Wire and Air, not DMX
            if self.data[1] == 0x00:
                return "Request statistics #%d" % self.data[2]
            elif self.data[1] == 0x01:
                return "Reset statistics"
            elif self.data[1] == 0x02:
                return "Reply request statistics"
            elif self.data[1] == 0x03:
                return "Last reply request statistics"
        elif self.command == LoxCanLegacyMessage.LoxCmd.OtauRxPacket:
            return "Send Otau RX Packet #%d : %s" % (self.data[1], binascii.hexlify(self.data[2:]))
        elif self.command == LoxCanLegacyMessage.LoxCmd.AnalogInputValue0:  # Extension
            val0 = self.data[4] | (((self.data[1] >> 0) & 3) << 8)
            val1 = self.data[5] | (((self.data[1] >> 2) & 3) << 8)
            val2 = self.data[6] | (((self.data[1] >> 4) & 3) << 8)
            val3 = self.data[7] | (((self.data[1] >> 6) & 3) << 8)
            return "Analog Inputs: #1:%.2fV #2:%.2fV #3:%.2fV #4:%.2fV" % (
                val0 * 0.01,
                val1 * 0.01,
                val2 * 0.01,
                val3 * 0.01,
            )
        elif self.command == LoxCanLegacyMessage.LoxCmd.EnoceanCmd:
            return "Enocean Config: BaseId %d Reset %d" % (self.val32, self.data[1])
        elif self.command == LoxCanLegacyMessage.LoxCmd.LearnEnocean:
            return "Learn Enocean %s" % (binascii.hexlify(self.data))
        elif (
            self.command == LoxCanLegacyMessage.LoxCmd.send_sync_package
        ):  # Date/Time Sync Packet
            return "Send Sync packet. %s" % self.dateTimeString
        elif self.command == LoxCanLegacyMessage.LoxCmd.AnalogOutputValue0:
            val0 = self.data[4] | (((self.data[1] >> 0) & 3) << 8)
            val1 = self.data[5] | (((self.data[1] >> 2) & 3) << 8)
            val2 = self.data[6] | (((self.data[1] >> 4) & 3) << 8)
            val3 = self.data[7] | (((self.data[1] >> 6) & 3) << 8)
            return "Analog Outputs: #1:%.2fV #2:%.2fV #3:%.2fV #4:%.2fV" % (val0 * 0.01, val1 * 0.01, val2 * 0.01, val3 * 0.01)
        elif self.command == LoxCanLegacyMessage.LoxCmd.AnalogOutputInit:

            def aOutInitStr(val):
                if val == 0:
                    return "Jump"
                elif val == 21:
                    return "1%"
                elif val == 22:
                    return "2%"
                else:
                    return "%d%%" % (val * 5)

            return "Analog Output Init #1:%s/%s #2:%s/%s #3:%s/%s #4:%s/%s" % (
                ((self.data[2] >> 0) & 0xF) != 0x04,
                aOutInitStr(self.data[4]),
                ((self.data[2] >> 4) & 0xF) != 0x04,
                aOutInitStr(self.data[5]),
                ((self.data[3] >> 0) & 0xF) != 0x04,
                aOutInitStr(self.data[6]),
                ((self.data[3] >> 4) & 0xF) != 0x04,
                aOutInitStr(self.data[7]),
            )
        elif self.command == LoxCanLegacyMessage.LoxCmd.SendRetryPage:
            return "Send retry page address:%06X 4 bytes:%s" % (self.data[1] + (self.data[2] << 8) + (self.data[3] << 16), binascii.hexlify(self.data[4:8]))
        elif self.command == LoxCanLegacyMessage.LoxCmd.SendLogLevel:
            return "Set log level %d" % (self.val32)
        #  elif self.command==LoxCanLegacyMessage.LoxCmd.CheckCfgCrc: # DMX-only or just checksum mismatch?
        #    return 'Value Checksum (%08x)' % (self.val32)
        elif self.command == LoxCanLegacyMessage.LoxCmd.ParkExtension:  # used for unknown extension
            return "Park unused extension"
        elif self.command == LoxCanLegacyMessage.LoxCmd.LinkDiagnosisRx:  # (not send when extension muted)
            return "Reply CAN Diagnostic packet: Err %d, REC %d, TEC %d" % (self.val32, self.data[3], self.data[2])
        # Loxone Link Diagnose – as long as the dialog is open, the following messages are on the bus
        elif self.command == LoxCanLegacyMessage.LoxCmd.request_CAN_diagnosis_packet:
            return "Request CAN Diagnostic packet"
        elif self.command == LoxCanLegacyMessage.LoxCmd.DigitalInputSensitivity0 or self.command == LoxCanLegacyMessage.LoxCmd.DigitalInputSensitivity1 or self.command == LoxCanLegacyMessage.LoxCmd.DigitalInputSensitivity2 or self.command == LoxCanLegacyMessage.LoxCmd.DigitalInputSensitivity3:

            def digitalInputSensitivity(val, sb):
                mode = val & 7
                val = (val + sb * 256) >> 3
                if mode <= 4:  # power of 10 with 0.001 as the minimum value
                    return val * pow(10, -3 + mode)
                elif mode == 5:  # seconds
                    return 60 * val
                elif mode == 6:  # 10 seconds
                    return 60 * 10 * val
                elif mode == 7:  # hours in ms
                    return 60 * 60 * 1000 * val

            def digitalInputSensitivityStr(val, sb):
                if (val + sb * 256) == 0x3FF:
                    return "Frequencycounter"
                else:
                    return "%.3fs" % (digitalInputSensitivity(val, sb))

            return "Digital Input Sensitivity #%d 0x%4.4X %s %s %s %s" % (
                self.command - LoxCanLegacyMessage.LoxCmd.DigitalInputSensitivity0,
                self.val16,
                digitalInputSensitivityStr(self.data[4], self.data[1] & 3),
                digitalInputSensitivityStr(self.data[5], (self.data[1] >> 2) & 3),
                digitalInputSensitivityStr(self.data[6], (self.data[1] >> 4) & 3),
                digitalInputSensitivityStr(self.data[7], (self.data[1] >> 6) & 3),
            )
        if self.command == LoxCanLegacyMessage.LoxCmd.SendFragmented:  # Fragmented package - up to 1530 bytes large (6 bytes * 255 packages)
            if self.data[1] == 0x00:  # header
                self.fragmentCommand = self.data[2]
                # self.data[3]==0x00
                self.fragmentSize = self.val32 & 0xFFFF
                self.fragmentCRC = (self.val32 >> 16) & 0xFFFF  # actually a SUM16 over all bytes, not a CRC
                self.fragmentData = []
                return "Fragmented package cmd:%02x %d bytes, checksum: %04x" % (self.fragmentCommand, self.fragmentSize, self.fragmentCRC)
            else:
                # self.data[1]==package index
                if self.fragmentData:
                    self.fragmentData += self.data[2:]
                else:
                    self.fragmentData = self.data[2:]
                if len(self.fragmentData) >= self.fragmentSize and self.fragmentSize > 0:
                    self.fragmentData = self.fragmentData[:self.fragmentSize]
                    retStr = self.getFragmentedPackage(self.address, self.fragmentCommand, self.fragmentData)
                    self.fragmentCommand = 0
                    self.fragmentSize = 0
                    self.fragmentCRC = 0
                    self.fragmentData = []
                    return retStr
        elif self.command == LoxCanLegacyMessage.LoxCmd.SendFragmentedLargeDataData:  # Large fragmented package header (less than 64kb package size)
            self.fragmentCommand = self.data[2]
            # data[3]==0x00
            self.fragmentSize = self.val32 & 0xFFFF
            self.fragmentCRC = (self.val32 >> 16) & 0xFFFF  # actually a SUM16 over all bytes, not a CRC
            retStr = "Large fragmented package cmd:%02x %d bytes, checksum: %06x" % (self.fragmentCommand, self.fragmentSize, self.fragmentCRC)
        elif self.command == LoxCanLegacyMessage.LoxCmd.SendFragmentedLargeDataStart:  # Large fragmented package
            if self.fragmentData:
                self.fragmentData += self.data
            else:
                self.fragmentData = self.data
            if len(self.fragmentData) >= self.fragmentSize:
                retStr = self.getFragmentedPackage(self.address, self.fragmentCommand, binascii.hexlify(self.fragmentData))
                self.fragmentCommand = 0
                self.fragmentSize = 0
                self.fragmentCRC = 0
                self.fragmentData = []
                return retStr
        elif self.command == LoxCanLegacyMessage.LoxCmd.ValueFromDigInputs:  # (Extension, Dimmer Extension)
            return "Digital Inputs 0x%04x" % (self.val32)
        elif self.command == LoxCanLegacyMessage.LoxCmd.ValueFrequency:  # Frequency report (Extension)
            return "Frequency #%d:%dHz #%d:%dHz #%d:%dHz #%d:%dHz" % (
                (self.data[5] & 0x0F) + 1,
                self.data[1],
                ((self.data[5] >> 4) & 0x0F) + 1,
                self.data[2],
                (self.data[6] & 0x0F) + 1,
                self.data[3],
                ((self.data[6] >> 4) & 0x0F) + 1,
                self.data[4],
            )
        elif self.command == LoxCanLegacyMessage.LoxCmd.command_send_temperature:  # Overheating temperature (Extension, Relay Extension, Dimmer Extension) (not send when extension muted)
            hardwareVersion = 0  # hardwareVersion > 1 supports returning the temperature in two formats
            shutDownStr = "no"
            if self.data[3]:
                shutDownStr = "yes"
            if self.data[2] == 1 or hardwareVersion <= 1:  # e.g. the Loxone Extension doesn't set self.data[1] and self.data[2], so a version test is needed
                tempC = (1475 - (self.val32 * 2245 / 1024)) * 0.1
            else:
                tempC = self.val32 * 0.1
            return "System Temperature %.1fC, over temperature shutdown:%s" % (tempC, shutDownStr)
        elif self.command == LoxCanLegacyMessage.LoxCmd.SendPageCrc:  # Send CRCs over all pages (1024 bytes per page) to the device to allow verification
            # self.data[1] = 0x00
            return "Update CRC Error page #%d, pageCRC:%#08x" % (self.data[2], self.val32)
        elif self.command == LoxCanLegacyMessage.LoxCmd.BootAirBase:
            return "Reboot air base extension (forced:%d)" % (self.data[1])
        elif self.command == LoxCanLegacyMessage.LoxCmd.MuteExtension:
            return "Mute extension"
        elif self.command == LoxCanLegacyMessage.LoxCmd.set_DigOutputs:
            return "Digital Outputs 0x%04x" % (self.val32)
        # 1Wire extension:
        #  elif self.command==LoxCanLegacyMessage.LoxCmd.iButtonInit:
        #    return 'Value C1WR iButton Init, version %s' % (LoxCanMessage.versionString(self.val32))
        elif self.command == LoxCanLegacyMessage.LoxCmd.SetMonitor:
            if self.data[2] == 0x00 and self.data[3] == 0xFF and self.data[4] == 0x00:
                return "Search for devices"
            if self.data[2] == 0x01:
                if self.data[1] == 0x00:
                    return "Stop Monitor for devices start"
                else:
                    return "Start Monitor for devices start"
        #  elif self.command==LoxCanLegacyMessage.LoxCmd.C1WR_SEARCH:
        #    return 'Value C1WR Search Last (%2.2X.%2.2X%2.2X%2.2X%2.2X%2.2X%2.2X.crc)' % (self.data[1], self.data[2], self.data[3], self.data[4], self.data[5], self.data[6], self.data[7])
        #  elif self.command==LoxCanLegacyMessage.LoxCmd.AnalogValue1Wire:
        #    return 'Value 1Wire Sensor #%d Temperature: %.4f' % (self.data[1], self.data[2] + self.data[3] / 16.0)
        elif self.command == LoxCanLegacyMessage.LoxCmd.LearnIR:
            if self.data[1]:
                return "Learn IR Extension Module %#08x" % (self.val32)
            else:
                return "Learn IR Extension Module %#08x off" % (self.val32)
        elif self.command == LoxCanLegacyMessage.LoxCmd.ChangeDaliAddresse:
            return "Dali change address from %d to %d" % (self.data[1], self.data[2])
        elif self.command == 0x74:
            if self.data[3] == 0xFF:
                val = (self.data[2] << 8) + self.data[1]
                if val:
                    return "DMX start learning"
                else:
                    return "DMX stop learning"
        elif self.command == LoxCanLegacyMessage.LoxCmd.ValueChecksum:
            return "Set Config Checksum %s" % (binascii.hexlify(self.data))
        elif self.command == LoxCanLegacyMessage.LoxCmd.RequestChecksum:
            return " %s" % (binascii.hexlify(self.data))
        elif self.command == LoxCanLegacyMessage.LoxCmd.Arrive1Wire:
            return ("Value 1Wire Sensor %2.2X.%2.2X%2.2X%2.2X%2.2X%2.2X%2.2X.crc Arrive" % (self.data[1], self.data[2], self.data[3], self.data[4], self.data[5], self.data[6], self.data[7]))
        elif self.command == LoxCanLegacyMessage.LoxCmd.Depart1Wire:
            return ("Value 1Wire Sensor %2.2X.%2.2X%2.2X%2.2X%2.2X%2.2X%2.2X.crc Depart" % (self.data[1], self.data[2], self.data[3], self.data[4], self.data[5], self.data[6], self.data[7]))
        else:
            return "???"

class LoxCanNATMessage(LoxCanMessage):
    class xCanID_t(IntEnum):
        # starting from 0x00: general commands
        Version_Request = 0x1
        Start = 0x2
        Device_Version = 0x3
        Config_Equal = 0x4
        Ping = 0x5
        Pong = 0x6
        Park_Devices = 0x7
        Alive_Packet = 0x8
        Sync_Packet = 0xC
        Identify_LED = 0x10
        Send_Config_Data = 0x11
        WebServicesText = 0x12
        DeviceLog = 0x13
        AlarmMode = 0x14
        InternormMonitorData = 0x15
        CAN_Diagnosis_Reply = 0x16
        CAN_Diagnosis_Request = 0x17
        CAN_Error_Reply = 0x18
        CAN_Error_Request = 0x19
        Tree_Shortcut = 0x1A
        Tree_Shortcut_Test = 0x1B
        KNX_Send_Telegram = 0x1C
        KNX_Group_Address_Config = 0x1D
        GroupIdentify = 0x1E # 16-bit:array element count, 16-bit: flag, 32-bit: ???, 6-byte array:[32-bit:serial, 8-bit:index , 8-bit:filler]
        Tree_LinkSnifferPacker = 0x1F

        # starting from 0x90: getter/setter values commands
        Digital_Value = 0x80
        Analog_Value = 0x81
        Internorm_Digital_Value = 0x82
        Internorm_Analog_Value = 0x83
        RGBW = 0x84
        Frequency = 0x85
        AccessCodeInput = 0x86
        Keypad_NfcId = 0x87
        Composite_RGBW = 0x88
        TreeKeypad_Send = 0x89
        Composite_White = 0x8A
        Composite_RGBW_magic = 0x8A
        TreeInternormDataPacket = 0x8D

        # starting from 0x90: encrypted commands
        CryptoValueDigital = 0x90  # after decryption maps to Digital_Value
        CryptoValueAnalog = 0x91  # after decryption maps to Analog_Value
        CryptoValueAccessCodeInput = 0x92  # after decryption maps to AccessCodeInput
        CryptoNfcId = 0x93
        CryptoKeyPacket = 0x94
        CryptoDeviceIdReply = 0x98
        CryptoDeviceIdRequest = 0x99
        CryptoChallengeRollingKeyReply = 0x9A
        CryptoChallengeRollingKeyRequest = 0x9B
        CryptoChallengeRequest = 0x9C # needed starting version 10.3.11.10
        CryptoChallengeReply = 0x9D

        Update_New = 0xEF

        # starting from 0xF0: NAT assignments, large packages, update, etc
        Fragment_Start = 0xF0
        Fragment_Data = 0xF1
        Update_Reply = 0xF3
        Identify_Unknown_Extensions = 0xF4
        KNX_Monitor = 0xF5
        Internorm_Learn_Feedback = 0xFA
        Search_Devices = 0xFB
        Search_Reply = 0xFC
        NAT_Offer = 0xFD
        NAT_Index_Request = 0xFE

    class Reason(IntEnum):
        MiniserverStart = 0x1
        Pairing = 0x2
        AliveRequested = 0x3
        Reconnected = 0x4
        Alive_Packet = 0x5
        Reconnect_Broadcast = 0x6
        PowerOnReset = 0x20
        StandbyReset = 0x21
        WatchdogReset = 0x22
        SoftwareReset = 0x23
        PinReset = 0x24
        WindowWatchdogReset = 0x25
        LowPowerReset = 0x26

    @classmethod
    def reasonString(cls, reason):
        if reason == LoxCanNATMessage.Reason.MiniserverStart:
            return "Miniserver start"
        elif reason == LoxCanNATMessage.Reason.Pairing:
            return "pairing"
        elif reason == LoxCanNATMessage.Reason.AliveRequested:
            return "alive requested"
        elif reason == LoxCanNATMessage.Reason.Reconnected:
            return "reconnect"
        elif reason == LoxCanNATMessage.Reason.Alive_Packet:
            return "alive packet"
        elif reason == LoxCanNATMessage.Reason.Reconnect_Broadcast:
            return "reconnect (broadcast)"
        elif reason == LoxCanNATMessage.Reason.PowerOnReset:
            return "power on reset"
        elif reason == LoxCanNATMessage.Reason.StandbyReset:
            return "standby reset"
        elif reason == LoxCanNATMessage.Reason.WatchdogReset:
            return "watchdog reset"
        elif reason == LoxCanNATMessage.Reason.SoftwareReset:
            return "software reset"
        elif reason == LoxCanNATMessage.Reason.PinReset:
            return "pin reset"
        elif reason == LoxCanNATMessage.Reason.WindowWatchdogReset:
            return "window watchdog reset"
        elif reason == LoxCanNATMessage.Reason.LowPowerReset:
            return "low power reset"
        return "unknown"

    def __init__(self, isTreeMessage=False):
        LoxCanMessage.__init__(self)
        self.isTreeMessage = isTreeMessage

    def __repr__(self):
        if self.isServerMessage:
            typeStr = "S"
        else:
            typeStr = "E"
        if self.type == 0x10:  # Loxone Link
            natStr = "NAT "
        elif self.type == 0x11:  # Tree Bus
            natStr = "TREE"
        else:
            natStr = "??%02x" % self.type
        return "<%s   %s%d:E%02x D%02x %02x %s %s>" % (
            natStr,
            typeStr,
            self.flags,
            self.extensionNAT,
            self.deviceNAT,
            int(self.command),
            binascii.hexlify(self.data[1:]),
            self.commandDescription,
        )

    @classmethod
    def addMessage(cls, message):
        fragment = LoxMessageFragment.fragmentForMessage(message)
        if message.command == LoxCanNATMessage.xCanID_t.Fragment_Start:
            fragment.Command = LoxCanNATMessage.xCanID_t(message.data[1])
            fragment.Size = message.val16
            fragment.Checksum = message.val32
        elif message.command == LoxCanNATMessage.xCanID_t.Fragment_Data:
            if not fragment.Command:  # start command missing
                return
            if fragment.Data:
                fragment.Data += message.data[1:]
            else:
                fragment.Data = message.data[1:]
            if len(fragment.Data) >= fragment.Size:
                fragment.Data = fragment.Data[: fragment.Size]
                if fragment.Checksum != stm32_crc32(fragment.Data):
                    print("# CRC ERROR %lx!=%lx %s" % (fragment.Checksum, stm32_crc32(fragment.Data), binascii.hexlify(fragment.Data)))
                else:
                    # add the complete command to the message
                    message.command = fragment.Command
                    message.data = chr(message.deviceNAT) + fragment.Data
                fragment.Command = None
                fragment.Size = None
                fragment.Checksum = None
                fragment.Data = None

    @property
    def serial(self):
        raise AttributeError
        return 0

    @serial.setter
    def serial(self, serial):
        raise AttributeError

    @property
    def command(self):
        return LoxCanNATMessage.xCanID_t(self.address & 0xFF)

    @command.setter
    def command(self, command):
        if not isinstance(command, LoxCanNATMessage.xCanID_t):
            raise TypeError("command must be set to an xCanID_t")
        self.address = (self.address & 0xFFFFFF00) | (int(command) & 0xFF)

    @property
    def extensionNAT(self):
        return (self.address >> 12) & 0xFF

    @extensionNAT.setter
    def extensionNAT(self, extensionNAT):
        self.address = (self.address & 0xFFF00FFF) | ((extensionNAT & 0xFF) << 12)

    @property
    def flags(self):
        return (self.address >> 20) & 0xF

    @flags.setter
    def flags(self, flags):
        self.address = (self.address & 0xFF0FFFFF) | ((flags & 0xF) << 20)

    @property
    def isServerMessage(self):
        return ((self.address >> 22) & 1) != 0

    @isServerMessage.setter
    def isServerMessage(self, isServerMessage):
        flags = 0
        if isServerMessage:
            flags = 6  # two bits in the flags are set to id packages from the server
        self.address = (self.address & 0xFF1FFFFF) | (flags << 20)

    @property
    def isTreeMessage(self):
        return self.type == 0x11

    @isTreeMessage.setter
    def isTreeMessage(self, isTreeMessage):
        if isTreeMessage:
            self.type = 0x11
        else:
            self.type = 0x10

    @property
    def deviceNAT(self):
        return self.data[0]

    @deviceNAT.setter
    def deviceNAT(self, deviceNAT):
        self.data[0] = deviceNAT

    @property
    def commandDescription(self):
        if self.command == LoxCanNATMessage.xCanID_t.Version_Request:
            return "Version request to %s" % LoxCanMessage.serialString(self.val32)
        elif self.command == LoxCanNATMessage.xCanID_t.Start or self.command == LoxCanNATMessage.xCanID_t.Device_Version:  # (fragmented command)
            if self.command == LoxCanNATMessage.xCanID_t.Start:
                cmdStr = "Start"
            elif self.command == LoxCanNATMessage.xCanID_t.Device_Version:
                cmdStr = "Version"
            appVersion, unknown_info, config_crc, serial, startReason, hwType, HWVersion = struct.unpack("<LLLLBHB", self.data[1:])
            return (
                '%s packet: appVersion:%s settingsCRC:%08x serial:%s (start reason:"%s") hwType:"%s" hwVersion:%d'
                % (
                    cmdStr,
                    LoxCanMessage.versionString(appVersion),
                    config_crc,
                    LoxCanMessage.serialString(serial),
                    LoxCanNATMessage.reasonString(startReason),
                    getDeviceSubType(hwType),
                    HWVersion,
                )
            )
        elif self.command == LoxCanNATMessage.xCanID_t.Config_Equal:
            return "Config Equal"
        elif self.command == LoxCanNATMessage.xCanID_t.Ping:
            return "Ping"
        elif self.command == LoxCanNATMessage.xCanID_t.Pong:
            return "Pong"
        elif self.command == LoxCanNATMessage.xCanID_t.Park_Devices:
            return "Park Devices"
        elif self.command == LoxCanNATMessage.xCanID_t.Alive_Packet:
            return ('Alive packet to tree device, NAT index:%2.2x, configCRC:%08x, reason:"%s"' % (self.deviceNAT, self.val32, LoxCanNATMessage.reasonString(self.data[1])))
        elif self.command == LoxCanNATMessage.xCanID_t.Sync_Packet:
            return "Send Sync packet. %s" % self.dateTimeString
        elif self.command == LoxCanNATMessage.xCanID_t.Identify_LED:
            return "Identify Led %2.2X/%2.2X Serial:%s" % (self.data[1], self.data[2], LoxCanMessage.serialString(self.val32))
        elif self.command == LoxCanNATMessage.xCanID_t.Send_Config_Data:  # (fragmented command)
            return "Send config data: %d bytes :%s" % (self.data[1], binascii.hexlify(self.data[2:]))
        elif self.command == LoxCanNATMessage.xCanID_t.WebServicesText:  # Web Services Text (fragmented command)
            packageSize = self.data[2]
            if packageSize > 1:  # Zero-Byte at the end of the string is ignored anyway
                printfStr = self.data[3:packageSize + 3 - 1].decode()
                return 'WebServiceRequest: "%s"' % printfStr
            else:
                return 'WebServiceRequest: ""'
        elif self.command == LoxCanNATMessage.xCanID_t.DeviceLog:  # Device Log Text (fragmented command)
            packageSize = self.data[2]
            if packageSize > 1:  # Zero-Byte at the end of the string is ignored anyway
                return 'Device Log: "%s"' % (self.data[3:packageSize + 3 - 1].decode())
            else:
                return 'Device Log: ""'
        elif self.command == LoxCanNATMessage.xCanID_t.CAN_Diagnosis_Reply:
            if self.val16 == 0x01:
                return ("Reply CAN Diagnostic packet Tree Left: Err %d, REC %d, TEC %d" % (self.val32, self.data[2], self.data[3]))
            elif self.val16 == 0x02:
                return ("Reply CAN Diagnostic packet Tree Right: Err %d, REC %d, TEC %d" % (self.val32, self.data[2], self.data[3]))
            else:
                return "Reply CAN Diagnostic packet: Err %d, REC %d, TEC %d" % (self.val32, self.data[2], self.data[3])
        elif self.command == LoxCanNATMessage.xCanID_t.CAN_Diagnosis_Request:
            if self.val16 == 0x01:
                return "Request CAN Diagnostic Tree Left"
            elif self.val16 == 0x02:
                return "Request CAN Diagnostic Tree Right"
            else:
                return "Request CAN Diagnostic"
        elif self.command == LoxCanNATMessage.xCanID_t.CAN_Error_Reply:
            if self.val16 == 0x01:
                return "CAN error packet Tree Left: Err %d, REC %d, TEC %d" % (self.val32, self.data[2], self.data[3])
            elif self.val16 == 0x02:
                return "CAN error packet Tree Right: Err %d, REC %d, TEC %d" % (self.val32, self.data[2], self.data[3])
            else:
                return "CAN error packet: Err %d, REC %d, TEC %d" % (self.val32, self.data[2], self.data[3])
        elif self.command == LoxCanNATMessage.xCanID_t.CAN_Error_Request:
            if self.val16 == 0x01:
                return "Request CAN error Tree Left"
            elif self.val16 == 0x02:
                return "Request CAN error Tree Right"
            else:
                return "Request CAN error"
        elif self.command == LoxCanNATMessage.xCanID_t.Tree_Shortcut:
            if self.data[1] & 0x40:
                fromDev = "left"
            else:
                fromDev = "right"
            return "Tree Shortcut from 0x%2.2X (%s branch)" % (self.data[1], fromDev)
        elif self.command == LoxCanNATMessage.xCanID_t.Tree_Shortcut_Test:
            if self.data[1] & 0x40:
                fromDev = "left"
            else:
                fromDev = "right"
            if self.data[2] & 0x40:
                toDev = "left"
            else:
                toDev = "right"
            return ("Tree Shortcut Test from 0x%2.2X (%s branch). Sender Tree Extension: 0x%2.2X:%s (%s branch)" % (self.data[1], fromDev, self.data[2], LoxCanMessage.serialString(self.val32), toDev))
        #    elif self.command==LoxCanNATMessage.xCanID_t.KNX_Send_Telegram: # only used by the KNX extension
        #        return '?KNX Send Telegram'
        #    elif self.command==LoxCanNATMessage.xCanID_t.KNX_Group_Address_Config: # only used by the KNX extension
        #        return '?KNX Group Address Config'

        elif self.command == LoxCanNATMessage.xCanID_t.Digital_Value:
            return "Digital Value %08x" % self.val32
        elif self.command == LoxCanNATMessage.xCanID_t.Analog_Value:
            val = self.val32
            if self.val16 & 0x10:
                val = val * 1.0  # signed value
            else:
                val = val * 1.0  # unsigned value
            factor = self.val16 & 0x0F
            if factor == 0:
                val *= 1.0
            elif factor == 1:
                val *= 1000.0
            elif factor == 2:
                val *= 1000000.0
            elif factor == 3:
                val *= 1000000000.0
            elif factor == 5:
                val /= 1000.0
            elif factor == 6:
                val /= 1000000.0
            elif factor == 7:
                val /= 1000000000.0
            elif factor == 8:
                val /= 10.0
            return "Analog Value #%d: %f" % (self.data[1], val)
        elif self.command == LoxCanNATMessage.xCanID_t.RGBW:
            return "RGBW R:%d G:%d B:%d W:%d" % (self.data[4], self.data[5], self.data[6], self.data[7])
        elif self.command == LoxCanNATMessage.xCanID_t.Frequency:
            return "Frequency #%d: %ldHz" % (self.data[1], self.val32)
        elif self.command == LoxCanNATMessage.xCanID_t.Composite_RGBW:
            fadingTime = self.val16
            if (fadingTime & 0x4000) == 0x4000:
                fadingTime = (fadingTime & 0x3FFF) * 1.0
            else:  # 0x8000 or 0x0000
                fadingTime = (fadingTime & 0x3FFF) * 0.1
            return "Composite RGBW R:%d G:%d B:%d W:%d FadingTime:%.1fs" % (self.data[4],self.data[5],self.data[6],self.data[7],fadingTime)
        elif self.command == LoxCanNATMessage.xCanID_t.Composite_White:  # (fragmented command)
            return "Composite White Values:%d,%d,%d,%d FadingTimes:%d,%d,%d,%d" % (self.data[2],self.data[3],self.data[4],self.data[5],self.data[6] + (self.data[7] << 8),self.data[8] + (self.data[9] << 8),self.data[10] + (self.data[11] << 8),self.data[12] + (self.data[13] << 8))
        elif self.command == LoxCanNATMessage.xCanID_t.Composite_RGBW_magic:  # (fragmented command)
            return "Composite RGBW Magic R:%d G:%d B:%d W:%d FadingTime:%.1fs magic:%08x" % (self.data[4],self.data[5],self.data[6],self.data[7],fadingTime,self.data[8] + (self.data[9] << 8) + (self.data[10] << 16) + (self.data[11] << 24))

        elif self.command == LoxCanNATMessage.xCanID_t.Fragment_Start:  # (fragmented command)
            return "Fragment Header command:%s size:%d fragmentCRC:%08x" % (LoxCanNATMessage.xCanID_t(self.data[1]),self.val16,self.val32)
        elif self.command == LoxCanNATMessage.xCanID_t.Fragment_Data:  # (fragmented command)
            return "Fragment Data %s" % (binascii.hexlify(self.data[1:]))
        elif self.command == LoxCanNATMessage.xCanID_t.Update_Reply:  # (fragmented command)
            return "Update Reply %s" % (binascii.hexlify(self.data))
        elif self.command == LoxCanNATMessage.xCanID_t.Identify_Unknown_Extensions:  # always a NAT multicast
            return "Identify Unknown Extensions"
        elif self.command == LoxCanNATMessage.xCanID_t.KNX_Monitor:  # KNX Extension only
            if self.val16 == 0x00:
                monitorState = "OFF"
            else:
                monitorState = "ON"
            return "send monitor %s to KNX extension" % monitorState
        elif self.command == LoxCanNATMessage.xCanID_t.Search_Devices:  # always a NAT multicast
            return "Search Devices"
        elif self.command == LoxCanNATMessage.xCanID_t.Search_Reply:
            if self.val16 & 0x8000:
                branch = "right"
                if self.data[1] & 0x40:
                    branch = "left"
                return ('NAT search answer from tree device %s (%s branch) (device type:"%s")' % (LoxCanMessage.serialString(self.val32), branch, getDeviceSubType(self.val16)))
            else:
                return 'NAT search answer from tree device %s (device type:"%s")' % (LoxCanMessage.serialString(self.val32), getDeviceSubType(self.val16))
        elif self.command == LoxCanNATMessage.xCanID_t.NAT_Offer:
            parkStr = ""
            if self.data[2] & 1:
                parkStr = ", park extension"
            return "Send NAT offer to Extension %s newNAT:%2.2x%s" % (LoxCanMessage.serialString(self.val32),self.data[1],parkStr)
        elif self.command == LoxCanNATMessage.xCanID_t.NAT_Index_Request:
            if self.val16 & 0x8000:
                branch = "right"
                if self.data[1] & 0x40:
                    branch = "left"
                return ('NAT index request from tree device %s (%s branch) (device type:"%s")' % (LoxCanMessage.serialString(self.val32),branch,getDeviceSubType(self.val16)))
            else:
                return 'NAT index request from tree device %s (device type:"%s")' % (LoxCanMessage.serialString(self.val32),getDeviceSubType(self.val16))
        else:
            return "Command:%s" % (self.command)


###############################################################################
# CAN bus sending/receiving
###############################################################################
# USBtin from https://www.fischl.de/usbtin/
class CANBus_USBtin(object):
    def __init__(self, isLoxoneTree=False):
        self.serial = serial.Serial("/dev/cu.usbmodemA02172A81", baudrate=115200)
        self.isLoxoneTree = isLoxoneTree
        if self.isLoxoneTree:
            print("- TREE BUS")
            self.serial.write("S2\r")  # Set baudrate: 50kHz
        else:
            print("- LOXONE LINK")
            self.serial.write("S4\r")  # Set baudrate: 125kHz
        self.serial.write("O\r")  # Open CAN channel
        # self.serial.write('v\r') # Get firmware version (for testing)

    def __del__(self):
        self.serial.close()

    def send(self, message):
        s = "T%08x8%s\r" % (message.address, binascii.hexlify(message.data))
        #print('Sent %08x : %s' % (message.address, binascii.hexlify(message.data)))
        self.serial.write(s)
        time.sleep(0.010)  # to avoid overflows after 4 packages send quickly in a row

    def readline(self):
        line = bytearray()
        timeoutMsTime = int(round(time.time() * 1000)) + 100  # 100ms timeout
        while True:
            currentMsTime = int(round(time.time() * 1000))
            if currentMsTime > timeoutMsTime:
                break
            if self.serial.inWaiting():
                c = self.serial.read(1)
                if c:
                    line += c
                    if line[-1:] == b"\r":
                        break
                else:
                    break
        return bytes(line)

    def receive(self):
        if not self.serial.inWaiting():
            return None
        buffer = self.readline().rstrip()
        if len(buffer) != 26 or buffer[0] != "T" or buffer[9] != "8":
            # print '$ %s' % buffer
            return None
        address = int(buffer[1:9], 16)
        if ((address >> 24) & 0x1F) == 0x10 or self.isLoxoneTree:
            message = LoxCanNATMessage()
        else:
            message = LoxCanLegacyMessage()
        message.address = address
        message.data = bytearray.fromhex(buffer[10:])
        return message


###############################################################################
# Emulate Legacy Extensions - Base Class
###############################################################################
class LoxBusLegacyExtension(object):
    def __init__(self, canbus, serial, hardwareVersion, version):
        self.canbus = canbus
        self.serial = serial
        self.hardwareVersion = hardwareVersion
        self.version = version
        encryptedAESKey = binascii.unhexlify(LoxoneCryptoEncryptedAESKey)
        self.CryptoCanAlgoKey = [DEKHash(encryptedAESKey), JSHash(encryptedAESKey), DJBHash(encryptedAESKey), RSHash(encryptedAESKey)]
        encryptedAESIV = binascii.unhexlify(LoxoneCryptoEncryptedAESIV)
        self.CryptoCanAlgoIV = [DEKHash(encryptedAESIV), JSHash(encryptedAESIV), DJBHash(encryptedAESIV), RSHash(encryptedAESIV)]
        self.reset()

    def reset(self):
        # initialize all runtime variables, just like after a reset
        # we do not reinitialize the configuration, which should be in FLASH memory anyway
        self.isDeviceIdentified = False
        self.isMuted = False
        self.nextStatusMessageTime = 0
        self.forceStartMessage = True
        self.firmwareUpdateActive = False
        self.firmwareUpdateData = bytearray()
        self.firmwareUpdateCRCs = []
        self.firmwareNewVersion = 0

    def sendCommandWithValues(self, command, val8, val16, val32):
        if self.isMuted:
            return
        msg = LoxCanLegacyMessage()
        msg.serial = self.serial
        msg.isServerMessage = False
        msg.command = command
        msg.data[1] = val8
        msg.val16 = val16
        msg.val32 = val32
        self.canbus.send(msg)
        msg.addMessage(msg)

    def sendCommandWithVersion(self, command):
        msg = LoxCanLegacyMessage()
        msg.serial = self.serial
        msg.isServerMessage = False
        msg.command = command
        msg.val32 = self.version
        self.canbus.send(msg)
        msg.addMessage(msg)

    def CryptoCanAlgo_DecryptInitPacket(self, data, serial):
        # pre-calculate the AES key/iv based on constant data and the serial number
        aesKey = [0] * 4
        aesIV = [0] * 4
        for i in range(0, 4):
            aesKey[i] = (~serial ^ self.CryptoCanAlgoKey[i]) & 0xFFFFFFFF
            aesIV[i] = (serial ^ self.CryptoCanAlgoIV[i]) & 0xFFFFFFFF
        key = struct.pack("<LLLL", aesKey[0], aesKey[1], aesKey[2], aesKey[3])
        iv = struct.pack("<LLLL", aesIV[0], aesIV[1], aesIV[2], aesIV[3])
        decipher = Crypto.Cipher.AES.new(key, Crypto.Cipher.AES.MODE_CBC, iv)
        return decipher.decrypt(bytes(data))

    def CryptoCanAlgo_DecryptDataPacket(self, data, key, iv):
        key = struct.pack("<LLLL", iv ^ key[0], iv ^ key[1], iv ^ key[2], iv ^ key[3])
        iv = struct.pack("<LLLL", iv, iv, iv, iv)
        decipher = Crypto.Cipher.AES.new(key, Crypto.Cipher.AES.MODE_CBC, iv)
        return decipher.decrypt(bytes(data))

    def CryptoCanAlgo_EncryptDataPacket(self, data, key, iv):
        key = struct.pack("<LLLL", iv ^ key[0], iv ^ key[1], iv ^ key[2], iv ^ key[3])
        iv = struct.pack("<LLLL", iv, iv, iv, iv)
        decipher = Crypto.Cipher.AES.new(key, Crypto.Cipher.AES.MODE_CBC, iv)
        return decipher.encrypt(bytes(data))

    def CryptoCanAlgo_SolveChallenge(self, random, serial, deviceID):
        buffer = deviceID + struct.pack("<LL", random, serial)
        xorStr = ''
        for i in range(len(buffer)):
            xorStr += chr(ord(buffer[i]) ^ 0xA5)
        return (
            [
                RSHash(buffer),
                JSHash(buffer),
                DJBHash(buffer),
                DEKHash(buffer),
            ],
            RSHash(xorStr),
        )

    def msTimer(self, msTime):
        if self.forceStartMessage:
            self.forceStartMessage = False
            self.nextStatusMessageTime = msTime + 1000 * ((self.serial & 0x3F) + 6 * 60)
            self.sendCommandWithVersion(LoxCanLegacyMessage.LoxCmd.RequestStart)
        elif msTime >= self.nextStatusMessageTime:
            self.nextStatusMessageTime = msTime + 1000 * ((self.serial & 0x3F) + 6 * 60)
            self.sendCommandWithVersion(LoxCanLegacyMessage.LoxCmd.alive_request)

    def canPacket(self, message):
        deviceType = (self.serial >> 24) & 0x0F  # device type in the top bits
        # these are the 5 CAN filters used by legacy extensions:
        if (message.address & 0x1FFFFFFF) == 0x00000000:  # Multicast to all extensions
            self.packetMulticastAll(message)
        elif (message.address & 0x1FFFFFFF) == (deviceType << 24):  # Multicast to all extensions of a certain type
            self.packetMulticastExtension(message)
        elif (message.address & 0x1FFFFFFF) == (self.serial | 0x10000000):  # Send to the extension directly
            self.packetToExtension(message)
        elif (message.address & 0x1FFFFFFF) == self.serial:  # Send from the extension
            self.packetFromExtension(message)
        elif (message.address & 0x1FFF0000) == ((deviceType << 16) | 0x1F000000):  # Firmware update packet to all extensions of a certain type
            self.packetFirmwareUpdate(message.address & 0xFFFF, message.data)

    def packetMulticastAll(self, message):  # multicast to all devices is used during start and for sync
        if message.command == LoxCanLegacyMessage.LoxCmd.identity_led:
            print("Extension: LED Identification OFF")
        elif message.command == LoxCanLegacyMessage.LoxCmd.identify_unknown_extensions:
            self.isMuted = False
            if (
                not self.isDeviceIdentified
            ):  # this extension is not known to the configuration?
                self.forceStartMessage = True
        elif message.command == LoxCanLegacyMessage.LoxCmd.set_extension_offline or message.command == LoxCanLegacyMessage.LoxCmd.ParkExtension:
            self.isMuted = False
            self.isDeviceIdentified = False
        elif message.command == LoxCanLegacyMessage.LoxCmd.send_sync:  # used to synchronize the LED blinking
            pass
        elif message.command == LoxCanLegacyMessage.LoxCmd.send_sync_package:
            pass
        else:
            print("# packetMulticastAll %s" % (message))
        pass

    def packetMulticastExtension(self, message):  # Multicast to a specific extension type is only used for firmware updates
        if message.command == LoxCanLegacyMessage.LoxCmd.software_update:
            self.firmwareUpdateActive = False
            if message.data[1] <= self.hardwareVersion:
                if message.val16 == 0xDEAD or message.val32 != self.version:
                    self.firmwareUpdateData = bytearray()
                    self.firmwareUpdateCRCs = []
                    self.firmwareUpdateActive = True
                    # ignored by the Miniserver:
                    self.sendCommandWithVersion(LoxCanLegacyMessage.LoxCmd.BC_ACK)
                else:
                    # ignored by the Miniserver:
                    self.sendCommandWithVersion(LoxCanLegacyMessage.LoxCmd.BC_NAK)
        elif message.command == LoxCanLegacyMessage.LoxCmd.BootExtension:
            self.isMuted = False
            self.firmwareUpdateActive = False
            if message.val16 == 0xDEAD or self.firmwareNewVersion != self.version:
                self.version = self.firmwareNewVersion  # HACK: we simply force our version to be the version of the update to stop further update tries
                # reboot device
                self.reset()
        elif message.command == LoxCanLegacyMessage.LoxCmd.update_verify:
            if self.firmwareUpdateActive:
                self.firmwareNewVersion = message.val32
                if (message.data[1] == 0x00 and message.val32 != self.version) or message.data[1] == 0x01:  # verify, if version is different or a force verify
                    # verify CRC32 over the 1kb blocks...
                    while (len(self.firmwareUpdateData) % 0x400) != 0:  # round up to next page
                        self.firmwareUpdateData.append(0xFF)
                    checksumValid = True
                    for pageNo in range(0, message.val16):
                        calcCRC = stm32_crc32(self.firmwareUpdateData[pageNo * 0x400:(pageNo + 1) * 0x400])
                        if self.firmwareUpdateCRCs[pageNo] != calcCRC:
                            msg = LoxCanLegacyMessage()
                            msg.serial = self.serial
                            msg.isServerMessage = False
                            msg.command = LoxCanLegacyMessage.LoxCmd.SendPageCrc
                            msg.val15 = pageNo
                            msg.val32 = calcCRC
                            self.canbus.send(msg)
                            msg.addMessage(msg)
                            checksumValid = False
                    if checksumValid:
                        self.firmwareNewVersion = message.val32
        elif message.command == LoxCanLegacyMessage.LoxCmd.SendPageCrc:
            if self.firmwareUpdateActive:
                while len(self.firmwareUpdateCRCs) <= message.val16:
                    self.firmwareUpdateCRCs.append(0)
                self.firmwareUpdateCRCs[message.val16] = message.val32
        elif message.command == LoxCanLegacyMessage.LoxCmd.MuteExtension:
            self.isMuted = True
            print("Extension: muted")
        else:
            print("# packetMulticastExtension %s" % (message))
        pass

    def send_fragmented_package(self, fragmentedCommand, fragData):
        fragLength = len(fragData)
        fragData += chr(0) * 6 # to avoid an out-of-bounds below

        msg = LoxCanLegacyMessage()
        msg.serial = self.serial
        msg.isServerMessage = False
        msg.command = LoxCanLegacyMessage.LoxCmd.SendFragmented
        msg.data[1] = 0x00 # header
        msg.data[2] = 0x19 # fragmented command
        msg.data[3] = 0x00 # unused
        msg.data[4] = fragLength & 0xFF
        msg.data[5] = fragLength >> 8
        checksum = 0
        for val in fragData:
            checksum += ord(val)
        msg.data[6] = checksum & 0xFF
        msg.data[7] = (checksum >> 8) & 0xFF
        self.canbus.send(msg)
        msg.addMessage(msg)

        index = 1
        for offset in range(0,fragLength,6):
            msg.data[1] = index
            index += 1
            msg.data[2] = fragData[0+offset]
            msg.data[3] = fragData[1+offset]
            msg.data[4] = fragData[2+offset]
            msg.data[5] = fragData[3+offset]
            msg.data[6] = fragData[4+offset]
            msg.data[7] = fragData[5+offset]
            self.canbus.send(msg)
            msg.addMessage(msg)

    def packetToExtension(self, message):
        if message.isFragmentedPackage:
            if message.command == 0x18: # CryptoChallengeRequest
                decryptedData = self.CryptoCanAlgo_DecryptInitPacket(message.data[1:], self.serial)
                magic, randomValue, zero, zero = struct.unpack("<LLLL", decryptedData)
                if magic == 0xdeadbeef: # valid request?
                    # this seems to be the master device ID for all devices
                    cryptoCanMasterDeviceID = binascii.unhexlify(LoxoneCryptoMasterDeviceID)
                    self.cryptoKey,self.cryptoIV = self.CryptoCanAlgo_SolveChallenge(randomValue, self.serial, cryptoCanMasterDeviceID)

                    # send a reply to confirm the authorization
                    cryptoReply = struct.pack("<LL", 0xDEADBEEF, random.randrange(0xFFFFFFFF))
                    cryptoReply += chr(0xa5) * 8
                    encrypted_package = self.CryptoCanAlgo_EncryptDataPacket(cryptoReply, self.cryptoKey,self.cryptoIV)
                    self.send_fragmented_package(0x19, encrypted_package)
            return
        if message.command == LoxCanLegacyMessage.LoxCmd.send_identify:
            self.isDeviceIdentified = True
            self.isMuted = False
            self.forceStartMessage = True
        elif message.command == LoxCanLegacyMessage.LoxCmd.identity_led:
            print("Extension: LED Identification ON")
        elif message.command == LoxCanLegacyMessage.LoxCmd.alive_request:  # Check Alive Request from Miniserver
            self.sendCommandWithVersion(LoxCanLegacyMessage.LoxCmd.alive_reply)
        elif message.command == LoxCanLegacyMessage.LoxCmd.set_extension_offline or message.command == LoxCanLegacyMessage.LoxCmd.ParkExtension:
            self.isMuted = False
            self.isDeviceIdentified = False
            print("Extension: parked")
        elif message.command == LoxCanLegacyMessage.LoxCmd.SendBlinkPos:  # LED blink position
            # blinkPos = message.val32
            # sync LEDs between all extensions
            # print ('Extension: LED Blink Position %d' % (blinkPos))
            pass
        elif message.command == LoxCanLegacyMessage.LoxCmd.alive_reply:
            pass
        elif message.command == LoxCanLegacyMessage.LoxCmd.request_CAN_diagnosis_packet:
            rxCount = 0  # CAN receive errors
            txCount = 0  # CAN transmission errors
            errorCount = 0  # CAN Errors since reboot
            self.sendCommandWithValues(
                LoxCanLegacyMessage.LoxCmd.LinkDiagnosisRx,
                0x00,
                (rxCount & 0x7F) + ((txCount & 0x7F) << 8),
                errorCount,
            )
        elif message.command == LoxCanLegacyMessage.LoxCmd.MuteExtension:
            self.isMuted = True
        elif message.command == LoxCanLegacyMessage.LoxCmd.SendFragmented:
            pass
        else:
            print("# packetToExtension %s" % (message))
        pass

    def packetFromExtension(self, message):
        pass  # these packages can be ignored, as they come _from_ the extension anyway

    def packetFirmwareUpdate(self, package, data):
        if not self.firmwareUpdateActive:
            return
        if package == 0xFFFF:  # last package?
            return
        while len(self.firmwareUpdateData) < (package + 1) * 8:
            self.firmwareUpdateData += "\0" * 8
        self.firmwareUpdateData[package * 8 + 0] = data[0]
        self.firmwareUpdateData[package * 8 + 1] = data[1]
        self.firmwareUpdateData[package * 8 + 2] = data[2]
        self.firmwareUpdateData[package * 8 + 3] = data[3]
        self.firmwareUpdateData[package * 8 + 4] = data[4]
        self.firmwareUpdateData[package * 8 + 5] = data[5]
        self.firmwareUpdateData[package * 8 + 6] = data[6]
        self.firmwareUpdateData[package * 8 + 7] = data[7]


###############################################################################
# Emulate Relay Extension
# - 14 relay outputs
# - overheating shutdown and CPU temperature reporting
###############################################################################
class LoxBusExtensionRelay(LoxBusLegacyExtension):
    def update_relays(self, bitmask):
        if self.shutdownFlag:  # if the hardware is overheating, turn all relays off
            bitmask = 0x0000
        for outputIndex in range(0, 14):
            if bitmask & (1 << outputIndex):
                self.hwDigitalOutBitmask |= 1 << outputIndex
            else:
                self.hwDigitalOutBitmask &= ~(1 << outputIndex)
        print("### Relay Status %#x" % (self.hwDigitalOutBitmask))

    def __init__(self, canbus, serial):
        LoxBusLegacyExtension.__init__(self, canbus, (serial & 0xFFFFFF) | (0x0B << 24), 1, 10031107)

    def reset(self):
        self.hwDigitalOutBitmask = 0x0000
        self.shutdownFlag = False  # emergency shutdown active? (Temperature too high, here:constant, just for testing)
        self.temperature = 70.3  # current temperature (here:constant, just for testing)
        LoxBusLegacyExtension.reset(self)

    def msTimer(self, msTime):
        # send the temperature after the next status message, or when forced
        doSendTemp = msTime >= self.nextStatusMessageTime or self.forceSendTemperature
        LoxBusLegacyExtension.msTimer(self, msTime)
        if not self.isMuted and doSendTemp:
            self.forceSendTemperature = False
            # convert temperature in Celsius into Luminary System Temperature (as returned by the ADC in the CPU)
            value = int(((1475 - (self.temperature * 10)) * 1024) / 2245)
            # Reverse conversion: tempC = (1475-(value*2245/1024))/10
            self.sendCommandWithValues(
                LoxCanLegacyMessage.LoxCmd.command_send_temperature,
                0x00,
                0x00 | (self.shutdownFlag << 8),
                value,
            )

    def packetToExtension(self, message):
        if message.command == LoxCanLegacyMessage.LoxCmd.SendBlinkPos:  # LED blink position is set after boot, this is the time to update Loxone with the current temperature
            self.forceSendTemperature = True
            LoxBusLegacyExtension.packetToExtension(self, message)
        elif message.command == LoxCanLegacyMessage.LoxCmd.set_DigOutputs:  # Digital Outputs Bits (14 possible bits)
            setBitmask = message.val32
            self.update_relays(setBitmask)
            self.sendCommandWithValues(
                LoxCanLegacyMessage.LoxCmd.set_DigOutputs,
                0x00,
                0,
                self.hwDigitalOutBitmask,
            )
        else:
            LoxBusLegacyExtension.packetToExtension(self, message)


###############################################################################
# Emulate Loxone Extension
# - 8 digital Outputs
# - 4 analog Outputs (0…10V, 12-bit resolution)
# - 12 digital Inputs (24V, state and frequency measurement up to 150Hz)
# - 4 analog Inputs (0…10V, 10-bit resolution, also usable as 4 additional digital 24V inputs)
# - overheating shutdown and CPU temperature reporting
###############################################################################
class LoxBusExtension(LoxBusLegacyExtension):
    # send four 10-bit values (0-10V) in one package, used for analog in and analog out values
    def sendCommandAnalogValues(self, command, valueList):
        if self.isMuted:
            return
        val0 = valueList[0]
        val1 = valueList[1]
        val2 = valueList[2]
        val3 = valueList[3]
        highBitMask = (val0 >> 8) & 3
        highBitMask |= ((val1 >> 8) & 3) << 2
        highBitMask |= ((val2 >> 8) & 3) << 4
        highBitMask |= ((val3 >> 8) & 3) << 6
        msg = LoxCanLegacyMessage()
        msg.serial = self.serial
        msg.isServerMessage = False
        msg.command = command
        msg.data[1] = highBitMask
        msg.val32 = val0
        self.canbus.send(msg)
        msg.addMessage(msg)

    def sendCommandConfigAcknowledge(self, cfgBitmask):
        if cfgBitmask & 0x8000:
            self.configBitmask = cfgBitmask & 0x3FFF
        else:
            self.configBitmask |= cfgBitmask & 0x3FFF
        if cfgBitmask & 0x4000:
            if not self.isMuted:
                msg = LoxCanLegacyMessage()
                msg.serial = self.serial
                msg.isServerMessage = False
                msg.command = LoxCanLegacyMessage.LoxCmd.ACKCFG
                msg.val16 = self.configBitmask
                msg.val32 = self.version
                self.canbus.send(msg)
                msg.addMessage(msg)

    def convertValueToMilliseconds(self, value):
        msValue = value >> 3
        expValue = value & 7
        if expValue == 0:
            return msValue
        elif expValue == 1:
            return msValue * 10  # 10ms
        elif expValue == 2:
            return msValue * 100  # 100ms
        elif expValue == 3:
            return msValue * 1000  # 1s
        elif expValue == 4:
            return msValue * 10000  # 10s
        elif expValue == 5:
            return msValue * 60000  # 1min
        elif expValue == 6:
            return msValue * 600000  # 10min
        elif expValue == 7:
            return msValue * 3600000  # 1hour
        pass

    def __init__(self, canbus, serial):
        LoxBusLegacyExtension.__init__(self, canbus, (serial & 0xFFFFFF) | (0x01 << 24), 1, 10031107)

    def reset(self):
        self.forceSendTemperature = False

        self.analogInForceValueFlag = False
        self.analogInCurrentValues = [0] * 4
        self.analogInAverageSum = [0] * 4
        self.analogInAverageCounter = [0] * 4
        self.analogInMinTimeChangeValues = [0] * 4
        self.analogInDelayValues = [0] * 4
        self.analogInLastTime = [0] * 4
        self.hwAnalogInValues = [0] * 4

        self.digitalInForceFrequencyFlag = False
        self.digitalInForceFlag = False
        self.digitalInValues = [0] * 12
        self.digitalInFreqCounterFlag = [False] * 12
        self.digitalInFreqCounter = [0] * 12
        self.digitalInFreqLastTransmittedCounter = [0] * 12
        self.digitalInFreqTransmitCounter = 0
        self.digitalInTime = [0] * 12
        self.digitalInThrottleTime = [0] * 12
        self.digitalInThrottleBitmask = 0x0000
        self.digitalInLastFreqBitmask = 0x0000
        self.digitalInLastTransmittedBitmask = 0x0000

        self.hwDigitalInBitmask = 0x0000  # 12 bits representing the state of the actual hardware

        self.analogOutForceValueFlag = False
        self.analogOutTargetValues = [0] * 4
        self.analogOutCurrentValues = [0] * 4
        self.analogOutLastSetValues = [0] * 4
        self.analogOutPerceptionFlag = [False] * 4  # True => newValue = (value * value / 1000)
        self.analogOutFadeCounter = [0] * 4
        self.analogOutFadeCounterMaxValue = [0] * 4
        self.analogOutFadeOffset = [0] * 4
        self.analogOutDirectionFlag = [0] * 4  # -1:below target value, 0:value reached, 1:above target value

        self.hwAnalogOutValues = [0] * 4  # 0…0xFFF representing the state of the actual hardware
        self.hwDigitalOutBitmask = 0x00  # 8 bits representing the state of the actual hardware
        self.shutdownFlag = False  # emergency shutdown active? (Temperature too high, here:constant, just for testing)
        self.temperature = 70.3  # current temperature (here:constant, just for testing)
        self.configChecksum = bytearray([0] * 7)
        self.configBitmask = 0x0000
        LoxBusLegacyExtension.reset(self)

    def msTimer(self, msTime):
        # send the temperature after the next status message, or when forced
        doSendTemp = msTime >= self.nextStatusMessageTime or self.forceSendTemperature
        LoxBusLegacyExtension.msTimer(self, msTime)
        if not self.isMuted and doSendTemp:
            self.forceSendTemperature = False
            # convert temperature in Celsius into Luminary System Temperature (as returned by the ADC in the CPU)
            value = int(((1475 - (self.temperature * 10)) * 1024) / 2245)
            # Reverse conversion: tempC = (1475-(value*2245/1024))/10
            self.sendCommandWithValues(
                LoxCanLegacyMessage.LoxCmd.command_send_temperature,
                0x00,
                0x00 | (self.shutdownFlag << 8),
                value,
            )

        # Handle Digital Inputs
        hwDigitalInBitmask = self.hwDigitalInBitmask
        transmitFrequencyFlag = False
        freqCounterBitmask = 0x0000
        self.digitalInForceFlag = False
        for digitalInIndex in range(0, 12):
            digitalInBitMask = 1 << digitalInIndex
            if self.digitalInFreqCounterFlag[digitalInIndex]:  # count the input changes for the frequency
                freqCounterBitmask |= digitalInBitMask
                if (hwDigitalInBitmask & digitalInBitMask) ^ (self.digitalInLastFreqBitmask & digitalInBitMask):
                    self.digitalInFreqCounter[digitalInIndex] += 1
                self.digitalInFreqTransmitCounter += 1
                if self.digitalInFreqTransmitCounter >= 1000:
                    self.digitalInFreqTransmitCounter = 0
                    transmitFrequencyFlag = True
            else:  # regular value changes
                changedBits = self.digitalInLastTransmittedBitmask ^ hwDigitalInBitmask
                if self.digitalInTime[digitalInIndex]:  # is there a throttle active?
                    if changedBits & digitalInBitMask:  # did input actually change between the last calls?
                        if self.digitalInThrottleBitmask & digitalInBitMask:  # did we already transmit this bit?
                            if msTime < self.digitalInThrottleTime[digitalInIndex]:  # timeout?
                                hwDigitalInBitmask ^= digitalInBitMask # reset this bit, so it does not get reported
                            else:
                                self.digitalInThrottleTime[digitalInIndex] = 0  # reset timeout
                                self.digitalInThrottleBitmask &= ~digitalInBitMask
                                self.digitalInForceFlag = True  # and transmit this bit!
                        else:
                            self.digitalInThrottleTime[digitalInIndex] = msTime + self.digitalInTime[digitalInIndex]
                            hwDigitalInBitmask ^= digitalInBitMask # reset this bit, so it does not get reported
                            self.digitalInThrottleBitmask |= digitalInBitMask
                    else:  # input did not change, reset throttle time
                        self.digitalInThrottleTime[digitalInIndex] = 0
                        self.digitalInThrottleBitmask &= ~digitalInBitMask
                else:  # no throttle => always send if input changed
                    if changedBits & digitalInBitMask:
                        self.digitalInForceFlag = True
        hwDigitalInBitmask &= ~freqCounterBitmask  # erase all frequency counter bits
        if hwDigitalInBitmask != self.digitalInLastTransmittedBitmask or self.digitalInForceFlag:
            self.digitalInLastTransmittedBitmask = hwDigitalInBitmask
            self.sendCommandWithValues(self, 0x50 | 0x80, 0x00, 0x0000, self.digitalInLastTransmittedBitmask)

        # transmit digital input
        if transmitFrequencyFlag or self.digitalInForceFrequencyFlag:
            pkgIndex = 0
            freqBuffer = [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]
            for digitalInIndex in range(0, 12):
                if self.digitalInFreqCounterFlag[digitalInIndex]:
                    freq = self.digitalInFreqCounter[digitalInIndex]
                    if freq or self.digitalInFreqLastTransmittedCounter[digitalInIndex] != 0 or self.digitalInForceFrequencyFlag:  # don't repeat 0 Hz
                        self.digitalInFreqLastTransmittedCounter[digitalInIndex] = freq
                        freqBuffer[pkgIndex] = freq
                        pos = 4
                        if pkgIndex >= 2:
                            pos = 5
                        if (pkgIndex & 1) != 0:
                            freqBuffer[pos] = (digitalInIndex << 4) | (freqBuffer[pos] & 0x0F)
                        else:
                            freqBuffer[pos] = (freqBuffer[pos] & 0xF0) | digitalInIndex
                        pkgIndex += 1
                        if pkgIndex == 4:
                            msg = LoxCanLegacyMessage()
                            msg.serial = self.serial
                            msg.isServerMessage = False
                            msg.command = LoxCanLegacyMessage.LoxCmd.ValueFrequency
                            msg.data[1] = freqBuffer[0]
                            msg.data[2] = freqBuffer[1]
                            msg.data[3] = freqBuffer[2]
                            msg.data[4] = freqBuffer[3]
                            msg.data[5] = freqBuffer[4]
                            msg.data[6] = freqBuffer[5]
                            msg.data[7] = freqBuffer[6]
                            self.canbus.send(msg)
                            msg.addMessage(msg)
                            pkgIndex = 0
            if pkgIndex != 0:
                msg = LoxCanLegacyMessage()
                msg.serial = self.serial
                msg.isServerMessage = False
                msg.command = LoxCanLegacyMessage.LoxCmd.ValueFrequency
                msg.data[1] = freqBuffer[0]
                msg.data[2] = freqBuffer[1]
                msg.data[3] = freqBuffer[2]
                msg.data[4] = freqBuffer[3]
                msg.data[5] = freqBuffer[4]
                msg.data[6] = freqBuffer[5]
                msg.data[7] = freqBuffer[6]
                self.canbus.send(msg)
                msg.addMessage(msg)
            self.digitalInForceFrequencyFlag = False
        self.digitalInLastFreqBitmask = hwDigitalInBitmask

        # Handle Analog Outputs
        # fade the analog values towards their target values
        for analogOutIndex in range(0, 4):
            self.analogOutFadeCounter[analogOutIndex] += 1
            if self.analogOutFadeCounter[analogOutIndex] >= self.analogOutFadeCounterMaxValue[analogOutIndex]:
                self.analogOutFadeCounter[analogOutIndex] = 0
                if self.analogOutDirectionFlag[analogOutIndex] < 0:  # below target value?
                    self.analogOutCurrentValues[analogOutIndex] += self.analogOutFadeOffset[analogOutIndex]
                    if self.analogOutCurrentValues[analogOutIndex] > self.analogOutTargetValues[analogOutIndex]:
                        self.analogOutCurrentValues[analogOutIndex] = self.analogOutTargetValues[analogOutIndex]
                        self.analogOutDirectionFlag[analogOutIndex] = 0
                elif self.analogOutDirectionFlag[analogOutIndex] > 0:  # above target value?
                    self.analogOutCurrentValues[analogOutIndex] -= self.analogOutFadeOffset[analogOutIndex]
                    if self.analogOutCurrentValues[analogOutIndex] < self.analogOutTargetValues[analogOutIndex]:
                        self.analogOutCurrentValues[analogOutIndex] = self.analogOutTargetValues[analogOutIndex]
                        self.analogOutDirectionFlag[analogOutIndex] = 0
        # set the 12 bit hardware values based on the current value
        for analogOutIndex in range(0, 4):
            value = self.analogOutCurrentValues[analogOutIndex]
            if self.analogOutForceValueFlag or self.analogOutLastSetValues[analogOutIndex] != value:  # only change the value, if it actually changed
                self.analogOutLastSetValues[analogOutIndex] = value
                if self.analogOutPerceptionFlag[analogOutIndex]:
                    value = value * value / 1000
                outputValue12Bit = (0xFFF * value + 0x800) / 1000
                if outputValue12Bit > 0xFFF:
                    outputValue12Bit = 0xFFF
                if outputValue12Bit < 0:
                    outputValue12Bit = 0
                self.hwAnalogOutValues[analogOutIndex] = outputValue12Bit
        if self.analogOutForceValueFlag:
            self.sendCommandAnalogValues(
                LoxCanLegacyMessage.LoxCmd.AnalogOutputValue0,
                self.analogOutTargetValues,
            )
            self.analogOutForceValueFlag = False

        # Handle Analog Inputs
        for analogInIndex in range(0, 4):
            inDelay = self.analogInDelayValues[analogInIndex]
            if inDelay > 1000:  # analog average over a certain time
                if inDelay == 1001:
                    avgTime = 1 * 60 * 1000
                elif inDelay == 1002:
                    avgTime = 5 * 60 * 1000
                elif inDelay == 1003:
                    avgTime = 10 * 60 * 1000
                elif inDelay == 1004:
                    avgTime = 30 * 60 * 1000
                elif inDelay == 1005:
                    avgTime = 60 * 60 * 1000
                elif inDelay == 1006:
                    avgTime = 1 * 1000
                elif inDelay == 1007:
                    avgTime = 5 * 1000
                elif inDelay == 1008:
                    avgTime = 10 * 1000
                elif inDelay == 1009:
                    avgTime = 30 * 1000
                else:
                    avgTime = 60 * 1000  # all other (illegal) cases
                self.analogInAverageSum[analogInIndex] += self.hwAnalogInValues[analogInIndex]
                self.analogInAverageCounter[analogInIndex] += 1
                if msTime >= self.analogInLastTime[analogInIndex] + avgTime:  # time for a new average report?
                    self.analogInLastTime[analogInIndex] = msTime
                    self.analogInCurrentValues[analogInIndex] = self.analogInAverageSum[analogInIndex] / self.analogInAverageCounter[analogInIndex]
                    self.analogInAverageSum[analogInIndex] = 0
                    self.analogInAverageCounter[analogInIndex] = 0
                    self.analogInForceValueFlag = True
            else:  # report value changes
                # did the value change enough?
                if self.hwAnalogInValues[analogInIndex] < self.analogInCurrentValues[analogInIndex] - inDelay or self.hwAnalogInValues[analogInIndex] > self.analogInCurrentValues[analogInIndex] + inDelay:
                    if self.analogInMinTimeChangeValues[analogInIndex]:  # throttle the number of reports?
                        if msTime > self.analogInLastTime[analogInIndex]:  # enough time passed?
                            self.analogInLastTime[analogInIndex] = msTime
                            self.analogInCurrentValues[analogInIndex] = self.hwAnalogInValues[analogInIndex]
                            self.analogInForceValueFlag = True
                    else:
                        self.analogInCurrentValues[analogInIndex] = self.hwAnalogInValues[analogInIndex]
                        self.analogInForceValueFlag = True
        if self.analogInForceValueFlag:
            self.sendCommandAnalogValues(LoxCanLegacyMessage.LoxCmd.AnalogInputValue0, self.analogInCurrentValues)
            self.analogInForceValueFlag = False

    def packetMulticastAll(self, message):
        if message.command == LoxCanLegacyMessage.LoxCmd.identify_unknown_extensions:
            if not self.isDeviceIdentified:  # this extension is not known to the configuration?
                self.analogOutForceValueFlag = False
                self.analogInForceValueFlag = False
                self.digitalInForceFrequencyFlag = False
            LoxBusLegacyExtension.packetMulticastAll(self, message)
        else:
            LoxBusLegacyExtension.packetMulticastAll(self, message)

    def packetToExtension(self, message):
        if message.command == LoxCanLegacyMessage.LoxCmd.send_identify:
            self.analogOutForceValueFlag = False
            self.analogInForceValueFlag = False
            self.digitalInForceFrequencyFlag = False
            LoxBusLegacyExtension.packetToExtension(self, message)
        elif message.command == message.command == LoxCanLegacyMessage.LoxCmd.SendBlinkPos:  # LED blink position is set after boot, this is the time to update Loxone with the current temperature
            self.forceSendTemperature = True
            self.digitalInForceFrequencyFlag = True
            LoxBusLegacyExtension.packetToExtension(self, message)
        elif message.command == LoxCanLegacyMessage.LoxCmd.AnalogInputSensitivity0 or message.command == LoxCanLegacyMessage.LoxCmd.AnalogInputSensitivity1:  # Analog Input Sensitivity
            inputOffset = 0
            if message.command == LoxCanLegacyMessage.LoxCmd.AnalogInputSensitivity1:
                inputOffset = 2
            self.analogInDelayValues[0 + inputOffset] = message.data[4] | (((message.data[1] >> 0) & 3) << 8)
            self.analogInDelayValues[1 + inputOffset] = message.data[6] | (((message.data[1] >> 4) & 3) << 8)
            self.analogInMinTimeChangeValues[0 + inputOffset] = self.convertValueToMilliseconds(message.data[5] | (((message.data[1] >> 2) & 3) << 8))
            self.analogInMinTimeChangeValues[1 + inputOffset] = self.convertValueToMilliseconds(message.data[7] | (((message.data[1] >> 6) & 3) << 8))
            cfgBitmask = message.val16
            self.sendCommandConfigAcknowledge(cfgBitmask)
        elif message.command == LoxCanLegacyMessage.LoxCmd.AnalogOutputValue0:

            def aOutSetValue(aOutputIndex, newValue):
                if newValue > 1000:
                    newValue = 1000
                currentValue = self.analogOutCurrentValues[aOutputIndex]
                self.analogOutTargetValues[aOutputIndex] = newValue
                if self.analogOutFadeOffset[aOutputIndex] == 0 or currentValue - newValue <= 9:  # jump to value or delta less than 1%?
                    self.analogOutCurrentValues[aOutputIndex] = newValue  # then jump directly to the new value
                    self.analogOutDirectionFlag[aOutputIndex] = 0
                else:
                    if newValue > self.analogOutCurrentValues[aOutputIndex]:
                        self.analogOutDirectionFlag[aOutputIndex] = -1
                    else:
                        self.analogOutDirectionFlag[aOutputIndex] = 1

            aOutSetValue(0, message.data[4] | (((message.data[1] >> 0) & 3) << 8))
            aOutSetValue(1, message.data[5] | (((message.data[1] >> 2) & 3) << 8))
            aOutSetValue(2, message.data[6] | (((message.data[1] >> 4) & 3) << 8))
            aOutSetValue(3, message.data[7] | (((message.data[1] >> 6) & 3) << 8))
            self.analogOutForceValueFlag = True
        elif message.command == LoxCanLegacyMessage.LoxCmd.AnalogOutputInit:

            def aOutInit(aOutputIndex, perceptionFlag, fadeRate):
                # the perception correction is simply taking the analog value (A) and calculates newA = (A * A / 1000)
                self.analogOutPerceptionFlag[aOutputIndex] = perceptionFlag != 0x04
                self.analogOutFadeOffset[aOutputIndex] = fadeRate
                if fadeRate == 21:  # every 100ms: 1%
                    self.analogOutFadeCounterMaxValue[aOutputIndex] = 100
                    self.analogOutFadeOffset[aOutputIndex] = 1
                elif fadeRate == 22:  # every 100ms: 2%
                    self.analogOutFadeCounterMaxValue[aOutputIndex] = 100
                    self.analogOutFadeOffset[aOutputIndex] = 2
                else:  # every 20ms => 5% * fadeRate
                    self.analogOutFadeCounterMaxValue[aOutputIndex] = 20
                    self.analogOutFadeOffset[aOutputIndex] = fadeRate

            aOutInit(0, ((message.data[2] >> 0) & 0xF), message.data[4] & 0x1F)
            aOutInit(1, ((message.data[2] >> 4) & 0xF), message.data[5] & 0x1F)
            aOutInit(2, ((message.data[3] >> 0) & 0xF), message.data[6] & 0x1F)
            aOutInit(3, ((message.data[3] >> 4) & 0xF), message.data[7] & 0x1F)
            if not self.isMuted:
                message.serial = self.serial
                message.isServerMessage = False
                message.command = LoxCanLegacyMessage.LoxCmd.AnalogOutputInit
                self.canbus.send(message)
                message.addMessage(message)
        elif message.command == LoxCanLegacyMessage.LoxCmd.DigitalInputSensitivity0 or message.command == LoxCanLegacyMessage.LoxCmd.DigitalInputSensitivity1 or message.command == LoxCanLegacyMessage.LoxCmd.DigitalInputSensitivity2:
            inputOffset = 0
            if message.command == LoxCanLegacyMessage.LoxCmd.DigitalInputSensitivity1:
                inputOffset = 2
            elif message.command == LoxCanLegacyMessage.LoxCmd.DigitalInputSensitivity2:
                inputOffset = 4

            def dInSetConfig(inputIndex, value):
                self.digitalInFreqCounterFlag[inputIndex] = value == 0x3FF
                if not self.digitalInFreqCounterFlag[inputIndex]:
                    self.digitalInTime[inputIndex] = self.convertValueToMilliseconds(value)

            dInSetConfig(inputOffset + 0, message.data[4] | (((message.data[1] >> 0) & 3) << 8))
            dInSetConfig(inputOffset + 1, message.data[5] | (((message.data[1] >> 2) & 3) << 8))
            dInSetConfig(inputOffset + 2, message.data[6] | (((message.data[1] >> 4) & 3) << 8))
            dInSetConfig(inputOffset + 3, message.data[7] | (((message.data[1] >> 6) & 3) << 8))
            cfgBitmask = message.val16
            self.sendCommandConfigAcknowledge(cfgBitmask)
        elif message.command == LoxCanLegacyMessage.LoxCmd.set_DigOutputs:
            self.hwDigitalOutBitmask = message.val32
            self.sendCommandWithValues(
                LoxCanLegacyMessage.LoxCmd.set_DigOutputs,
                0x00,
                0,
                self.hwDigitalOutBitmask,
            )
        elif message.command == LoxCanLegacyMessage.LoxCmd.ValueChecksum:
            self.configChecksum = message.data[1:]  # 7 bytes checksum
        elif message.command == LoxCanLegacyMessage.LoxCmd.RequestChecksum:
            if not self.isMuted:
                msg = LoxCanLegacyMessage()
                msg.serial = self.serial
                msg.isServerMessage = False
                msg.command = LoxCanLegacyMessage.LoxCmd.ValueChecksum
                msg.data[1] = self.configChecksum[0]
                msg.data[2] = self.configChecksum[1]
                msg.data[3] = self.configChecksum[2]
                msg.data[4] = self.configChecksum[3]
                msg.data[5] = self.configChecksum[4]
                msg.data[6] = self.configChecksum[5]
                msg.data[7] = self.configChecksum[6]
                self.canbus.send(msg)
                msg.addMessage(msg)
        else:
            LoxBusLegacyExtension.packetToExtension(self, message)


###############################################################################
# Emulate NAT Extension/Device - Base Class
###############################################################################
class LoxBusNATExtension(object):
    def send_nat_package(self, command, data=None, isFragmentedPackage=False):
        """Send out a regular NAT package – it is only sent, if a NAT is assigned"""
        if self.extensionNAT == 0x00:
            return
        msg = LoxCanNATMessage()
        if not data:
            data = chr(0) * 8
        if len(data) < 8:  # make sure to fill the package to 8 bytes
            data = (data + chr(0) * 7)[:7]
        for index in range(1, 8):
            msg.data[index] = data[index - 1]
        msg.extensionNAT = self.extensionNAT
        if self.busId == 0x10:  # Loxone Link Bus devices
            msg.deviceNAT = self.deviceNAT
        else:  # Tree Bus devices
            msg.deviceNAT = self.extensionNAT
        msg.isServerMessage = False
        msg.command = command
        msg.type = self.busId
        if isFragmentedPackage:
            msg.flags = 1
        self.canbus.send(msg)
        self.statistics_sent = self.statistics_sent + 1
        msg.addMessage(msg)

    def send_command_with_devtype_and_serial(self, command):
        """Send from an extension/device without a valid NAT"""
        msg = LoxCanNATMessage()
        data = struct.pack("<BHI", 0, self.deviceType, self.serial)
        for index in range(1, 8):
            msg.data[index] = data[index - 1]
        if self.deviceState == 0:  # a device, which is offline doesn't have any NAT
            msg.extensionNAT = CRC8_function(struct.pack("<I", self.serial)) | 0x80
        else:
            msg.extensionNAT = self.extensionNAT
        msg.deviceNAT = 0x00
        msg.isServerMessage = False
        msg.command = command
        msg.type = self.busId
        self.canbus.send(msg)
        self.statistics_sent = self.statistics_sent + 1
        msg.addMessage(msg)

    def send_fragmented_package(self, command, data):
        """Send a fragmented package"""
        header = struct.pack("<BHI", command, len(data), stm32_crc32(bytearray(data)))
        self.send_nat_package(LoxCanNATMessage.xCanID_t.Fragment_Start, header, True)  # fragmented header
        offset = 0
        while offset < len(data):
            self.send_nat_package(LoxCanNATMessage.xCanID_t.Fragment_Data, data[offset:offset + 7], True)  # fragmented header
            offset += 7

    def send_version_package(self, command, reason):
        """Send a version package with all relevant hardware infos"""
        data = struct.pack(
            "<LLLLBHB",
            self.version,
            0,
            self.configurationCRC,
            self.serial,
            int(reason),
            self.deviceType,
            self.hardwareVersion,
        )
        self.send_fragmented_package(command, data)

    def send_string(self, command, str):
        """Send fragmented string, used for WebRequests and debug logging"""
        while len(str) > 0:  # break the string into 131 byte character strings
            sstr = str[:131]
            self.send_fragmented_package(command, chr(0) + chr(len(sstr) + 1) + sstr + chr(0))
            str = str[131:]

    def send_update_package(self, message):
        """Manage firmware update package"""
        if self.deviceNAT != message.deviceNAT and message.deviceNAT != 0xFF:  # not matching this device
            return
        if self.deviceState == 1:  # parked
            return
        size, action, deviceType, version, page, index = struct.unpack("<BBHLHH", message.data[:12])
        if deviceType != self.deviceType:  # update is for a different hardware
            return
        if version <= self.version:  # update is not newer than the current version
            return
        if action == 1:  # Firmware data
            print("# Update: Firmware data for %s: %4.4x.%4.4x %s" % (LoxCanMessage.versionString(version), page, index, binascii.hexlify(message.data[12:])))
        elif action == 2:  # CRC data
            print("# Update: CRC data for %s: %4.4x %s" % (LoxCanMessage.versionString(version), page, binascii.hexlify(message.data[12:])))
        elif action == 3:  # Verify update
            self.version = version
            print("# Update: Verify update for %s: Pagecount:%4.4x" % (LoxCanMessage.versionString(version), page))
        elif action == 4:  # Verify update and reboot
            self.version = version
            print("# Update: Verify update for %s: Pagecount:%4.4x" % (LoxCanMessage.versionString(version), page))
            self.reset()

    def send_alive_packet(self):
        header = struct.pack("<BHL", LoxCanNATMessage.Reason.Alive_Packet, 0, self.configurationCRC)
        self.send_nat_package(LoxCanNATMessage.xCanID_t.Alive_Packet, header)  # Alive

    def CryptoCanAlgo_DecryptInitPacket(self, data, serial):
        # pre-calculate the AES key/iv based on constant data and the serial number
        aesKey = [0] * 4
        aesIV = [0] * 4
        for i in range(0, 4):
            aesKey[i] = ~(serial ^ self.CryptoCanAlgoKey[i]) & 0xFFFFFFFF
            aesIV[i] = (serial ^ self.CryptoCanAlgoIV[i]) & 0xFFFFFFFF
        key = struct.pack("<LLLL", aesKey[0], aesKey[1], aesKey[2], aesKey[3])
        iv = struct.pack("<LLLL", aesIV[0], aesIV[1], aesIV[2], aesIV[3])
        decipher = Crypto.Cipher.AES.new(key, Crypto.Cipher.AES.MODE_CBC, iv)
        return decipher.decrypt(bytes(data))

    def CryptoCanAlgo_DecryptInitPacketLegacy(self, data, serial):
        # pre-calculate the AES key/iv based on constant data and the serial number
        aesKey = [0] * 4
        aesIV = [0] * 4
        for i in range(0, 4):
            aesKey[i] = ~(serial ^ self.CryptoCanAlgoLegacyKey[i]) & 0xFFFFFFFF
            aesIV[i] = (serial ^ self.CryptoCanAlgoLegacyIV[i]) & 0xFFFFFFFF
        key = struct.pack("<LLLL", aesKey[0], aesKey[1], aesKey[2], aesKey[3])
        iv = struct.pack("<LLLL", aesIV[0], aesIV[1], aesIV[2], aesIV[3])
        decipher = Crypto.Cipher.AES.new(key, Crypto.Cipher.AES.MODE_CBC, iv)
        return decipher.decrypt(bytes(data))

    def CryptoCanAlgo_EncryptInitPacketLegacy(self, data, serial):
        # pre-calculate the AES key/iv based on constant data and the serial number
        aesKey = [0] * 4
        aesIV = [0] * 4
        for i in range(0, 4):
            aesKey[i] = ~(serial ^ self.CryptoCanAlgoLegacyKey[i]) & 0xFFFFFFFF
            aesIV[i] = (serial ^ self.CryptoCanAlgoLegacyIV[i]) & 0xFFFFFFFF
        key = struct.pack("<LLLL", aesKey[0], aesKey[1], aesKey[2], aesKey[3])
        iv = struct.pack("<LLLL", aesIV[0], aesIV[1], aesIV[2], aesIV[3])
        decipher = Crypto.Cipher.AES.new(key, Crypto.Cipher.AES.MODE_CBC, iv)
        return decipher.encrypt(bytes(data))

    def CryptoCanAlgo_DecryptDataPacket(self, data, key, iv):
        key = struct.pack("<LLLL", iv ^ key[0], iv ^ key[1], iv ^ key[2], iv ^ key[3])
        iv = struct.pack("<LLLL", iv, iv, iv, iv)
        decipher = Crypto.Cipher.AES.new(key, Crypto.Cipher.AES.MODE_CBC, iv)
        return decipher.decrypt(bytes(data))

    def CryptoCanAlgo_EncryptDataPacket(self, data, key, iv):
        key = struct.pack("<LLLL", iv ^ key[0], iv ^ key[1], iv ^ key[2], iv ^ key[3])
        iv = struct.pack("<LLLL", iv, iv, iv, iv)
        decipher = Crypto.Cipher.AES.new(key, Crypto.Cipher.AES.MODE_CBC, iv)
        return decipher.encrypt(bytes(data))

    def CryptoCanAlgo_SolveChallenge(self, random, serial, deviceID):
        buffer = deviceID + struct.pack("<LL", random, serial)
        xorStr = ''
        for i in range(len(buffer)):
            xorStr += chr(ord(buffer[i]) ^ 0xA5)
        return (
            [
                RSHash(buffer),
                JSHash(buffer),
                DJBHash(buffer),
                DEKHash(buffer),
            ],
            RSHash(xorStr),
        )

    def CryptoCanAlgo_SolveChallengeLegacy(self, random, serial, deviceID):
        buffer = deviceID + struct.pack("<LL", random, serial)
        return (
            [
                RSHash(buffer),
                JSHash(buffer),
                DJBHash(buffer),
                DEKHash(buffer),
            ],
            BPHash(buffer),
        )

    def crypto_update_receive_key(self, forceReply): # send keys to the Miniserver for packages _from_ the Miniserver _to_ the extension/device
        currentTime = int(round(time.time() * 1000 * 1000))  # seconds timer
        if self.legacyRequestTimer == None:
            self.legacyRequestTimer = currentTime
        if forceReply or (self.legacyRequestTimer + 10 < currentTime): # throttle to every 10s
            self.legacyRequestTimer = currentTime
            # send a request for authorization
            randomValue = random.randrange(0xFFFFFFFF)
            cryptoReply = struct.pack("<LL", 0xDEADBEEF, randomValue)
            cryptoReply = cryptoReply.ljust(16, chr(0))
            self.cryptoReceiveKey,self.cryptoReceiveIV = self.CryptoCanAlgo_SolveChallenge(randomValue, self.serial, self.deviceID)
            self.send_fragmented_package(
                LoxCanNATMessage.xCanID_t.CryptoChallengeRollingKeyReply,
                self.CryptoCanAlgo_EncryptInitPacketLegacy(cryptoReply, self.serial),
            )
        pass

    def __init__(self, canbus, serial, deviceType, hardwareVersion, version):
        self.canbus = canbus
        self.busId = 0x10  # Tree devices use 0x11
        self.serial = serial
        self.deviceType = deviceType
        self.hardwareVersion = hardwareVersion
        self.version = version
        # this seems to be the master device ID for all devices
        self.deviceID = binascii.unhexlify(LoxoneCryptoMasterDeviceID)
        self.configOfflineTimeout = 15 * 60  # default: 15 minutes
        self.configurationCRC = 0x00000000  # no config
        random.seed()
        encryptedAESKey = binascii.unhexlify(LoxoneCryptoEncryptedAESKey)
        self.CryptoCanAlgoKey = [DEKHash(encryptedAESKey), JSHash(encryptedAESKey), DJBHash(encryptedAESKey), RSHash(encryptedAESKey)]
        encryptedAESIV = binascii.unhexlify(LoxoneCryptoEncryptedAESIV)
        self.CryptoCanAlgoIV = [DEKHash(encryptedAESIV), JSHash(encryptedAESIV), DJBHash(encryptedAESIV), RSHash(encryptedAESIV)]
        self.CryptoCanAlgoLegacyKey = LoxoneCryptoCanAlgoLegacyKey
        self.CryptoCanAlgoLegacyIV = LoxoneCryptoCanAlgoLegacyIV
        self.legacyRequestTimer = None
        self.cryptoReceiveKey = [0] * 4
        self.cryptoReceiveIV = 0
        self.cryptoSendKey = [0] * 4
        self.cryptoSendIV = 0
        self.reset()

    def reset(self):
        # initialize all runtime variables, just like after a reset
        # we do not reinitialize the configuration, which should be in FLASH memory anyway
        self.extensionNAT = 0x00
        self.deviceNAT = 0x00
        self.randomNatInterval = 0
        self.offlineCountdown = 0
        self.lastMsTime = 0
        self.upTime = time.time()
        self.NATStateCounter = 0
        self.statistics_received = 0
        self.statistics_sent = 0
        self.setDeviceState(0)

    def configUpdate(self):
        # call whenever the configuration was changed
        pass

    def sendDefaults(self):
        # default values sent back to the Miniserver after a `NAT offer`
        pass

    def setDeviceState(self, state):
        """0 = offline, 1 = parked, 2 = online"""
        if state != 0:
            self.NATStateCounter = 0
        self.deviceState = state

    def msTimer(self, msTime):
        # send a NAT index request, if the device is offline
        if self.deviceState == 0:
            # throttle it more the longer the device is offline to limit the bus load
            if self.randomNatInterval == 0:
                self.randomNatInterval = msTime + random.randrange(50) + 1
            elif self.randomNatInterval < msTime:
                self.send_command_with_devtype_and_serial(LoxCanNATMessage.xCanID_t.NAT_Index_Request)
                if self.NATStateCounter <= 2:
                    self.randomNatInterval = msTime + random.randrange(50) + 100
                elif self.NATStateCounter <= 9:
                    self.randomNatInterval = msTime + random.randrange(500) + 500
                else:
                    self.randomNatInterval = msTime + random.randrange(1000) + 2000
                self.NATStateCounter += 1
        # every second
        if self.lastMsTime == 0 or self.lastMsTime + 1000 <= msTime:
            self.lastMsTime = msTime
            if self.offlineCountdown:
                if self.offlineCountdown == self.configOfflineTimeout / 10:
                    self.send_alive_packet()  # alive to the Miniserver, to ask for a reply
                elif self.offlineCountdown == 1:
                    self.setDeviceState(0)  # device is offline, no answer from the Miniserver
                self.offlineCountdown = self.offlineCountdown - 1

    def canPacket(self, message):
        if (message.type != self.busId or (message.flags & 2) != 2):  # not a NAT package from the Miniserver?
            return
        # message from the Miniserver re-trigger the offline timeout
        self.offlineCountdown = self.configOfflineTimeout  # it resets the offline countdown
        self.statistics_received = self.statistics_received + 1
        if message.extensionNAT == 0xFF:
            self.packetBroadcastToNAT(message)
        elif self.extensionNAT == message.extensionNAT:
            self.packetToNAT(message)

    def packetToNAT(self, message):
        if message.command == LoxCanNATMessage.xCanID_t.Config_Equal:
            pass  # is ignored
        elif message.command == LoxCanNATMessage.xCanID_t.Ping:
            self.send_nat_package(LoxCanNATMessage.xCanID_t.Pong)
        elif message.command == LoxCanNATMessage.xCanID_t.Alive_Packet:
            if self.configurationCRC == message.val32:
                self.send_nat_package(LoxCanNATMessage.xCanID_t.Config_Equal)
            else:
                self.send_alive_packet()
        elif message.command == LoxCanNATMessage.xCanID_t.Send_Config_Data:
            self.configurationCRC = stm32_crc32(message.data[1:-4])  # keep the CRC for the configuration for the alive message
            size, version, blinkOffset, unknown, offlineTimeout = struct.unpack("<BBBBL", message.data[1:9])
            if len(message.data) - 1 == size:
                print("# Config Version:%d BlinkOffset:%d Unknown:%d offlineTimeout:%ds Data:%s" % (version,blinkOffset,unknown,offlineTimeout,binascii.hexlify(message.data[9:-4])))
                self.configOfflineTimeout = offlineTimeout
                self.configData = message.data[9:-4]
                self.configUpdate()
        elif message.command == LoxCanNATMessage.xCanID_t.WebServicesText:
            webServiceRequest = ""
            if message.data[2] > 1:  # Zero-Byte at the end of the string is ignored anyway
                webServiceRequest = message.data[3:message.data[2] + 3 - 1].decode()
            # SysShell requests:
            if webServiceRequest == "Reboot":
                self.reset()
                return
            elif webServiceRequest == "ForceUpdate":
                self.version = 1000000
                self.send_version_package(LoxCanNATMessage.xCanID_t.Start,LoxCanNATMessage.Reason.AliveRequested)
            elif webServiceRequest == "GetCrashLog":
                pass
            elif webServiceRequest == "ResetCrashLog":
                pass
            elif webServiceRequest == "Queue":  # expects "ls" as a parameter, like Queue/ls
                pass
            elif webServiceRequest == "ReadMemory":
                pass
            elif webServiceRequest == "Version":
                self.send_string(LoxCanNATMessage.xCanID_t.WebServicesText,"App Version: %d, HW Version %d\r\n" % (self.version, self.hardwareVersion))
            elif webServiceRequest == "Statistics":
                self.send_string(LoxCanNATMessage.xCanID_t.WebServicesText,"Sent:%d;Rcv:%d;Err:%d;REC:%d;TEC:%d;HWE:%d;TQ:%d;mTQ:%d;QOvf:%d;RQ:%d;mRQ:%d;" % (self.statistics_sent,self.statistics_received,0,0,0,0,0,8,0,1,1))
            elif webServiceRequest == "TechReport":
                self.send_string(LoxCanNATMessage.xCanID_t.WebServicesText,"UpTime:%ds;Serial:%08x;NatIdx:%d;" % (int(round(time.time() - self.upTime)),self.serial,self.extensionNAT))
            else:
                print("WebServiceRequest: %s" % webServiceRequest)
                pass
        elif message.command == LoxCanNATMessage.xCanID_t.CAN_Diagnosis_Request and message.val16 == 0:
            # 0:Tree Extension, 1:Left, 2:Right;Receive Errors;Transmit Errors;Overall errors
            self.send_nat_package(LoxCanNATMessage.xCanID_t.CAN_Diagnosis_Reply,struct.pack("<BBBL", 0, 0, 0, 0))
        elif message.command == LoxCanNATMessage.xCanID_t.CAN_Error_Request and message.val16 == 0:
            # 0:Tree Extension, 1:Left, 2:Right;Receive Errors;Transmit Errors;Overall errors
            self.send_nat_package(LoxCanNATMessage.xCanID_t.CAN_Error_Reply,struct.pack("<BBBL", 0, 0, 0, 0))
        elif message.command == LoxCanNATMessage.xCanID_t.Update_Reply:
            self.send_update_package(message)
        elif message.command == LoxCanNATMessage.xCanID_t.Fragment_Start:
            pass
        elif message.command == LoxCanNATMessage.xCanID_t.Fragment_Data:
            pass

        elif message.command == LoxCanNATMessage.xCanID_t.CryptoValueAccessCodeInput: # only send by the device to the Miniserver
            print("*** CryptoValueAccessCodeInput")
        elif message.command == LoxCanNATMessage.xCanID_t.CryptoNfcId: # only send by the device to the Miniserver
            print("*** CryptoNfcId")
        elif message.command == LoxCanNATMessage.xCanID_t.CryptoValueDigital or message.command == LoxCanNATMessage.xCanID_t.CryptoValueAnalog or message.command == LoxCanNATMessage.xCanID_t.CryptoKeyPacket:
            decryptedData = self.CryptoCanAlgo_DecryptDataPacket(message.data[1:], self.cryptoReceiveKey,self.cryptoReceiveIV)
            magic, randomValue = struct.unpack("<LL", decryptedData[:8])
            print("*** CryptoPacket_%02x %08x %08x %s" % (int(message.command), magic, randomValue, binascii.hexlify(decryptedData[8:])))
            if magic == 0xdeadbeef: # valid request?
                self.cryptoReceiveIV += 1 # rolling key
                pass # deal with the package
            else:
                self.crypto_update_receive_key(False)
        elif message.command == LoxCanNATMessage.xCanID_t.CryptoDeviceIdRequest: # Miniserver requests the (encrypted) 12 byte internal STM32 serial number. Cached by the Miniserver in /sys/device/settings.bin
            decryptedData = self.CryptoCanAlgo_DecryptInitPacketLegacy(message.data[1:], self.serial)
            magic, randomValue, zero, zero = struct.unpack("<LLLL", decryptedData)
            if magic == 0xdeadbeef: # valid request?
                # send a reply to confirm the authorization
                cryptoReply = struct.pack("<LL", 0xDEADBEEF, random.randrange(0xFFFFFFFF))
                cryptoReply += self.deviceID
                cryptoReply = cryptoReply.ljust(32, chr(0))
            else: # invalid request
                cryptoReply = struct.pack("<LL", 0, random.randrange(0xFFFFFFFF))
                cryptoReply = cryptoReply.ljust(32, chr(0))
            self.send_fragmented_package(
                LoxCanNATMessage.xCanID_t.CryptoDeviceIdReply,
                self.CryptoCanAlgo_EncryptInitPacketLegacy(cryptoReply, self.serial),
            )
        elif message.command == LoxCanNATMessage.xCanID_t.CryptoDeviceIdReply: # only received by the Miniserver, never by extensions or devices
            print("*** CryptoDeviceIdReply")
        elif message.command == LoxCanNATMessage.xCanID_t.CryptoChallengeRollingKeyReply: # server sends keys to encrypt data packages _from_ the extension/device _to_ the Miniserver
            decryptedData = self.CryptoCanAlgo_DecryptInitPacketLegacy(message.data[1:], self.serial)
            magic, randomValue, zero, zero = struct.unpack("<LLLL", decryptedData)
            print("*** CryptoChallengeRollingKeyReply %08x %08x %08x%08x" % (magic, randomValue, zero, zero))
            if magic == 0xdeadbeef: # valid request?
                self.cryptoSendKey,self.cryptoSendIV = self.CryptoCanAlgo_SolveChallenge(randomValue, self.serial, self.deviceID)
                self.sendDefaults()
        elif message.command == LoxCanNATMessage.xCanID_t.CryptoChallengeRollingKeyRequest: # server requests keys to encrypt data packages _from_ the Miniserver _to_ the extension/device
            decryptedData = self.CryptoCanAlgo_DecryptInitPacketLegacy(message.data[1:], self.serial)
            magic, randomValue, zero, zero = struct.unpack("<LLLL", decryptedData)
            print("*** CryptoChallengeRollingKeyRequest %08x %08x %08x%08x" % (magic, randomValue, zero, zero))
            self.crypto_update_receive_key(True)
        elif message.command == LoxCanNATMessage.xCanID_t.CryptoChallengeRequest: # Authorization Challenge to identify valid devices (new in 10.3.11.6 or later)
            decryptedData = self.CryptoCanAlgo_DecryptInitPacket(message.data[1:], self.serial)
            magic, randomValue, zero, zero = struct.unpack("<LLLL", decryptedData)
            if magic == 0xdeadbeef: # valid request?
                self.cryptoKey,self.cryptoIV = self.CryptoCanAlgo_SolveChallenge(randomValue, self.serial, self.deviceID)

                # send a reply to confirm the authorization
                cryptoReply = struct.pack("<LL", 0xDEADBEEF, random.randrange(0xFFFFFFFF))
                cryptoReply += chr(0xa5) * 8
                encPacket = self.CryptoCanAlgo_EncryptDataPacket(cryptoReply, self.cryptoKey,self.cryptoIV)
                self.send_fragmented_package(
                    LoxCanNATMessage.xCanID_t.CryptoChallengeReply,
                    self.CryptoCanAlgo_EncryptDataPacket(cryptoReply, self.cryptoKey,self.cryptoIV),
                )
        elif message.command == LoxCanNATMessage.xCanID_t.CryptoChallengeReply: # Validate Authorization Challenge keys to identify valid devices (new in 10.3.11.6 or later)
            decryptedData = self.CryptoCanAlgo_DecryptDataPacket(message.data[1:], self.cryptoKey,self.cryptoIV),
            magic, randomValue, zero, zero = struct.unpack("<LLLL", decryptedData)
            if magic == 0xdeadbeef: # valid request?
                # send a reply to confirm the authorization
                cryptoReply = struct.pack("<LL", 0xDEADBEEF, random.randrange(0xFFFFFFFF))
                cryptoReply += chr(0xa5) * 8
                self.send_fragmented_package(
                    LoxCanNATMessage.xCanID_t.CryptoChallengeReply,
                    self.CryptoCanAlgo_EncryptDataPacket(cryptoReply, self.cryptoKey,self.cryptoIV),
                )

    def packetBroadcastToNAT(self, message):
        if message.command == LoxCanNATMessage.xCanID_t.Version_Request:
            if message.val32 == self.serial:
                # print('# Version request')
                self.send_version_package(LoxCanNATMessage.xCanID_t.Device_Version,LoxCanNATMessage.Reason.AliveRequested)
        elif message.command == LoxCanNATMessage.xCanID_t.Park_Devices:
            # print('# Park')
            self.extensionNAT = CRC8_function(struct.pack("<I", self.serial)) | 0x80
            self.setDeviceState(1)  # parked
        elif message.command == LoxCanNATMessage.xCanID_t.Sync_Packet:
            # print('# Sync')
            pass
        elif message.command == LoxCanNATMessage.xCanID_t.Identify_LED:
            if message.val32 == self.serial:
                # print('# Identify LED on')
                pass
            else:
                # print('# Identify LED off')
                pass
        elif message.command == LoxCanNATMessage.xCanID_t.Update_Reply:
            self.send_update_package(message)
        elif message.command == LoxCanNATMessage.xCanID_t.Identify_Unknown_Extensions:
            if self.deviceState == 1:  # respond as a parked device
                time.sleep(0.001 * random.randrange(100))
                self.send_command_with_devtype_and_serial(LoxCanNATMessage.xCanID_t.NAT_Index_Request)
        elif message.command == LoxCanNATMessage.xCanID_t.Search_Devices:
            time.sleep(0.001 * random.randrange(100))
            self.send_command_with_devtype_and_serial(LoxCanNATMessage.xCanID_t.Search_Reply)
        elif message.command == LoxCanNATMessage.xCanID_t.NAT_Offer:
            if message.val32 == self.serial:
                newNat = message.data[1]
                if message.data[2] & 1:  # park device
                    self.extensionNAT = newNat
                    self.setDeviceState(1)  # parked
                    self.send_version_package(LoxCanNATMessage.xCanID_t.Start, LoxCanNATMessage.Reason.Pairing)
                elif (newNat & 0x80) == 0x00:  # not a parked NAT?
                    self.extensionNAT = newNat
                    self.setDeviceState(2)  # online
                    self.send_version_package(LoxCanNATMessage.xCanID_t.Start, LoxCanNATMessage.Reason.Pairing)
                    if (message.data[2] & 4) == 0:  # rolling key encryption?
                        self.crypto_update_receive_key(True) # send keys to the Miniserver, so the extension/device can receive encrypted packages
                    if (message.data[2] & 2) == 0:  # no default values requested?
                        self.sendDefaults()


###############################################################################
# Emulate DI Extension
###############################################################################
class LoxBusDIExtension(LoxBusNATExtension):
    frequencyBitmask = 0
    hardwareBitmask = 0
    lastBitmaskTime = 0
    lastFrequencyTime = 0

    def __init__(self, canbus, serial):
        diExtensionType = 0x0014
        LoxBusNATExtension.__init__(self,canbus,(serial & 0xFFFFFF) | (diExtensionType << 24),diExtensionType,0,10031108)

    def sentBitmask(self):
        self.send_nat_package(LoxCanNATMessage.xCanID_t.Digital_Value,struct.pack("<BHI", 0, 0, self.hardwareBitmask))

    def reset(self):
        self.hardwareBitmask = 0
        self.lastBitmaskTime = 0
        self.lastFrequencyTime = 0
        LoxBusNATExtension.reset(self)

    def msTimer(self, msTime):
        # simulate the inputs changing every second. They are sent back on every value change,
        # but not faster than 20ms (= 50Hz)
        if self.lastBitmaskTime == 0 or self.lastBitmaskTime + 1000 <= msTime:
            self.lastBitmaskTime = msTime
            self.hardwareBitmask = self.hardwareBitmask + 1
            self.sentBitmask()
        # the frequency is sent every second
        if self.lastFrequencyTime == 0 or self.lastFrequencyTime + 1000 <= msTime:
            self.lastFrequencyTime = msTime
            # and send a test frequency (between 0…100Hz) on input 1
            self.send_nat_package(LoxCanNATMessage.xCanID_t.Frequency,struct.pack("<BHI", 0, 0, random.randrange(0, 100, 10)))
        LoxBusNATExtension.msTimer(self, msTime)

    def packetToNAT(self, message):
        LoxBusNATExtension.packetToNAT(self, message)

    def packetBroadcastToNAT(self, message):
        LoxBusNATExtension.packetBroadcastToNAT(self, message)

    def sendDefaults(self):
        self.sentBitmask()  # just sent the current value back

    def configUpdate(self):
        self.frequencyBitmask = struct.unpack("<L", self.configData)
        print("# frequencyBitmask = %08x" % self.frequencyBitmask)


###############################################################################
# Emulate AI Extension
###############################################################################
class LoxBusAIExtension(LoxBusNATExtension):
    def __init__(self, canbus, serial):
        diExtensionType = 0x0016
        LoxBusNATExtension.__init__(self,canbus,(serial & 0xFFFFFF) | (diExtensionType << 24),diExtensionType,0,10000905)

    def msTimer(self, msTime):
        LoxBusNATExtension.msTimer(self, msTime)

    def packetToNAT(self, message):
        LoxBusNATExtension.packetToNAT(self, message)

    def packetBroadcastToNAT(self, message):
        LoxBusNATExtension.packetBroadcastToNAT(self, message)


###############################################################################
# Emulate AO Extension
###############################################################################
class LoxBusAOExtension(LoxBusNATExtension):
    def __init__(self, canbus, serial):
        diExtensionType = 0x0017
        LoxBusNATExtension.__init__(self,canbus,(serial & 0xFFFFFF) | (diExtensionType << 24),diExtensionType,0,10000905)

    def msTimer(self, msTime):
        LoxBusNATExtension.msTimer(self, msTime)

    def packetToNAT(self, message):
        LoxBusNATExtension.packetToNAT(self, message)

    def packetBroadcastToNAT(self, message):
        LoxBusNATExtension.packetBroadcastToNAT(self, message)


###############################################################################
# Emulate Base Tree Extension
###############################################################################
class LoxBusTreeBaseExtension(LoxBusNATExtension):
    def __init__(self, canbus, serial):
        treeBusExtensionType = 0x0013
        self.wiredDevicesLeftBranch = []
        self.wiredDevicesRightBranch = []
        LoxBusNATExtension.__init__(self,canbus,(serial & 0xFFFFFF) | (treeBusExtensionType << 24),treeBusExtensionType,0,10031125)

    def reset(self):
        LoxBusNATExtension.reset(self)
        # initialize all runtime variables, just like after a reset
        # we do not reinitialize the configuration, which should be in FLASH memory anyway
        self.isLeftTree = None

    def addDevice(self, device, isLeftBranch=False):
        if isLeftBranch:
            self.wiredDevicesLeftBranch.append(device)
        else:
            self.wiredDevicesRightBranch.append(device)

    def send(self, treemsg):  # message from Tree Bus devices back to the Tree Base Extension
        message = copy.copy(treemsg)
        # print('TREE -> %x:%s %s' % (message.address, binascii.hexlify(message.data), message))
        message.type = 0x10  # Loxone Link bus message
        message.extensionNAT = self.extensionNAT # use the NAT from the Tree Base extensionNAT, the deviceNAT contains the correct NAT for the device
        if message.flags & 2:  # message from server?
            message.flags = message.flags & ~2  # reset this flags
            if message.command == LoxCanNATMessage.xCanID_t.Tree_Shortcut_Test:
                message.deviceNAT = 0x00
                if self.isLeftTree:
                    message.data[1] |= 0x40
            else:
                message.command = LoxCanNATMessage.xCanID_t.Tree_Shortcut
                message.deviceNAT = 0x00
                message.data[1] = 0x00
                message.data[2] = 0x00
                message.data[3] = 0x00
                message.data[4] = 0x00
                message.data[5] = 0x00
                message.data[6] = 0x00
                message.data[7] = 0x00
                if self.isLeftTree:
                    message.data[1] |= 0x40
        else:
            if message.command == LoxCanNATMessage.xCanID_t.Search_Reply or message.command == LoxCanNATMessage.xCanID_t.NAT_Index_Request:
                if self.isLeftTree:
                    message.data[1] |= 0x40
        # print('LBUS <- %x:%s %s' % (message.address, binascii.hexlify(message.data), message))
        self.canbus.send(message)

    def loxbus_forward_to_treebus(self, message):
        treemsg = copy.copy(message)
        # print('LBUS -> %x:%s %s' % (treemsg.address, binascii.hexlify(treemsg.data), treemsg))
        treemsg.type = 0x11  # Tree bus message
        deviceNAT = treemsg.deviceNAT
        treemsg.extensionNAT = deviceNAT
        # print('TREE <- %x:%s %s' % (treemsg.address, binascii.hexlify(treemsg.data), treemsg))
        # messages to parked devices is sent to both branches for parked devices, except for a NAT offer
        if (deviceNAT & 0x80) == 0x80 and treemsg.command != LoxCanNATMessage.xCanID_t.NAT_Offer:
            for device in self.wiredDevicesRightBranch:
                device.canbus = self  # send should go back to the tree extension, instead to the CAN Bus
                self.isLeftTree = False
                device.canPacket(treemsg)
            for device in self.wiredDevicesLeftBranch:
                device.canbus = self  # send should go back to the tree extension, instead to the CAN Bus
                self.isLeftTree = True
                device.canPacket(treemsg)
        else:  # all other messages are sent only to the correct branch
            if treemsg.command == LoxCanNATMessage.xCanID_t.NAT_Offer:
                deviceNAT = treemsg.data[1]  # for NAT offset use the new NAT
            if deviceNAT & 0x40:  # left branch?
                for device in self.wiredDevicesLeftBranch:
                    device.canbus = self  # send should go back to the tree extension, instead to the CAN Bus
                    self.isLeftTree = True
                    device.canPacket(treemsg)
            else:  # right branch
                for device in self.wiredDevicesRightBranch:
                    device.canbus = self  # send should go back to the tree extension, instead to the CAN Bus
                    self.isLeftTree = False
                    device.canPacket(treemsg)

    def sendDefaults(self):
        # Tree Extension Base: send CAN errors for both Tree Branches and crashlog, if available
        # 0:Tree Extension, 1:Left, 2:Right;Receive Errors;Transmit Errors;Overall errors
        header = struct.pack("<BBBL", 1, 0, 0, 0)
        self.send_nat_package(LoxCanNATMessage.xCanID_t.CAN_Error_Reply, header)
        header = struct.pack("<BBBL", 2, 0, 0, 0)
        self.send_nat_package(LoxCanNATMessage.xCanID_t.CAN_Error_Reply, header)

    def msTimer(self, msTime):
        LoxBusNATExtension.msTimer(self, msTime)
        for device in self.wiredDevicesRightBranch:
            device.canbus = self  # send should go back to the tree extension, instead to the CAN Bus
            self.isLeftTree = False
            device.msTimer(msTime)
        for device in self.wiredDevicesLeftBranch:
            device.canbus = self  # send should go back to the tree extension, instead to the CAN Bus
            self.isLeftTree = True
            device.msTimer(msTime)

    def packetToNAT(self, message):
        if message.deviceNAT != 0x00:  # message not to the Tree extension, but to a device or a broadcast?
            self.loxbus_forward_to_treebus(message)  # forward it!
        else:
            if message.command == LoxCanNATMessage.xCanID_t.CAN_Diagnosis_Request:
                if message.val16 != 0:  # request for left/right branch?
                    header = struct.pack("<BBL", message.val16, 0, 0)
                    self.send_nat_package(LoxCanNATMessage.xCanID_t.CAN_Diagnosis_Reply, header)
                    return
            elif message.command == LoxCanNATMessage.xCanID_t.CAN_Error_Request:
                if message.val16 != 0:  # request for left/right branch?
                    header = struct.pack("<BBBL", message.val16, 0, 0, 0)  # CAN Error reply
                    self.send_nat_package(LoxCanNATMessage.xCanID_t.CAN_Error_Reply, header)
                    return
            LoxBusNATExtension.packetToNAT(self, message)

    def packetBroadcastToNAT(self, message):
        self.loxbus_forward_to_treebus(message)  # forward all broadcast messages
        LoxBusNATExtension.packetBroadcastToNAT(self, message)


###############################################################################
# Emulate Tree Device Base Class
###############################################################################
class LoxBusTreeBaseClass(LoxBusNATExtension):
    def __init__(self, canbus, serial, deviceType, hardwareVersion, version):
        LoxBusNATExtension.__init__(self, canbus, serial, deviceType, hardwareVersion, version)
        self.busId = 0x11  # a tree device
        # Tree devices use a custom device ID
        self.deviceID = struct.pack("<LLL",self.serial,self.serial,self.serial)

    def msTimer(self, msTime):
        LoxBusNATExtension.msTimer(self, msTime)

    def packetToNAT(self, message):
        if message.command != LoxCanNATMessage.xCanID_t.Fragment_Start and message.command != LoxCanNATMessage.xCanID_t.Fragment_Data:
            print("Tree_%04x : %s" % (self.deviceType, message))
        LoxBusNATExtension.packetToNAT(self, message)

    def packetBroadcastToNAT(self, message):
        # print('Tree%04x B> %x:%s %s' % (self.deviceType,message.address, binascii.hexlify(message.data), message))
        LoxBusNATExtension.packetBroadcastToNAT(self, message)


###############################################################################
# Emulate Alarm Siren Tree
###############################################################################
class LoxBusTreeAlarmSiren(LoxBusTreeBaseClass):
    def __init__(self, canbus, serial):
        self.hardwareTamperStatus = True # Tamper status is ok, False = device was tampered with
        self.hardwareTemperature = 23.5
        self.hardwareSendTemperature = False # currently this seems to be disabled in the hardware
        self.configOfflineHardwareState = 0 # status of strobe and alarm sound if device is offline
        self.configMaxAudibleAlarmDelay = 90 # timeout for the siren
        LoxBusTreeBaseClass.__init__(self, canbus, serial, 0x8012, 0, 10031114)

    def sendTamperStatus(self):
        self.send_nat_package(LoxCanNATMessage.xCanID_t.Digital_Value,struct.pack("<BHI", 0, 0, self.hardwareTamperStatus))

    def sendTemperature(self):
        if self.hardwareSendTemperature:
            self.send_nat_package(LoxCanNATMessage.xCanID_t.Analog_Value,struct.pack("<BHI", 0, 0x0015, self.hardwareTemperature * 1000))

    def hardwareStrobe(self, status):
        print("# Strobe Light %s" % ("on" if status else "off"))

    def hardwareAlarmSound(self, status):
        self.alarmSoundStartTimer = time.time() * 1000 if status else 0
        print("# Alarm Sound %s" % ("on" if status else "off"))

    def reset(self):
        LoxBusTreeBaseClass.reset(self)
        # initialize all runtime variables, just like after a reset
        # we do not reinitialize the configuration, which should be in FLASH memory anyway
        self.tamperStatusOk = self.hardwareTamperStatus
        self.tamperStatusTimer = 0
        self.alarmSoundStartTimer = 0
        self.temperature = -9999
        self.temperatureTimer = 0

    def msTimer(self, msTime):
        # send tamper status, if changed or an update every 30s as an alive message
        if self.tamperStatusOk != self.hardwareTamperStatus or self.tamperStatusTimer + 30 * 1000 <= msTime:
            self.tamperStatusTimer = msTime
            self.tamperStatusOk = self.hardwareTamperStatus
            self.sendTamperStatus()
        # check the alarm sound timeout
        if self.alarmSoundStartTimer != 0:
            if self.alarmSoundStartTimer + self.configMaxAudibleAlarmDelay * 1000 <= msTime:
                self.alarmSoundStartTimer = 0
                self.hardwareAlarmSound(False)
        # send the temperature whenever it changes or every 5 minutes
        if self.hardwareSendTemperature:
            if abs(self.temperature - self.hardwareTemperature) > 0.1 or self.temperatureTimer <= msTime:
                self.temperature = self.hardwareTemperature
                self.temperatureTimer = msTime + 5 * 60 * 1000
                self.sendTemperature()
        LoxBusTreeBaseClass.msTimer(self, msTime)

    def packetToNAT(self, message):
        if message.command == LoxCanNATMessage.xCanID_t.Digital_Value:
            self.hardwareStrobe((message.val32 & 1) == 1)
            self.hardwareAlarmSound((message.val32 & 2) == 2)
        else:
            LoxBusTreeBaseClass.packetToNAT(self, message)

    def setDeviceState(self, state):
        LoxBusTreeBaseClass.setDeviceState(self, state)
        if state == 0:  # offline?
            if (self.configOfflineHardwareState & 3) == 1:
                self.hardwareStrobe(True)
            elif (self.configOfflineHardwareState & 3) == 2:
                self.hardwareStrobe(False)
            elif ((self.configOfflineHardwareState >> 2) & 3) == 1:
                self.hardwareAlarmSound(True)
            elif ((self.configOfflineHardwareState >> 2) & 3) == 2:
                self.hardwareAlarmSound(False)

    def configUpdate(self):
        self.configOfflineHardwareState, self.configMaxAudibleAlarmDelay = struct.unpack("<BH", self.configData)
        print("# configOfflineHardwareState = %02x, configMaxAudibleAlarmDelay = %ss" % (self.configOfflineHardwareState, self.configMaxAudibleAlarmDelay))

    def sendDefaults(self):
        self.sendTemperature()
        self.sendTamperStatus()


###############################################################################
# Emulate LED Spot RGBW Tree
###############################################################################
class LoxBusTreeLEDSpotRGBW(LoxBusTreeBaseClass):
    def __init__(self, canbus, serial):
        LoxBusTreeBaseClass.__init__(self, canbus, serial, 0x8016, 0, 10031111)

    def packetToNAT(self, message):
        if message.command == LoxCanNATMessage.xCanID_t.RGBW:  # Standard Actuator
            print(
                "# RGBW(%s%d%%,%d%%,%d%%,%s%d%%)"
                % (
                    "JUMP:" if (message.val16 & 7) != 0 else "",
                    message.data[4],
                    message.data[5],
                    message.data[6],
                    "JUMP:" if (message.val16 & 8) != 0 else "",
                    message.data[7],
                )
            )
        elif message.command == LoxCanNATMessage.xCanID_t.Composite_RGBW:  # Smart Actuator
            fadingTime = message.val16
            if (fadingTime & 0x4000) != 0:
                fadingTime = (fadingTime & 0x3FFF) * 1.0
            else:
                fadingTime = (fadingTime & 0x3FFF) * 0.1
            print(
                "# Composite RGBW(%d%%,%d%%,%d%%,%d%%) Fade Time:%.1fs%s"
                % (
                    message.data[4],
                    message.data[5],
                    message.data[6],
                    message.data[7],
                    fadingTime,
                    "/JUMP" if (message.val16 & 0x8000) != 0 else "",
                )
            )
        else:
            LoxBusTreeBaseClass.packetToNAT(self, message)

    def configUpdate(self):
        self.configLossRed, self.configLossGreen, self.configLossBlue, self.configLossWhite, self.configFadeRed, self.configFadeGreen, self.configFadeBlue, self.configFadeWhite = struct.unpack("<BBBBBBBB", self.configData[:8])
        # Loss of Connection: Value in %% (0…100%), 101% = Retain Last State
        # Fade Rate (only used for Standard Actuator Type, not for the Smart one): 0% = Jump, 1…100%
        # Smart Actuator Type = Composite RGBW is sent, which includes the Fade Rate
        # Standard Actuator Type: 2 outputs available; Dimmer RGB and Dimmer WWW, both are changed via RGBW
        print(
            "# Loss of Connection:RGBW(%d%%,%d%%,%d%%,%d%%) Fade Rate:RGBW(%d%%,%d%%,%d%%,%d%%)"
            % (
                self.configLossRed,
                self.configLossGreen,
                self.configLossBlue,
                self.configLossWhite,
                self.configFadeRed,
                self.configFadeGreen,
                self.configFadeBlue,
                self.configFadeWhite,
            )
        )


###############################################################################
# Emulate LED Spot RGBW Tree
###############################################################################
class LoxBusTreeRGBW24VDimmer(LoxBusTreeBaseClass):
    def __init__(self, canbus, serial):
        LoxBusTreeBaseClass.__init__(self, canbus, serial, 0x800C, 0, 10031108)

    def packetToNAT(self, message):
        if message.command == LoxCanNATMessage.xCanID_t.RGBW:  # Standard Actuator
            print(
                "# RGBW(%s%d%%,%d%%,%d%%,%s%d%%)"
                % (
                    "JUMP:" if (message.val16 & 7) != 0 else "",
                    message.data[4],
                    message.data[5],
                    message.data[6],
                    "JUMP:" if (message.val16 & 8) != 0 else "",
                    message.data[7],
                )
            )
        elif message.command == LoxCanNATMessage.xCanID_t.Composite_RGBW:  # Smart Actuator
            fadingTime = message.val16
            if (fadingTime & 0x4000) != 0:
                fadingTime = (fadingTime & 0x3FFF) * 1.0
            else:
                fadingTime = (fadingTime & 0x3FFF) * 0.1
            print(
                "# Composite RGBW(%d%%,%d%%,%d%%,%d%%) Fade Time:%.1fs%s"
                % (
                    message.data[4],
                    message.data[5],
                    message.data[6],
                    message.data[7],
                    fadingTime,
                    "/JUMP" if (message.val16 & 0x8000) != 0 else "",
                )
            )
        else:
            LoxBusTreeBaseClass.packetToNAT(self, message)

    def configUpdate(self):
        self.configData += chr(0) * 12
        self.configLossRed, self.configLossGreen, self.configLossBlue, self.configLossWhite, self.configFadeRed, self.configFadeGreen, self.configFadeBlue, self.configFadeWhite, self.typeRed, self.typeGreen, self.typeBlue, self.typeWhite = struct.unpack("<BBBBBBBBBBBB", self.configData[:12])
        # Loss of Connection: Value in %% (0…100%), 101% = Retain Last State
        # Fade Rate (only used for Standard Actuator Type, not for the Smart one): 0% = Jump, 1…100%
        # Smart Actuator Type = Composite RGBW is sent, which includes the Fade Rate
        # Standard Actuator Type: 2 outputs available; Dimmer RGB and Dimmer WWW, both are changed via RGBW
        print(
            "# Loss of Connection:RGBW(%d%%,%d%%,%d%%,%d%%) Fade Rate:RGBW(%d%%,%d%%,%d%%,%d%%) type:RGBW(%d,%d,%d,%d)"
            % (
                self.configLossRed, self.configLossGreen, self.configLossBlue, self.configLossWhite,
                self.configFadeRed, self.configFadeGreen, self.configFadeBlue, self.configFadeWhite,
                self.typeRed, self.typeGreen, self.typeBlue, self.typeWhite
            )
        )


###############################################################################
# Emulate Touch Tree
###############################################################################
class LoxBusTreeTouch(LoxBusTreeBaseClass):
    def __init__(self, canbus, serial):
        LoxBusTreeBaseClass.__init__(self, canbus, serial, 0x8003, 0, 10031114)

    def configUpdate(self):
        self.unknown, self.audibleAcknowledgement = struct.unpack("<LB", self.configData)
        print("# unknown = %08x, audibleAcknowledgement = %s" % (self.unknown, self.audibleAcknowledgement != 0))


###############################################################################
# Emulate Room Comfort Sensor Tree
###############################################################################
class LoxBusTreeRoomComfortSensor(LoxBusTreeBaseClass):
    def __init__(self, canbus, serial):
        LoxBusTreeBaseClass.__init__(self, canbus, serial, 0x8010, 0, 10031111)


###############################################################################
# Emulate LED Ceiling Light Tree
###############################################################################
class LoxBusTreeCorridorLight(LoxBusTreeBaseClass):
    def __init__(self, canbus, serial):
        LoxBusTreeBaseClass.__init__(self, canbus, serial, 0x8006, 0, 10031111)


###############################################################################
# Emulate Leaf Tree
###############################################################################
class LoxBusTreeLeaf(LoxBusTreeBaseClass):
    def __init__(self, canbus, serial):
        LoxBusTreeBaseClass.__init__(self, canbus, serial, 0x8014, 0, 10031111)

    def packetToNAT(self, message):
        if message.command == LoxCanNATMessage.xCanID_t.Digital_Value:
            if message.val32 & 1:
                print("# Set Bit 0: Filter Change Interval")
            if message.val32 & 2:
                print("# Set Bit 1: unknown")
            else:
                print("# Clr Bit 1: unknown")
        elif message.command == LoxCanNATMessage.xCanID_t.Analog_Value:
            if message.val8 == 0:
                #  Mode = 0 : off (e.g. window open, stopped)
                #  Mode = 1 : Airing phase
                #  Mode = 2 : Supply fresh air (Vent outside air in)
                #  Mode = 3 : Exhaust (Vent inside air out)
                print("# Mode %d" % message.val32)
            elif message.val8 == 1:
                print("# Speed %d%%" % message.val32)
        else:
            LoxBusTreeBaseClass.packetToNAT(self, message)


    def configUpdate(self):
        self.send_nat_package(LoxCanNATMessage.xCanID_t.Digital_Value,struct.pack("<BHI", 0, 0, 0x00))
        self.FilterChange, self.TimeOffset, self.dirIdx = struct.unpack("<LLB", self.configData)
        print("# FilterChange = %dh, TimeOffset = %s, dirIndex = %d" % (self.FilterChange, self.TimeOffset, self.dirIdx))


###############################################################################
# Emulate Weather Station Tree
###############################################################################
class LoxBusTreeWeatherStation(LoxBusTreeBaseClass):
    def __init__(self, canbus, serial):
        LoxBusTreeBaseClass.__init__(self, canbus, serial, 0x800a, 0, 10031111)

    def configUpdate(self):
        self.send_nat_package(LoxCanNATMessage.xCanID_t.Digital_Value,struct.pack("<BHI", 0, 0, 0xFF))
        self.send_nat_package(LoxCanNATMessage.xCanID_t.Analog_Value,struct.pack("<BHI", 2, 0, 1000))
        self.field_8,self.brightnessSunshineThreshold,self.field_c,self.field_d,self.stormWarningThreshold = struct.unpack("<HHBBB", self.configData)
        print(
            "# field8 = %d (5), brightnessSunshineThreshold = %d (28), field_c = %d (20), field_d = %d (80), stormWarningThreshold = %d (35)"
            % (self.field_8,self.brightnessSunshineThreshold,self.field_c,self.field_d,self.stormWarningThreshold)
        )


###############################################################################
# Emulate NFC Code Touch Tree
###############################################################################
class LoxBusTreeNFCCodeTouchTree(LoxBusTreeBaseClass):
    def __init__(self, canbus, serial):
        random.seed()
        LoxBusTreeBaseClass.__init__(self, canbus, serial, 0x8009, 0, 10031111)

    def packetToNAT(self, message):
        if message.command == LoxCanNATMessage.xCanID_t.Digital_Value:
            print("Keypad Buzzer Alarm %s" % (((message.val32 >> 3) & 1) == 1))
        elif message.command == LoxCanNATMessage.xCanID_t.Analog_Value:
            print("Keypad Analog Value %d" % (message.val32))
        elif message.command == LoxCanNATMessage.xCanID_t.RGBW:
            print("Keypad RGB %x : %d,%d,%d" % (message.data[1],message.data[4],message.data[5],message.data[6]))
        elif message.command == LoxCanNATMessage.xCanID_t.TreeKeypad_Send:
            print("Keypad Mode %04x %04x" % (message.val32 & 0xF, (message.val32 >> 16) & 0xFFFF))

        LoxBusNATExtension.packetToNAT(self, message)


canbus = CANBus_USBtin(False)

devices = []
treeExt = LoxBusTreeBaseExtension(canbus, 0x13112233)
#for devId in range(0x8001,0x801a):
#    treeExt.addDevice(LoxBusTreeBaseClass(canbus, 0xbb000000 + devId, devId, 0, 10010820))
#treeExt.addDevice(LoxBusTreeNFCCodeTouchTree(canbus, 0xbbaa8009))
#treeExt.addDevice(LoxBusTreeAlarmSiren(canbus, 0xbb008012))
treeExt.addDevice(LoxBusTreeLEDSpotRGBW(canbus, 0xBB008016))
#treeExt.addDevice(LoxBusTreeTouch(canbus,0xb0aabbcc),False)
#treeExt.addDevice(LoxBusTreeCorridorLight(canbus,0xbb000001),False)
#treeExt.addDevice(LoxBusTreeRoomComfortSensor(canbus,0xb0998899),True)
#treeExt.addDevice(LoxBusTreeRGBW24VDimmer(canbus,0xb0998899),True)
#treeExt.addDevice(LoxBusTreeWeatherStation(canbus,0xb0aa8899),True)


devices.append(treeExt)  # Tree Base Extension
#devices.append(LoxBusAIExtension(canbus,0x00010000)) # AI Extension
#devices.append(LoxBusAOExtension(canbus,0x00020000)) # AO Extension
#devices.append(LoxBusExtensionRelay(canbus,0x0FF0A01)) # Relay Extension
#devices.append(LoxBusExtension(canbus,0x0FF0A00)) # Extension
#devices.append(LoxBusDIExtension(canbus,0x14123456)) # DI Extension

while True:
    message = canbus.receive()
    if message:
        message.addMessage(message)
        print(message)
        for device in devices:
            device.canPacket(message)
    else:
        msTime = int(round(time.time() * 1000))  # ms timer
        for device in devices:
            device.msTimer(msTime)
    time.sleep(0.01)  # every 10ms
