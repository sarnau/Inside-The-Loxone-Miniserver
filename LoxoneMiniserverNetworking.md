# Loxone Miniserver Networking
 
The Miniserver allows connections from other computers and can talk to other systems. This document will try to document all ways the Miniserver communicates.

Whenever I need to mention the 6-byte serial number of the Miniserver, I will use `504F11223344` as the serial number. You obviously need to use your own serial number.

## Finding a Miniserver in the Network

## Booting the Miniserver

1. UDP dynamic DNS update
2. HTTP dynamic DNS check via dns.loxonecloud.com:80
3. HTTP request weather forecast
4. NTP clock requests
5. Send log information

## Known Loxone Servers

| Server name | Description |
| ----------- | ----------- |
| [clouddns.loxone.com]() | Cloud Service DNS |
| [mail.loxonecloud.com]() | Loxone Cloud Mailer Object to send emails |
| [push.loxonecloud.com]() | Push Notificationens |
| [update.loxone.com]() | Checking for "Automatic Updates" (can be disabled in Loxone Config), also used in the webinterface to show ads for Loxone products. It can't be disabled there |
| [monitorserver.loxone.com]() | Loxone Support Monitoring (not enabled by default) |
| [log.loxone.com]() | Loxone Log (can be disabled in Loxone Config, sends support information to Loxone) |
| [weather.loxone.com]() | Weather service |
| [caller.loxone.com]() | Caller Object for voice callbacks from the Miniserver |

[push.loxonecloud.com](), [monitorserver.loxone.com](), [weather.loxone.com](), [clouddns.loxone.com]() and [dns.loxonecloud.com]() are all services running on the same Amazon server.

[caller.loxone.com]() is running on a Loxone server from Netplanet in Vienna.

[log.loxone.com]() is running on a Loxone server directly at the Loxone headquarter in Kollerschlag, Austria.


## Dynamic DNS (clouddns.loxone.com)

Loxone offers a dynamic DNS service, which allows finding your own servers via the internet, based on the assumption that your home IP address is not static (which it typically is not). This still requires the Firewall to be open for the Miniserver. In general it is probably still better to have a VPN connection to your home, than relying on security of your home automation server. The advantage of this system is: it is easy and reasonably secure (if there are no security issues in the Miniserver and your passwords are good). That said: you are still exposing your server to the internet!

### Publishing the IP address

To publish the IP, the Miniserver sends a single UDP request to the Loxone Cloud Service DNS on port 7700 with the following content:

    504F11223344,80,00000000,AABBCCDDEEFF0011

- `504F11223344` is the 6-byte serial number of the Miniserver. All Miniservers start with `504F`.
- 80 is the port number under which the Miniserver responds to HTTP requests for the Web-Interface
- 00000000 is the version number of the `WebInterfaceAGZ`
- `AABBCCDDEEFF0011` is an 8 byte unique key. This key is constant for the Miniserver and acts as a validation for the serial number. It protects Loxone against bad guys pushing random serial numbers to their DNS server.

But you might be able to spot a problem with security: because the request is not encrypted, any bad guy who manages to collect one request can then send it's own request to Loxone. The next time you try to connect to your server, you then could end up on a compromised server from the bad guy, telling him your admin name and password!

### Finding an IP address

To find the IP address for a Miniserver, you need to know it's serial number and simply send this request: [http://dns.loxonecloud.com/504F11223344]()

This will get resolved to: [http://504F11223344.dns.loxonecloud.com]()

which forwards directly to your Miniserver.


### Cloud Service Caller (caller.loxone.com)

The Cloud Service Caller is an automated phone callback service from Loxone. It can be configured in Loxone Config. Whenever it is triggered, the Miniserver sends the following request:

[http://caller.loxone.com:80/cgi-bin/loxlive/call.pl?extip=http://dns.loxonecloud.com/504F11223344/dev/sps/io/caller/11389406-009a-2bdf-ffff1402153adf25/&loxid=504F11223344&tel=004912345678&text=Schalter%20aus]()

You can see the following parts in the request:

- `extip`=[http://dns.loxonecloud.com/504F11223344/dev/sps/io/caller/11223344-5566-7788-99aabbccddeeff00]() - `11223344-5566-7788-99aabbccddeeff00` is the object ID for the Caller Service in the Loxone Config file.
- `loxid`=`504F11223344` - serial number of the Miniserver, the Miniserver needs to have a paid subscription of the  Cloud Service Caller.
- `tel`=`004912345678` - phone number, which need to be called
- `text`=`Schalter%20aus` - the text which will be said to you via text-to-speech

This request triggers a http reply, which content can be ignored.

    HTTP/1.1 200 OK\r\n
    Date: Mon, 20 Feb 2019 00:11:22 GMT\r\n
    Server: Apache/2.4.7 (Ubuntu)\r\n
    X-Powered-By: PHP/5.5.9-1ubuntu4.14\r\n
    Vary: Accept-Encoding\r\n
    Transfer-Encoding: chunked\r\n
    Content-Type: text/html\r\n
    \n\r\n
    4a\r\n == Length of following line without the \r\n suffix
    2018-02-20 01:11:22:11.22.33.44:-----------------------------------<br>\n\r\n
    3b\r\n
    2018-02-20 01:11:22:11.22.33.44:TEXT2SPEECH START...<br>\n\r\n
    46\r\n
    2018-02-20 01:11:22:11.22.33.44:MINISERVER 504F11223344 ACTIVE.<br>\n\r\n
    3d\r\n
    2018-02-20 01:11:22:11.22.33.44:CALL TO 4912345678.<br>\n\r\n

Within a few seconds you will get a phone call with the announcement. You can then enter a code, which will be forwarded to your Miniserver (assuming the dynamic DNS is working), it does so by using the `extip` URL and appending the code, like so for the code `1`: [http://dns.loxonecloud.com/504F11223344/dev/sps/io/caller/11223344-5566-7788-99aabbccddeeff00/1]()

The Miniserver will reply accordingly, if the change was accepted:

    GET /dev/sps/io/caller/11223344-5566-7788-99aabbccddeeff00/1 HTTP/1.1\r\n
    Host: 11.22.33.44\r\n
    Accept: */*\r\n
    \r\n
    HTTP/1.1 200 OK\r\n
    Access-Control-Allow-Origin: \r\n
    Access-Control-Allow-Credentials: true\r\n
    Content-Type: text/xml\r\n
    Content-Length: 131\r\n
    Keep-Alive: timeout=10, max=1000\r\n
    Connection: Keep-Alive\r\n
    \r\n
    <?xml version="1.0" encoding="utf-8"?>
    <LL control="dev/sps/io/11223344-5566-7788-99aabbccddeeff11/pulse" value="1" Code="200"/>\r\n

As you can see, the whole communication is not encrypted. Attacks are possible, but limited:

- you need to know the Miniserver serial number, which has to have a paid subscription
- the request to trigger a callback has to come from the IP address of the Miniserver

As you can see: this would be easily possible for anybody within your home network. From this network you can fake callbacks with no problem. This could be especially tricky if the callback allows security relevant things, like unlocking doors.

Could somebody from the outside hack this? Potentially, but only in a small window:

- you need to catch the Caller request
- within 2 minutes, you can trigger the callback URL, even with different parameters

Is this all a big risk? Probably not, but Loxone could have done better – even without SSL.


## Weather Service (weather.loxone.com)

Loxone also offers a subscription to weather service. This service is offered via [Meteo Blue](https://www.meteoblue.com), but routed via a Loxone server [weather.loxone.com](), which validates the subscription.

Several times a day the Miniserver sends the following request: [http://weather.loxone.com:6066/forecast/?user=loxone_504F11223344&coord=13.8408,48.6051&asl=20&format=1]()

You notice a couple of parameters:

- user=loxone_504F11223344 - this is the user account based on the serial number of the Miniserver 
- coord=13.8408,48.6051 - GPS location for the weather report (longitude,latitude). As entered in Loxone Config.
- asl=200 - altitude over sea level in meter. Not sure why this is needed, because `coord` implies it. Can be entered as Elevation in Loxone Config. This parameter seems optional, but the Miniserver always provides it.
- format=1 - the Weather server can return two different report formats: `format=0`, which is XML or `format=1`, which is a mixture between XML and CSV from Meteo Blue. The Miniserver understands both detects the right format automatically.

If have not found out, when the XML/CSV format is requested, it seems that it can happen after a reboot. Typically the Miniserver seems to request XML. But as I said, the server could ignore the format and simply return whatever is more convenient.

Here a shortened example for the XML/CSV format. I've only shown the first 2 and last 2 entries. Overall it is 181 entries large. As you can see it has a header, describing the individual columns in the CSV block below. It also has a `valid_until` entry, which contains the subscription expiry date. The Miniserver will start warning, once you hit that date. `Kollerschlag` is a bug, it seems to not know the city, so it falls back to `Kollerschlag`. Longitude and latitude are correct, as well as the elevation. Sunrise/Sunset are also provided, but the Miniserver does it's own calculation locally.

The report has to be hourly and lasts about 7 days into the future. The Miniserver ignores a lot of the data, especially the cloud coverage at different altitudes does not seem to be used.

    <mb_metadata>
    id;name;longitude;latitude;height (m.asl.);country;timezone;utc-timedifference;sunrise;sunset;
    local date;weekday;local time;temperature(C);feeledTemperature(C);windspeed(km/h);winddirection(degr);wind gust(km/h);low clouds(%);medium clouds(%);high clouds(%);precipitation(mm);probability of Precip(%);snowFraction;sea level pressure(hPa);relative humidity(%);CAPE;picto-code;radiation (W/m2);
    </mb_metadata><valid_until>2018-04-25</valid_until>
    <station>
    ;Kollerschlag;13.84°E;48.61°N ;200;;CEST;UTC+2.0;07:06;11:22;
    01.02.2018;Mon;14;  3.3;  2.3; 12;280; 12; 10; 10;  0;  0.0;  0;0.0;1005; 50;    33;4; 200;
    01.02.2018;Mon;15;  5.6;  1.7; 11;244; 12; 71;  6;  0;  0.0;  0;0.0;1005; 54;    78;5; 100;
    …
    10.02.2018;Tue;01;  2.0; -2.0; 30;170; 37; 20; 37; 10;  0.0; 19;0.0;1021; 70;     2;8; 200;
    10.02.2018;Tue;02;  1.9; -1.5; 30;180; 40;  2; 55; 17;  0.0; 17;0.0;1023; 70;    20;5;   0;
    </station>

Here a shortened example for the XML format. I've only shown the first entry. Overall it is 181 entries large.

    <?xml version="1.0"?>
    <metdata_feature_collection p="m" valid_until="2018-04-25">
        <metdata>
            <timepoint>2018-02-01T12:00:00</timepoint>
            <TT>3.3</TT>
            <FF>2.6111111111111</FF>
            <DD>111</DD>
            <RR1H>0.0</RR1H>
            <PP0>1005</PP0>
            <RH>50</RH>
            <HI>0.3</HI>
            <RAD>200</RAD>
            <WW>2</WW>
            <FFX>3.8</FFX>
            <LC>10</LC>
            <MC>10</MC>
            <HC>0</HC>
            <RAD4C>1</RAD4C>
        </metdata>
        …
    </metdata_feature_collection>

The keys for one `metdata` entry are as follows

|       Key | Description |
| --------- | ----------- |
| timepoint | Date/Time for this data point |
|        TT | Temperature in C |
|        TD | Dewpoint in C |
|        FF | Wind Speed in m/s |
|        DD | Wind Direction |
|      RR1H | Percipitation in mm |
|       PP0 | Pressure in hPa |
|        RH | Relative Huminity in % |
|        HI | Feel Temperature in C |
|        WW | Weathertype (picto-code) |
|       FFX | Gusts in m/s |
|        LC | Low Clouds in % |
|        MC | Medium Clouds in % |
|        HC | High Clouds in % |
|       RAD | Absolute Radiation (Solar Irradiation (0-20% (<60), 20-40% (<100), 40-100%)) |
|      RRAD | Relative Radiation |
|     RAD4C | Radiation (UV Index) |

The picto-codes for the weather icons seem to come from [Meteoblue](https://content.meteoblue.com/en/help/standards/symbols-and-pictograms)

| Picto-Code | Description |
| :--------: | :---------- |
|  1         | Clear, cloudless sky (Loxone: Wolkenlos) |
|  2         | Clear, few cirrus (Loxone: Wolkenlos) |
|  3         | Clear with cirrus (Loxone: Heiter) |
|  4         | Clear with few low clouds (Loxone: Heiter) |
|  5         | Clear with few low clouds and few cirrus (Loxone: Heiter) |
|  6         | Clear with few low clouds and cirrus (Loxone: Heiter) |
|  7         | Partly cloudy (Loxone: Heiter) |
|  8         | Partly cloudy and few cirrus (Loxone: Heiter) |
|  9         | Partly cloudy and cirrus (Loxone: Wolkig) |
| 10         | Mixed with some thunderstorm clouds possible (Loxone: Wolkig) |
| 11         | Mixed with few cirrus with some thunderstorm clouds possible (Loxone: Wolkig) |
| 12         | Mixed with cirrus and some thunderstorm clouds possible (Loxone: Wolkig) |
| 13         | Clear but hazy (Loxone: Wolkenlos) |
| 14         | Clear but hazy with few cirrus (Loxone: Heiter) |
| 15         | Clear but hazy with cirrus (Loxone: Heiter) |
| 16         | Fog/low stratus clouds (Loxone: Nebel) |
| 17         | Fog/low stratus clouds with few cirrus (Loxone: Nebel) |
| 18         | Fog/low stratus clouds with cirrus (Loxone: Nebel) |
| 19         | Mostly cloudy (Loxone: Stark bewölkt) |
| 20         | Mostly cloudy and few cirrus (Loxone: Stark bewölkt) |
| 21         | Mostly cloudy and cirrus (Loxone: Stark bewölkt) |
| 22         | Overcast (Loxone: Bedeckt) |
| 23         | Overcast with rain (Loxone: Regen) |
| 24         | Overcast with snow (Loxone: Schneefall) |
| 25         | Overcast with heavy rain (Loxone: Starker Regen) |
| 26         | Overcast with heavy snow (Loxone: Starker Schneefall) |
| 27         | Rain, thunderstorms likely (Loxone: Kräftiges Gewitter) |
| 28         | Light rain, thunderstorms likely (Loxone: Gewitter) |
| 29         | Storm with heavy snow (Loxone: Starker Schneeschauer) |
| 30         | Heavy rain, thunderstorms likely (Loxone: Kräftiges Gewitter) |
| 31         | Mixed with showers (Loxone: Leichter Regenschauer) |
| 32         | Mixed with snow showers (Loxone: Leichter Schneeschauer) |
| 33         | Overcast with light rain (Loxone: Leichter Regen) |
| 34         | Overcast with light snow (Loxone: Leichter Schneeschauer) |
| 35         | Overcast with mixture of snow and rain (Loxone: Schneeregen) |

## Log Server

log.loxone.com

982 Bytes

Contains the Miniserver serial number and the name of the author.

7707	UDP	Loxone Support Crashlog


## Web-Interface

The Miniserver offers a HTTP interface at the HTTP port 80 (this port can be changed in Loxone Config). You can use a webbrowser to use the "Loxone Smart Home" directly on the server.

## FTP-Interface

The Miniserver offers a FTP interface at the FTP port 21 (this port can be changed in Loxone Config). This is used to upload a configuration or download backups.

