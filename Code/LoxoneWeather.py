#!/usr/bin/env python
# -*- coding: utf-8 -*-

import SocketServer
import SimpleHTTPServer
import urllib
import json
import sys
import datetime
import requests
import urlparse
import os

# HTTP Proxy Server for the Loxone Weather Service
# (Can be run on a Raspberry Pi)

# You need a private DNS server, which the Miniserver uses. That DNS server needs
# to forward `weather.loxone.com` to this server!

# Visit https://darksky.net to setup an account and use an evaluation account
# (1000 requests per day is more than enough for your server)
# The 'SECRET KEY' needs to be added:
DARKSKY_SECRET_KEY = '### SECRET KEY ###'

licenseExpiryDate = datetime.datetime(2049,12,31, 0, 0)
LOXONE_WEATHER_SERVICE_PORT = 6066

def downloadReport(longitude, latitude, asl):
    payload = {'extend': 'hourly', 'lang': 'de', 'units': 'ca'}
    r = requests.get('https://api.darksky.net/forecast/'+DARKSKY_SECRET_KEY+'/{lon:.3f},{lat:.2f}'.format(lon=longitude,lat=latitude), params=payload)
    if r.status_code == 200:
        ret = r.content
    else:
        print 'Error %d' % (r.status_code)
        ret = None
    return ret

# Generate an icon for Loxone based on the Meteoblue picto-codes
# <https://content.meteoblue.com/en/help/standards/symbols-and-pictograms>
#  1	Clear, cloudless sky (Loxone: Wolkenlos)
#  2	Clear, few cirrus (Loxone: Wolkenlos)
#  3	Clear with cirrus (Loxone: Heiter)
#  4	Clear with few low clouds (Loxone: Heiter)
#  5	Clear with few low clouds and few cirrus (Loxone: Heiter)
#  6	Clear with few low clouds and cirrus (Loxone: Heiter)
#  7	Partly cloudy (Loxone: Heiter)
#  8	Partly cloudy and few cirrus (Loxone: Heiter)
#  9	Partly cloudy and cirrus (Loxone: Wolkig)
# 10	Mixed with some thunderstorm clouds possible (Loxone: Wolkig)
# 11	Mixed with few cirrus with some thunderstorm clouds possible (Loxone: Wolkig)
# 12	Mixed with cirrus and some thunderstorm clouds possible (Loxone: Wolkig)
# 13	Clear but hazy (Loxone: Wolkenlos)
# 14	Clear but hazy with few cirrus (Loxone: Heiter)
# 15	Clear but hazy with cirrus (Loxone: Heiter)
# 16	Fog/low stratus clouds (Loxone: Nebel)
# 17	Fog/low stratus clouds with few cirrus (Loxone: Nebel)
# 18	Fog/low stratus clouds with cirrus (Loxone: Nebel)
# 19	Mostly cloudy (Loxone: Stark bewölkt)
# 20	Mostly cloudy and few cirrus (Loxone: Stark bewölkt)
# 21	Mostly cloudy and cirrus (Loxone: Stark bewölkt)
# 22	Overcast (Loxone: Bedeckt)
# 23	Overcast with rain (Loxone: Regen)
# 24	Overcast with snow (Loxone: Schneefall)
# 25	Overcast with heavy rain (Loxone: Starker Regen)
# 26	Overcast with heavy snow (Loxone: Starker Schneefall)
# 27	Rain, thunderstorms likely (Loxone: Kräftiges Gewitter)
# 28	Light rain, thunderstorms likely (Loxone: Gewitter)
# 29	Storm with heavy snow (Loxone: Starker Schneeschauer)
# 30	Heavy rain, thunderstorms likely (Loxone: Kräftiges Gewitter)
# 31	Mixed with showers (Loxone: Leichter Regenschauer)
# 32	Mixed with snow showers (Loxone: Leichter Schneeschauer)
# 33	Overcast with light rain (Loxone: Leichter Regen)
# 34	Overcast with light snow (Loxone: Leichter Schneeschauer)
# 35	Overcast with mixture of snow and rain (Loxone: Schneeregen)

def loxoneWeatherIcon(weatherReportHourly):
    iconDarksky = weatherReportHourly['icon']
    if iconDarksky == 'clear-day' or iconDarksky == 'clear-night':
        iconID = 1 # wolkenlos
    elif iconDarksky == 'rain':
        iconID = 23 # Regen
    elif iconDarksky == 'snow':
        iconID = 24 # Schneefall
    elif iconDarksky == 'sleet':
        iconID = 35 # Schneeregen
#    elif iconDarksky == 'wind':
#        pass
    elif iconDarksky == 'fog':
        iconID = 16 # Nebel
    elif iconDarksky == 'cloudy':
        iconID = 7 # Wolkig
    elif iconDarksky == 'partly-cloudy-day' or iconDarksky == 'partly-cloudy-night':
        iconID = 7 # Wolkig
    elif iconDarksky == 'hail':
        iconID = 35 # Schneeregen
    elif iconDarksky == 'thunderstorm':
        iconID = 28 # Gewitter
#    elif iconDarksky == 'tornado':
#        iconID = 29 # kräftiges Gewitter
    else:
        iconID = 7 # Wolkig

    # fix the cloud cover icon
    if iconID == 7:
        cloudCover = weatherReportHourly['cloudCover']
        if cloudCover<0.125:
            iconID = 1 # Wolkenlos und sonnig
        elif cloudCover<0.5:
            iconID = 3 # Heiter und leicht bewölkt
        elif cloudCover<0.75:
            iconID = 9 # bewölkt bis stark bewölkt
        elif cloudCover<0.875:
            iconID = 19 # Stark bewölkt
        else:
            iconID = 22 # fast bedeckt und bedeckt

    # add rain, if necessary
    if iconID == 23 and weatherReportHourly['precipIntensity'] > 0.0:
        if weatherReportHourly['precipIntensity']<0.5:
            iconID = 33 # Leichter Regen
        elif weatherReportHourly['precipIntensity']<=4:
            iconID = 23 # Regen
        else:
            iconID = 25 # Starker Regen
    return iconID


# Loxone is using www.meteoblue.com for their weather data, it's the same format!
def generateCSV(weatherReport, asl):
    csv = ""
    csv += "<mb_metadata>\n"
    csv += "id;name;longitude;latitude;height (m.asl.);country;timezone;utc-timedifference;sunrise;sunset;\n"
    csv += "local date;weekday;local time;temperature(C);feeledTemperature(C);windspeed(km/h);winddirection(degr);wind gust(km/h);low clouds(%);medium clouds(%);high clouds(%);precipitation(mm);probability of Precip(%);snowFraction;sea level pressure(hPa);relative humidity(%);CAPE;picto-code;radiation (W/m2);\n"
    csv += "</mb_metadata><valid_until>{:{dfmt}}</valid_until>\n".format(licenseExpiryDate, dfmt='%Y-%m-%d')
    # CAPE = Convective available potential energy <https://en.wikipedia.org/wiki/Convective_available_potential_energy>
    csv += "<station>\n"
    longitude = weatherReport['longitude']
    if longitude < 0:
        longitude = -longitude
        eastwest = 'W'
    else:
        eastwest = 'E'
    latitude = weatherReport['latitude']
    if latitude < 0:
        latitude = -latitude
        northsouth = 'S'
    else:
        northsouth = 'N'

    sunriseTime = '{:{sunrise}}'.format(datetime.datetime.fromtimestamp(weatherReport['daily']['data'][0]['sunriseTime']), sunrise='%H:%M')
    sunsetTime = '{:{sunset}}'.format(datetime.datetime.fromtimestamp(weatherReport['daily']['data'][0]['sunsetTime']), sunset='%H:%M')
    csv += ";Kollerschlag;{lon:.2f}°{eastwest};{lat:.2f}°{northsouth} ;{asl};;CEST;UTC{utcTimedifference:+.1f};{sunrise};{sunset};\n".format(lon=longitude,eastwest=eastwest,lat=latitude,northsouth=northsouth,asl=asl,utcTimedifference=weatherReport['offset'],sunrise=sunriseTime,sunset=sunsetTime)
    for hourly in weatherReport['hourly']['data']:
        time = datetime.datetime.fromtimestamp(hourly['time'])
        iconID = loxoneWeatherIcon(hourly)
        csv += '{:{localDate};{weekday};{localTime}};'.format(time, localDate='%d.%m.%Y', weekday='%a', localTime='%H')
        csv += '{:5.1f};'.format(hourly['temperature'])
        csv += '{:5.1f};'.format(hourly['apparentTemperature'])
        csv += '{:3.0f};'.format(hourly['windSpeed'])
        csv += '{:3.0f};'.format(hourly['windBearing'])
        csv += '{:3.0f};'.format(hourly['windGust'])
        csv += '{:3.0f};'.format(0.0)
        csv += '{:3.0f};'.format(hourly['cloudCover']*100)
        csv += '{:3.0f};'.format(0.0)
        csv += '{:5.1f};'.format(hourly['precipIntensity'])
        csv += '{:3.0f};'.format(hourly['precipProbability'])
        csv += '{:3.1f};'.format(0.0)
        csv += '{:4.0f};'.format(hourly['pressure'])
        csv += '{:3.0f};'.format(hourly['humidity']*100)
        csv += '{:6d};'.format(0)
        csv += '{:d};'.format(iconID)
        csv += '{:4.0f};'.format(hourly['uvIndex']*100)
        csv += '\n'
    csv += "</station>\n"
    return csv

def generateXML(weatherReport, asl):
    xml = '<?xml version="1.0"?>'
    xml += '<metdata_feature_collection p="m" valid_until="{:{dfmt}}">'.format(licenseExpiryDate, dfmt='%Y-%m-%d')

    for hourly in weatherReport['hourly']['data']:
        time = datetime.datetime.fromtimestamp(hourly['time'])
        iconID = loxoneWeatherIcon(hourly)
        xml += '<metdata>'
        xml += '<timepoint>{:%Y-%m-%dT%H:%M:%S}</timepoint>'.format(time)
        xml += '<TT>{:.1f}</TT>'.format(hourly['temperature']) # Temperature (C)
        xml += '<FF>{:.1f}</FF>'.format(hourly['windSpeed']*1000/3600) # Wind Speed (m/s)
        windBearing = hourly['windBearing']-180
        if windBearing < 0:
            windBearing += 360
        xml += '<DD>{:.0f}</DD>'.format(windBearing) # Wind Speed (Direction)
        xml += '<RR1H>{:5.1f}</RR1H>'.format(hourly['precipIntensity']) # Rainfall (mm)
        xml += '<PP0>{:.0f}</PP0>'.format(hourly['pressure']) # Pressure (hPa)
        xml += '<RH>{:.0f}</RH>'.format(hourly['humidity']*100) # Humidity (%)
        xml += '<HI>{:.1f}</HI>'.format(hourly['apparentTemperature']) # Perceived Temperature (C)
        xml += '<RAD>{:4.0f}</RAD>'.format(hourly['uvIndex']*100) # Solar Irradiation (0-20% (<60), 20-40% (<100), 40-100%)
        xml += '<WW>2</WW>' # Icon
        xml += '<FFX>{:.1f}</FFX>'.format(hourly['windGust']*1000/3600) # Wind Speed (m/s)
        xml += '<LC>{:.0f}</LC>'.format(0) # low clouds
        xml += '<MC>{:.0f}</MC>'.format(hourly['cloudCover']*100) # medium clouds
        xml += '<HC>{:.0f}</HC>'.format(0) # high clouds
        xml += '<RAD4C>{:.0f}</RAD4C>'.format(hourly['uvIndex']) # UV Index
        xml += '</metdata>'
    xml += '</metdata_feature_collection>\n'
    return xml

class Proxy(SimpleHTTPServer.SimpleHTTPRequestHandler):
    def do_GET(self):
        path,query = self.path.split('?')
        query = urlparse.parse_qs(query)
        self.server_version = 'Apache/2.4.7 (Ubuntu)'
        self.sys_version = ''
        self.protocol_version = 'HTTP/1.1'
        if path == '/forecast/':
            self.send_response(200)
            self.send_header('Vary', 'Accept-Encoding')
            self.send_header('Connection', 'close')
            self.send_header('Transfer-Encoding', 'chunked')
            if 'asl' in query:
                asl = int(query['asl'][0])
            else:
                asl = 0
            lat,long = query['coord'][0].split(',')
            if os.path.isfile('weather.json'):
                jsonReport = json.loads(open('weather.json').read())
            else:
                jsonReport = json.loads(downloadReport(float(long), float(lat), asl))
            if 'format' in query and int(query['format'][0]) == 1:
                reply = generateCSV(jsonReport, asl)
                self.send_header('Content-Type', 'text/plain')
            else:
                reply = generateXML(jsonReport, asl)
                self.send_header('Content-Type', 'text/xml')
            self.end_headers()
            self.wfile.write("%x\r\n%s\r\n" % (len(reply), reply))
            self.wfile.write("0\r\n\r\n")
        else:
            print(path)
            print(urlparse.parse_qs(query))
            self.send_response(404)
            self.end_headers()

SocketServer.TCPServer.allow_reuse_address = True
httpd = SocketServer.ForkingTCPServer(('', LOXONE_WEATHER_SERVICE_PORT), Proxy)
httpd.serve_forever()
