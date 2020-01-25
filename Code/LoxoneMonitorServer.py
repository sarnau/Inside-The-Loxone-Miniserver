import socket
import binascii
import struct
from datetime import datetime
import re
from http.server import HTTPServer, SimpleHTTPRequestHandler
import threading

LOCAL_IP = '192.168.178.200'

# Try loading the english strings to match the logging of the Loxone Monitor software
strDict = {}
try:
    f = open('./sys/sys_ENG/ENG.xml')
    for line in f.readlines():
        m = re.search('<String IDV="(\d+?)" Text="(.*?)"/>', line)
        if m:
            strDict[int(m.group(1))] = m.group(2)
except:
    pass
data = ''

cycleDeltaTime = 0
def parsePackageSystem(pkg):
    global cycleDeltaTime
    _,version,CoSw,CSint,Max,Heap,taskDeltaTime,cycleDeltaTime,f1C,Wdog,currentTime,SystemTimerHandlerCounter,CAN_irq_handlerCounter,EMAC_HandlerCounter,Emac_TxP,Emac_TxE,Emac_collisions,Emac_Exhau,Emac_Urun,Emac_RxP,Emac_EOF,Emac_OVR,Emac_BNA,Emac_Sof,Emac_Frag,BusPar_0,BusPar_1,BusPar_ErrorCount,BusPar_RXOverflow_Counter,LinkErrorsTX,LinkErrorsRX,numberOfTasks,f7C,f80 = struct.unpack('<HH32I', pkg[28:28+33*4])
    if version != 3:
        print('Unknown version #%d' % version)
    else:
        print('-' * 30)
        print('CPU  stats: Usage %3.1f%%' % (100-taskDeltaTime*100.0/cycleDeltaTime), end=' ')
        print('Heap %dkB' % ((Heap+511)/1024), end=' ')
        print('Max %dkB' % ((Max+511)/1024), end=' ')
        print('Wdog %08x' % Wdog, end=' ')
        print('CoSw %d' % CoSw, end=' ')
        print('CSint %d' % CSint, end=' ')
        print('Time %d' % currentTime) # since boot in ms
        print('LAN  stats: TxP %d / TxE/c %d/%d / Exhau/Urun %d/%d / RxP %d / EOF/Ovrun %d/%d / NoBuf/Sof %d/%d / Frag %d' % (Emac_TxP,Emac_TxE,Emac_collisions,Emac_Exhau,Emac_Urun,Emac_RxP,Emac_EOF,Emac_OVR,Emac_BNA,Emac_Sof,Emac_Frag))
        print('Link stats: Sent %d / Rcv %d / Err/OvE %d/%d' % (BusPar_0,BusPar_1,BusPar_ErrorCount,BusPar_RXOverflow_Counter), end=' ')
        print('TEC %d / REC %d' % (LinkErrorsTX,LinkErrorsRX), end=' ')
        print('Ticks %d' % SystemTimerHandlerCounter, end=' ')
        print('Lnk %d' % CAN_irq_handlerCounter, end=' ')
        print('EMAC %d' % EMAC_HandlerCounter)
        #print('Other     : Tasks #%d' % numberOfTasks)
        # Missing:
        # Usage: ?/3385/318
        print(taskDeltaTime,cycleDeltaTime,f1C,f7C,f80)
def parsePackageHardware(pkg):
    header,version = struct.unpack('<HH', pkg[28:32])
    if version != 2:
        print('Unknown version #%d' % version)
        return
    #print(binascii.hexlify(pkg), end='  ')
    digitalIn,relays = struct.unpack('<HH', pkg[32:32+4])
    analog1In,analog1Out = struct.unpack('<HH', pkg[32+0x80*1:32+0x80*1+4])
    analog2In,analog2Out = struct.unpack('<HH', pkg[32+0x80*2:32+0x80*2+4])
    analog3In,analog3Out = struct.unpack('<HH', pkg[32+0x80*3:32+0x80*3+4])
    analog4In,analog4Out = struct.unpack('<HH', pkg[32+0x80*4:32+0x80*4+4])
    print("Digital In %04x, Relays %04x" % (digitalIn,relays), end=' ')
    print("Analog In %6.3fV,%6.3fV,%6.3fV,%6.3fV" % (analog1In*10.0/4095,analog2In*10.0/4095,analog3In*10.0/4095,analog4In*10.0/4095), end=' ')
    print("Analog Out %6.3fV,%6.3fV,%6.3fV,%6.3fV" % (analog1Out*10.0/4095,analog2Out*10.0/4095,analog3Out*10.0/4095,analog4Out*10.0/4095))
    pass
def parsePackageTasks(pkg,strType):
    global cycleDeltaTime
    print()
    for offset in range(28,len(pkg),40):
        contextSwitches,stackSize,usedStackSize,stackRelated,timeoutCounter,state,priorityState,taskRunningStatus,_,taskID,eventID,strType,strValue,taskDeltaTime,mem,numberMem = struct.unpack('<IHHIIBBBBHHHHIII', pkg[offset:offset+40])
        thread = 'Thread%d' % taskID
        if taskID >= 560 and taskID <= 567:
            thread = strDict[560] % (taskID - 560)
        elif taskID in strDict:
            thread = strDict[taskID]
            if '%' in thread:
                thread = thread % 0
        if cycleDeltaTime == 0:
            cpuLoad = 0
        else:
            cpuLoad = taskDeltaTime*100.0/cycleDeltaTime
        timeoutStr = 'endless'
        if timeoutCounter != 0xFFFFFFFF:
            timeoutStr = '%d' % timeoutCounter
        stateStr = '%d' % state
        if state == 0:
            stateStr = 'Running'
        elif state == 4:
            stateStr = 'Ready'
        elif state & 2:
            stateStr = 'Wait'
            if strType in strDict:
                str = strDict[strType]
                if '%' in str:
                    str = str % strValue
                stateStr += ' ' + str
        print('%10s %5.2f %8s %5d/%-5d %10d %d %-16s %d %d' % (thread, taskDeltaTime*100.0/cycleDeltaTime, timeoutStr, usedStackSize*4,stackSize*4, contextSwitches, priorityState,stateStr, mem,numberMem))
    pass
def parsePackageLogging(pkg,strType,parameterCount):
    offset = 28
    format = '%s'
    if strType in strDict:
        format = strDict[strType]
    parameter = []
    while parameterCount > 0:
        parameterCount -= 1
        type = pkg[offset]
        offset += 1
        if type==0x01: # String (0-terminated string)
            str = ''
            while pkg[offset]:
                str += chr(pkg[offset])
                offset += 1
            offset += 1
            parameter.append(str)
        elif type==0x02: # Buffer (16-bit size plus size-bytes data)
            buffer_size = struct.unpack('<H', pkg[offset:offset+2])[0]
            offset += 2
            parameter.append(binascii.hexlify(pkg[offset:offset+buffer_size]))
            offset += buffer_size
        elif type==0x03: # Par (4 bytes integer)
            val = struct.unpack('<I', pkg[offset:offset+4])[0]
            offset += 4
            parameter.append(val)
        elif type==0x04: # IP (4 bytes)
            parameter.append('%d.%d.%d.%d' % (pkg[offset],pkg[offset+1],pkg[offset+2],pkg[offset+3]))
            offset += 4
        elif type==0x05: # MAC (6 bytes)
            parameter.append('%02X:%02X:%02X:%02X:%02X:%02X' % (pkg[offset],pkg[offset+1],pkg[offset+2],pkg[offset+3],pkg[offset+4],pkg[offset+5]))
            offset += 6
        elif type==0x06: # TCPflags (4 bytes + 1 byte)
            acknowledgment_number,tcp_flags = struct.unpack('<IB', pkg[offset:offset+5])
            offset += 5
            parameter.append('%ld %02x' % (acknowledgment_number,tcp_flags))
        else: # these type don't seem to exist
            parameter.append(binascii.hexlify(pkg[offset:]))
    try:
        pcount = format.replace('%%', '').count('%')
        if len(parameter) > pcount:
            print((format % tuple(parameter[:pcount])) + ' ' + parameter[pcount:])
        else:
            print(format % tuple(parameter))
    except:
        print(format,parameter)
    pass
def parsePackageContent(pkg):
    header,size,xorval,parameterCount,strType,eventCounter,idlems,currentTime,ipaddr,usedMem,f24 = struct.unpack('<HHBBHHHIIII', pkg[:28])
    timestr = datetime.utcfromtimestamp(currentTime + 1230768000 + idlems / 1000).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
    ipaddrstr = '%d.%d.%d.%d' % (ipaddr&0xFF,(ipaddr>>8)&0xFF,(ipaddr>>16)&0xFF,(ipaddr>>24)&0xFF)
    # There are two independent event counters, one for strType < 0xFFF0 and one for strType >= 0xFFF0
    # This can be used to filter out duplicates
    if strType >= 0xFFF0:
        #print('%s' % (timestr), end=' ')
        if strType == 0xFFFF:
            #parsePackageSystem(pkg)
            pass
        elif strType == 0xFFFE:
            #parsePackageHardware(pkg)
            pass
        elif strType >= 0xFFF0 and strType <= 0xFFFD:
            #parsePackageTasks(pkg,strType)
            pass
    if strType < 0xFFF0:
        print('%s' % (timestr), end=' ')
        parsePackageLogging(pkg,strType,parameterCount)
        pass
def parsePackage(data):
    # validate package
    if len(data)<2:
        return data
    header = data[0] + (data[1]<<8)
    if header == 0x1F1F: # End of package marker
        data = data[2:]
    elif header == 0xFA1F and len(data) >= 4:
        size = data[2] + (data[3]<<8)
        if size <= len(data):
            pkg = data[:size]
            data = data[size:]
            xor = 0x00
            for i in range(5,size):
                xor ^= pkg[i]
            if xor == pkg[4]:
                parsePackageContent(pkg)
    else:
        data = data[2:]
    return data

def monitorserver_logger(name):
    UDP_IP = LOCAL_IP
    UDP_PORT = 7777

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # Internet UDP
    sock.bind((UDP_IP, UDP_PORT))

    while True:
        data, addr = sock.recvfrom(2048) # buffer size is 2048 bytes
        while len(data) >= 2:
            data = parsePackage(data)

class Proxy(SimpleHTTPRequestHandler):
    def do_GET(self):
        print(self.path)
        if self.path.startswith('/?'): # port 80 (follows by Miniserver serial number, this example excepts any serial number)
            self.send_response(200, 'OK')
            self.send_header('Content-type', 'application/xml')
            self.end_headers()
            self.wfile.write(bytes('''<?xml version="1.0"?>
<Log Version="10" LogKeep="true" NoIPchange="false">
  <LogMode>on</LogMode>
  <LogDest>/dev/udp/%s/%d</LogDest>
  <LogLevelCommon>moreinfo</LogLevelCommon>
  <LogLevelSPS>moreinfo</LogLevelSPS>
  <LogLevelProtocol>moreinfo</LogLevelProtocol>
  <LogLevelBus>moreinfo</LogLevelBus>
  <LogLevelFilesystem>moreinfo</LogLevelFilesystem>
  <LogLevelNet>moreinfo</LogLevelNet>
</Log>''' % (UDP_IP,UDP_PORT), 'UTF-8'))
        else:
            self.send_response(404)
            self.end_headers()

def monitorserver_proxy(name):
    httpd = HTTPServer((LOCAL_IP, 80), Proxy)
    httpd.serve_forever()

print('Starting Monitor Server Proxy...')
x = threading.Thread(target=monitorserver_proxy, args=(1,), daemon=True)
x.start()

print('Starting Monitor Server Logger...')
y = threading.Thread(target=monitorserver_logger, args=(1,), daemon=True)
y.start()

x.join()
