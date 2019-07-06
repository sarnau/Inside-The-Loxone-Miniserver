# Loxone Miniserver Networking
 
The Miniserver allows connections from other computers and can talk to other systems. This document will try to document all ways the Miniserver communicates.

Whenever I need to mention the 6-byte serial number of the Miniserver, I will use `504F11223344` as the serial number. You obviously need to use your own serial number.

## Known external Loxone Servers

| Server name | Description | Loxone Documentation Link |
| ----------- | ----------- | :------------------------- |
| <https://www.loxone.com> | Their main website, also hosts the News Feed. | <https://www.loxone.com> |
| [clouddns.loxone.com]() | Loxone DNS Service | <https://www.loxone.com/enen/kb/dns-service/> |
| [mail.loxonecloud.com]() | Loxone Mailer Service to send emails | <https://www.loxone.com/enen/kb/mailer-service/> |
| [push.loxonecloud.com]() | Push Notifications Service | <https://www.loxone.com/enen/kb/push-notifications/> |
| [weather.loxone.com]() | The subscription-based Loxone Weather Service | <https://www.loxone.com/enen/kb/weather-service/> |
| [caller.loxone.com]() | The subscription-based Caller Service for text-to-speech callbacks for notifications | <https://www.loxone.com/enen/kb/caller-service/> |
| [update.loxone.com]() | Update server for the hardware | <https://www.loxone.com/enen/kb/installing-updates/> |
| [monitorserver.loxone.com]() | Loxone Monitor | <https://www.loxone.com/enen/kb/loxone-monitor/> |
| [log.loxone.com]() | Loxone Log (can be disabled in Loxone Config, sends support information to Loxone) | |

[clouddns.loxone.com](), [push.loxonecloud.com](), [weather.loxone.com](),  and [dns.loxonecloud.com]() are all services running on the same Amazon server.

[mail.loxonecloud.com](), [monitorserver.loxone.com]() is running on Host Europe GmbH.

[update.loxone.com]() is running on an running on Amazon cloud server.

[caller.loxone.com]() is running on a Loxone server from Netplanet in Vienna.

[log.loxone.com]() is running on a Loxone server directly at the Loxone headquarter in Kollerschlag, Austria.

## Known used ports of the Miniserver

| Type | Port | Description |
| :--: | :--: | :---------- |
| TCP  | 21   | FTP server |
| TCP  | 23   | Telnet (stream) |
| TCP  | 80   | HTTP server (also: stream) |
| TCP  | 8080 | HTTP |
| UDP  | 68   | DHCP |
| UDP  | 123  | NTP |
| UDP  | 137  | NetBIOS NS |
| UDP  | 162  | smtp (stream) |
| UDP  | 514  | syslog (stream) |
| UDP  | 1900 | SSDP |
| UDP  | 3671 | EIBnet/IP tunnel protocol |
| UDP  | 5000 | Intercom |
| UDP  | 5353 | mDNS |
| UDP  | 7070/7071 | Miniserver send/answer – used for discovery |
| UDP  | 7072/7073 | Loxone Gateway (from/to ports) |
| UDP  | 7074/7075 | Loxone Gateway (from/to ports) (alternative ports) |
| UDP  | 7076 | Loxone Gateway |
| UDP  | 7077 | Intercom |
| UDP  | 7078 | Bus Handler (unknown) |
| UDP  | 7090 | Keba Wallbox (see <https://www.keba.com/web/downloads/e-mobility/KeContact_P20_P30_UDP_ProgrGuide_en.pdf>) |
| UDP  | 7091 | Loxone Multi Media Server |
| UDP  | 7700 | Loxone DNS Service (send only) |
| UDP  | 7707 | Loxone Log Server (send only) |
| UDP  | 7777 | Loxone Monitor (send only) |
| UDP  | 8110 | Intercom Xl |
| UDP  | 8112 | Intercom SIP |
| UDP  | 55895 | UPnp search |

The firewall in the Miniserver only allows the configured HTTP port (typically 80) and FTP port (typically 21) to pass through. Additionally HTTPS (port 443) and port 7091 are always allowed. All other will be blocked.

DHCP/NTP/NetBIOS/SSDP/mDNS/UPnp are typical ports to detect or be detected by other network devices. There are no special Miniserver related services being offered by them.

The stream ports are possible destinations for the Loxone configuration, like `/dev/udp`.

The Ports starting at 7070 seem to be a reserved range of UDP ports used by the Miniserver. 7700,7707,7777 are for sending to Loxone specific services, they can all be disabled, if necessary.

The Intercom seems to use a range of ports (5000,7077,8110,8112)


## Finding a Miniserver in the local network

There are two ways to search for a Miniserver in a local network:

1. UDP Broadcast
2. Simple Service Discovery Protocol

To find a Miniserver from outside the local network, you either need to use the DNS service from Loxone or use a VPN setup for your local network.

### UDP Broadcast

To search via UDP Broadcast, broadcast a single 0x00 byte to the UDP port 7070. while listening on UDP port 7071 for about 3s.

Miniservers will reply with one package:

    [LoxLIVE: Loxone Miniserver 192.168.178.32:80 504F11223344 10.2.3.26 Prog:2019-04-24 21:08:03 Type:0 HwId:A0000 IPv6:,0c112233:10020217/O]

- `LoxLIVE:` can be used to detect the message
- `Loxone Miniserver` is the name of the Miniserver. You might notice, that it is tricky to detect the length of the string. You need to scan for a valid IPv4 behind it to figure it out.
- `192.168.178.32:80` is the local IPv4 with the HTTP port number.
- `504F11223344` is the serial number of the Miniserver
- `10.2.3.26` is the firmware version of the Miniserver
- `Prog:2019-04-24 21:08:03` is the date of the Loxone Config file.
- `Type:0`
- `HwId:A0000` is the hardware version of the Miniserver as documented in [Loxone Miniserver Hardware](LoxoneMiniserverHardware.md)
- `IPv6:,0c112233:10020217/O` looks like it is supposed to contain the IPv6 of the Miniserver, but because it is not assigned one, it seems to return garbage, which looks like the serial number of a Air Base Extension with its firmware version.

### Simple Service Discovery Protocol

This protocol is used by many different hardware devices, like Sonos. As such the Miniserver uses `NOTIFY` to inform the network via Broadcast.

The Miniserver also responds to a [SSDP](https://en.wikipedia.org/wiki/Simple_Service_Discovery_Protocol) request. It returns a reply like this:

    HTTP/1.1 200 OK
    CACHE-CONTROL:max-age=3600
    ST:upnp:rootdevice
    USN:uuid:aabbccdd-eeff-0011-2233-445566778899::upnp:rootdevice
    EXT:
    SERVER:Loxone Miniserver Loxone Miniserver UPnP/1.0
    LOCATION:http://192.168.178.32:80/upnp.xml

It contains the name after "Loxone Miniserver" and the SSDP UUID, as well as a location of an XML, which provides you with the `LOCATION`, which responds with the following XML code, that looks like this:

    <root xmlns="urn:schemas-upnp-org:device-1-0">
      <specVersion>
        <major>1</major>
        <minor>0</minor>
      </specVersion>
      <device>
        <deviceType>urn:schemas-upnp-org:device:HVAC_System:1</deviceType>
        <friendlyName>Loxone Miniserver</friendlyName>
        <manufacturer>Loxone Electronics GmbH</manufacturer>
        <manufacturerURL>https://www.loxone.com/</manufacturerURL>
        <modelDescription>Loxone Electronics home control (Loxone Miniserver: *4C6F786F6E65204D696E69736572766572 192.168.178.32:80 504F11223344 10.2.3.26 IPv6:,0c112233:10020217/O)</modelDescription>
        <modelName>Loxone Miniserver</modelName>
        <modelNumber>1</modelNumber>
        <modelURL>https://www.loxone.com/help/miniserver</modelURL>
        <serialNumber>504F11223344</serialNumber>
        <UDN>uuid:aabbccdd-eeff-0011-2233-445566778899</UDN>
        <iconList>
          <icon>
            <mimetype>image/png</mimetype>
            <width>16</width>
            <height>16</height>
            <depth>32</depth>
            <url>/images/icon16.png</url>
          </icon>
          <icon>
            <mimetype>image/png</mimetype>
            <width>32</width>
            <height>32</height>
            <depth>32</depth>
            <url>/images/icon32.png</url>
          </icon>
          <icon>
            <mimetype>image/png</mimetype>
            <width>48</width>
            <height>48</height>
            <depth>32</depth>
            <url>/images/icon48.png</url>
          </icon>
          <icon>
            <mimetype>image/png</mimetype>
            <width>64</width>
            <height>64</height>
            <depth>32</depth>
            <url>/images/icon64.png</url>
          </icon>
          <icon>
            <mimetype>image/png</mimetype>
            <width>256</width>
            <height>256</height>
            <depth>32</depth>
            <url>/images/icon256.png</url>
          </icon>
        </iconList>
        <presentationURL>http://192.168.178.32:80/index.html</presentationURL>
      </device>
    </root>


The important entries are:

- `friendlyName` - the user facing name of the Miniserver
- `modelNumber` - is provided just like the serial number and the UUID from the flash memory.
- `modelDescription` - similar to the UDP request. The hex-string after the `*` also contains the name.
- `serialNumber` - serial number of the Miniserver
- `UDN` - UUID for the Miniserver, similar to its serial number, but only used for SSDP.
- `presentationURL` - URL to the webinterface
- `iconList` - the iconList does not work, because the png asserts are not on the Miniserver. Feels like a bug.


## During starting of the Miniserver

1. SSDP NOTIFY to the local network
2. Send log information, if necessary
3. UDP dynamic IP update via dns.loxonecloud.com:80
4. HTTP request for the weather forecast
5. NTP clock requests


## Loxone News Feed (www.loxone.com)
The Loxone Smart Home application, but also the webinterface to show ads for Loxone products. These can't be disabled!

The web application is requesting

    https://www.loxone.com/loxone-feed.php?channel=app&lang=dede?_=123456789

which requests the annoying advertisements shown in the top-right corner of the app. The `_` parameter is just a random number (actually a timer value) to avoid caching of the data, it could be omitted. The returned data is a JSON block, which looks like this:

    HTTP/1.1 200 OK
    Date: Mon, 01 May 2018 00:11:22 GMT
    Content-Type: application/json
    Transfer-Encoding: chunked
    Connection: close
    Access-Control-Allow-Origin: *
    Expires: 0
    Last-Modified: Mon, 01 May 2018 00:11:22 GMT
    Cache-Control: no-store, no-cache, must-revalidate
    Cache-Control: post-check=0, pre-check=0
    Pragma: no-cache
    Vary: Accept-Encoding
    Expect-CT: max-age=604800, report-uri="https://report-uri.cloudflare.com/cdn-cgi/beacon/expect-ct"
    Server: cloudflare

    [
        {
            "title": "Touch Nightlight: Viel mehr als ein gew\u00f6hnliches Nachtlicht",
            "image": "https:\/\/www.loxone.com\/wp-content\/uploads\/sites\/2\/2019\/03\/Touch_Nightlight_Header_NEU.png",
            "short_text": "Das Touch Nightlight ist weit mehr als ein gew\u00f6hnliches Nachtlicht. Es ist Ambientelicht, Wecker, Bedienger\u00e4t, Alarmgeber und Nachtlicht zugleich. Diese Vielf\u00e4ltigkeit macht es zur perfekten Erg\u00e4nzung f\u00fcr all Ihre Wohn- und Schlafr\u00e4ume. Vom Elternschlafzimmer bis zum Kinderzimmer.",
            "link": "https:\/\/www.loxone.com\/dede\/touch-nightlight-mehr-als-ein-nachtlicht\/",
            "timestamp": 1553592596,
            "location_long": "",
            "location_lat": "",
            "radius": "",
            "partner_status": ""
        },
        ……………
        {
            "title": "iPad Wallmount: Die eleganteste Wandhalterung aller Zeiten",
            "image": "https:\/\/www.loxone.com\/wp-content\/uploads\/sites\/2\/2018\/11\/Wallmount_Article-Header-Landscape-with-Finishing@1x.min_.png",
            "short_text": "Hochwertige Materialien, beste Verarbeitung, hauchd\u00fcnne Abmessungen, ein elegantes sowie zeitloses Design und ein revolution\u00e4re Ladevorrichtung. Diese Attribute beschreiben unsere iPad Wallmount. Angebracht an Ihrem Lieblingsort, verwandelt sie Ihr iPad in die eleganteste Smart Home Bedienzentrale aller Zeiten. ",
            "link": "https:\/\/www.loxone.com\/dede\/ipad-wallmount\/",
            "timestamp": 1543914098,
            "location_long": "",
            "location_lat": "",
            "radius": "",
            "partner_status": ""
        }
    ]


## Loxone DNS Service (clouddns.loxone.com)

Loxone offers a dynamic DNS service, which allows finding your own servers via the internet, based on the assumption that your home IP address is not static (which it typically is not). This still requires the Firewall to be open for the Miniserver. In general it is probably still better to have a VPN connection to your home, than relying on security of your home automation server. The advantage of this system is: it is easy and reasonably secure (if there are no security issues in the Miniserver and your passwords are good). That said: you are still exposing your server to the internet!


### Publishing the IP address for a Miniserver

To publish the IP, the Miniserver sends a single UDP request to the Loxone DNS Service on port 7700 with the following content:

    504F11223344,80,00000000,AABBCCDDEEFF0011

- `504F11223344` is the 6-byte serial number of the Miniserver. All Miniservers start with `504F`.
- 80 is the port number under which the Miniserver responds to HTTP requests for the Web-Interface
- 00000000 is the version number of the `WebInterfaceAGZ`
- `AABBCCDDEEFF0011` is an 8 byte unique key. This key is constant for the Miniserver and acts as a validation for the serial number. It protects Loxone against bad guys pushing random serial numbers to their DNS server.

But you might be able to spot a problem with security: because the request is not encrypted, any bad guy who manages to collect one request can then send it's own request to Loxone. The next time you try to connect to your server, you then could end up on a compromised server from the bad guy, telling him your admin name and password!

Also it is called every 60s, which feels excessive. It should be called whenever the external IP changes, but not every minute.

### Finding an IP address for a Miniserver

To find the IP address for a Miniserver, you need to know it's serial number and simply send this request: [http://dns.loxonecloud.com/504F11223344]()

This will get resolved to [http://504F11223344.dns.loxonecloud.com]() which forwards directly to your Miniserver.

Alternatively you can get the DNS status by sending this request [http://dns.loxonecloud.com/?getip&snr=504F11223344&json=true](), which returns a proper JSON reply:

    {
      "cmd": "getip",
      "IP": "123.123.123.123",
      "Code": 200,
      "LastUpdated": "2018-02-01 00:11:22",
      "PortOpen": true,
      "DNS-Status": "registered"
    }

Without the json flag, you get an XML reply. Whatever you prefer, but Loxone has been deprecating XML-based APIs, so I would probably go with the JSON one.

    <Answer cmd="getip" LastUpdated="2018-02-01 00:11:22" PortOpen="1" IP="123.123.123.123" Code="200" DNS-Status="registered"/>


## Mailer / Loxone Mailer Service (mail.loxonecloud.com)
The Miniserver can send emails with status updates to any email account.

When using the tandard Mailer service, you have to provide an SMTP server with username and password to send emails, it does support TLS security vis SMTP (Thanks for Stefan for pointing this out)

The Loxone Mailer Service is a special mail server from Loxone, which does encrypt data between the Miniserver and the mail server. The disadvantage is a potential limit on the number of emails you can send and that you are relying on Loxone as well as trusting them with you data. Interestingly it is not using SMTP, but HTTPS to send the data. It works in two steps:

1. Request an authorization key via `https://mail.loxonecloud.com/getkey/MINISERVER_SERIAL`. The response is a 48 byte hex string, which converts into a 24 byte ASCII string.
2. Send the email via POST `https://mail.loxonecloud.com/sendmail/MINISERVER_SERIAL` with an XML block containing the user, date, sender, sender name (the server name), receiver, subject, mail body and an authorization code. The user field is the encrypted username and password, the authorization code is calculated with a HMAC-SHA1 with the response from the first request as a key and a secret code plus the Miniserver serial number as the data. This allows the Mail server to validate the partner.

Security: trusting somebody on the internet is always a risk, even Loxone. But mail is not considered really secure and we are typically talking about status updates. Their choice of HTTPS is fine, but their authorization mechanism is kind of weird. Yes, it is a handshake between two partners, but the signature of the reply is only based on the serial number. The username/password are empty anyway, but probably validated via decryption – which is another check, this time with the date and Miniserver serial number. What is absent are all the other fields, which could be considered an attack surface, because via a man-in-the-middle these fields could be simply replaced with new data. Nevertheless not a very probable attack, but possible, especially if you are in the same network.

## Push Notification Service (push.loxonecloud.com)
This service allows sending notifications to typically mobile devices, like smartphones. The content is similar to mail, but more limited.

Apple requires all iOS software to use HTTPS for notifications, which means that this service is HTTPS based.

Sending a notification is done via an HTTPS POST to `https://push.loxonecloud.com:443/v1/push` with the notification being a JSON block in the body. This block contains a UUID, a timestamp, a title, a message, the name of the Miniserver, a list of UUIDs of devices to notify, a type, an optional sound (none, door bell, alarm, smoke alarm), a level (info,error,system error) and a UUID reference to the notification object in the Loxone configuration. It is also signed via HMAC-SHA1. The server will return a response with a valid status (true/false), an HTTP-like error code and a list of push_errors, e.g. if certain devices are no longer registered for push notifications.

To receive notifications you have to to an HTTPS POST to `https://push.loxonecloud.com:443/v1/register` also with a JSON block.

## Weather Service (weather.loxone.com)

Loxone also offers a subscription to weather service. This service is offered via [Meteo Blue](https://www.meteoblue.com), but routed via a Loxone server [weather.loxone.com](), which validates the subscription.

Several times a day the Miniserver sends the following request: [http://weather.loxone.com:6066/forecast/?user=loxone_504F11223344&coord=13.8408,48.6051&asl=20&format=1]()

You notice a couple of parameters:

- user=loxone_504F11223344 - this is the user account based on the serial number of the Miniserver 
- coord=13.8408,48.6051 - GPS location for the weather report (longitude,latitude). As entered in Loxone Config.
- asl=200 - altitude over sea level in meter. Not sure why this is needed, because `coord` implies it. Can be entered as Elevation in Loxone Config. This parameter seems optional, but the Miniserver always provides it.
- format=1 - the Weather server can return two different report formats: `format=0`, which is XML or `format=1`, which is a mixture between XML and CSV from Meteo Blue. The Miniserver understands both detects the right format automatically.

If have not found out, when the XML/CSV format is requested, it seems that it can happen after a reboot. Typically the Miniserver seems to request XML. But as I said, the server could ignore the format and simply return whatever is more convenient.

If there is no paid subscription, the response will be this:

    HTTP/1.1 200 OK
    Date: Wed, 01 Feb 2018 01:02:34 GMT
    Server: Apache/2.4.7 (Ubuntu)
    Vary: Accept-Encoding
    Content-Length: 153
    Content-Type: text/xml

    <?xml version="1.0"?>
    <ServiceExceptionReport><ServiceException>authentication exception: user is not active</ServiceException></ServiceExceptionReport>


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

Every time data is received, it is appened to `/data/weatheru.bin` on the webserver of the Miniserver (up to 200 entries). The data is in 108 byte chunks as follows:

- 4 Bytes unsigned integer: Loxone Timestamp
- 4 Bytes integer: WW (see `Key` above)
- 4 Bytes integer: DD (see `Key` above)
- 4 Bytes integer: RAD4C (see `Key` above)
- 4 Bytes integer: RH (see `Key` above)
- 8 Bytes double: TT (see `Key` above)
- 8 Bytes double: HI (see `Key` above)
- 8 Bytes double: TD (see `Key` above)
- 8 Bytes double: RR1H (see `Key` above)
- 8 Bytes double: FF (see `Key` above)
- 8 Bytes double: PP0 (see `Key` above)
- 4 Bytes integer: LC (see `Key` above)
- 4 Bytes integer: MC (see `Key` above)
- 4 Bytes integer: HC (see `Key` above)
- 4 Bytes integer: probability of Precipitation (see in the XML format above)
- 8 Bytes double: RAD (see `Key` above)
- 8 Bytes double: Snow Fraction (see in the XML format above)
- 8 Bytes double: CAPE (see in the XML format above)


## Cloud Service Caller (caller.loxone.com)

The Cloud Service Caller is an automated phone callback service from Loxone. It can be configured in Loxone Config. Whenever it is triggered, the Miniserver sends the following request:

[http://caller.loxone.com:80/cgi-bin/loxlive/call.pl?extip=http://dns.loxonecloud.com/504F11223344/dev/sps/io/caller/11389406-009a-2bdf-ffff1402153adf25/&loxid=504F11223344&tel=004912345678&text=Schalter%20aus]()

You can see the following parameters in the request:

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


## Loxone Update Server (update.loxone.com)

Used if checking for "Automatic Updates" is enabled in Loxone Config. [update.loxone.com]() is a server to serve all updates for the Loxone products, it also hosts the XML file, which is requested by the Miniserver and all other Loxone apps. An update for the Miniserver is installed via an update of the the Loxone Config application. The Miniserver will then update all extensions and devices to the latest version automatically.

    http://update.loxone.com/updatecheck.xml?serial=504F11223344&version=10020326&reason=App

You can see the following parameters in the request, they are all just for logging purposes.

- `serial=504F11223344` - serial number of the Miniserver
- `version=10020326` - current firmware version of the Miniserver
- `reason=App` - why was the updated requested. (`0` = the Miniserver, `App` = a Loxone app requests it)

The reply is a rather large XML file, which starting with Version 10 includes public key certificates and signatures used to validate the software update by the Miniserver. Previous versions just used a checksum. I've replaced the certificate and the signatures with `<CERTIFICATE>` and `<SIGNATURE>` to keep the document brief. As you can see, that there are 3 types of updates:

- Release
- Beta
- Test

Loxone seems to use this to allow public beta tests of their software. Updates are also included for all related products, like the "Loxone Smart Home" app for various platforms and TimeZone updates.

    <Miniserversoftware Version="10" certificate="<CERTIFICATE>">
      <Test Version="10.03.05.04" Path="http://updatefiles.loxone.com/LoxConfig/LoxoneConfigSetup_10030504.zip" signature="<SIGNATURE>"/>
      <Beta Version="10.03.05.04" Path="http://updatefiles.loxone.com/LoxConfig/LoxoneConfigSetup_10030504.zip" signature="<SIGNATURE>"/>
      <Release Version="10.02.03.26" Path="http://updatefiles.loxone.com/LoxConfig/LoxoneConfigSetup_10020326.zip" signature="<SIGNATURE>"/>
      <update Name="WebInterface" type="webif">
        <Test Version="20190503" Path="http://updatefiles.loxone.com/WebInterface/10320190503_commonv2.zip" Filesize="5873496" crc32="4577c078" signature=<SIGNATURE>"/>
        <Beta Version="20190503" Path="http://updatefiles.loxone.com/WebInterface/10320190503_commonv2.zip" Filesize="5873496" crc32="4577c078" signature="<SIGNATURE>"/>
        <Release Version="20190402" Path="http://updatefiles.loxone.com/WebInterface/102520190402_commonv2.zip" Filesize="5844622" crc32="73310bf5" signature="<SIGNATURE>"/>
      </update>
      <update Name="WebInterfaceAGZ" type="webifAGZ">
        <Test Version="20190503" Path="http://updatefiles.loxone.com/WebInterfaceAGZ/10320190503_commonv2.agz" Filesize="6008320" crc32="7bbc65ef" signature="<SIGNATURE>"/>
        <Beta Version="20190503" Path="http://updatefiles.loxone.com/WebInterfaceAGZ/10320190503_commonv2.agz" Filesize="6008320" crc32="7bbc65ef" signature="<SIGNATURE>"/>
        <Release Version="20190402" Path="http://updatefiles.loxone.com/WebInterfaceAGZ/102520190402_commonv2.agz" Filesize="5978624" crc32="899ff065" signature="<SIGNATURE>"/>
      </update>
      <update Name="Loxone Smart Home for Mac" type="Mac OS X">
        <Test Version="10.3.0 (2019.05.03)" Path="http://updatefiles.loxone.com/macOS/10320190503.dmg" Filesize="14059397" crc32="eb045428" signature="<SIGNATURE>"/>
        <Beta Version="10.3.0 (2019.05.03)" Path="http://updatefiles.loxone.com/macOS/10320190503.dmg" Filesize="14059397" crc32="eb045428" signature="<SIGNATURE>"/>
        <Release Version="10.2.5 (2019.04.02)" Path="http://updatefiles.loxone.com/macOS/102520190402.dmg" Filesize="14059397" crc32="eb045428" signature="<SIGNATURE>"/>
      </update>
      <update Name="Loxone Smart Home for Linux x64" type="linux-x64">
        <Test Version="10.3.0 (2019.05.03)" Path="http://updatefiles.loxone.com/linux/10320190503-amd64.deb" Filesize="43394142" crc32="df0a2559" signature="<SIGNATURE>"/>
        <Beta Version="10.3.0 (2019.05.03)" Path="http://updatefiles.loxone.com/linux/10320190503-amd64.deb" Filesize="43394142" crc32="df0a2559" signature="<SIGNATURE>"/>
        <Release Version="10.2.5 (2019.04.02)" Path="http://updatefiles.loxone.com/linux/102520190402-amd64.deb" Filesize="43394142" crc32="df0a2559" signature="<SIGNATURE>"/>
      </update>
      <update Name="Loxone Smart Home for Linux x86" type="linux-x86">
        <Test Version="10.3.0 (2019.05.03)" Path="http://updatefiles.loxone.com/linux/10320190503-i386.deb" Filesize="44373068" crc32="8aabec55" signature="<SIGNATURE>"/>
        <Beta Version="10.3.0 (2019.05.03)" Path="http://updatefiles.loxone.com/linux/10320190503-i386.deb" Filesize="44373068" crc32="8aabec55" signature="<SIGNATURE>"/>
        <Release Version="10.2.5 (2019.04.02)" Path="http://updatefiles.loxone.com/linux/102520190402-i386.deb" Filesize="44373068" crc32="8aabec55" signature="<SIGNATURE>"/>
      </update>
      <update Name="Loxone Smart Home for Linux armv7l" type="linux-armv7l">
        <Test Version="10.3.0 (2019.05.03)" Path="http://updatefiles.loxone.com/linux/10320190503-armv7l.deb" Filesize="39867056" crc32="19dc7942" signature="<SIGNATURE>"/>
        <Beta Version="10.3.0 (2019.05.03)" Path="http://updatefiles.loxone.com/linux/10320190503-armv7l.deb" Filesize="39867056" crc32="19dc7942" signature="<SIGNATURE>"/>
        <Release Version="10.2.5 (2019.04.02)" Path="http://updatefiles.loxone.com/linux/102520190402-armv7l.deb" Filesize="39867056" crc32="19dc7942" signature="<SIGNATURE>"/>
      </update>
      <update Name="Loxone Smart Home for Linux arm64" type="linux-arm64">
        <Test Version="10.3.0 (2019.05.03)" Path="http://updatefiles.loxone.com/linux/10320190503-arm64.deb" Filesize="38808166" crc32="04756263" signature="<SIGNATURE>"/>
        <Beta Version="10.3.0 (2019.05.03)" Path="http://updatefiles.loxone.com/linux/10320190503-arm64.deb" Filesize="38808166" crc32="04756263" signature="<SIGNATURE>"/>
        <Release Version="10.2.5 (2019.04.02)" Path="http://updatefiles.loxone.com/linux/102520190402-arm64.deb" Filesize="38808166" crc32="04756263" signature="<SIGNATURE>"/>
      </update>
      <update Name="Loxone Smart Home for Windows" type="windows">
        <Test Version="10.3.0 (2019.05.03)" Path="http://updatefiles.loxone.com/windows/10320190503.exe" Filesize="13155791" crc32="44926439"/>
        <Beta Version="10.3.0 (2019.05.03)" Path="http://updatefiles.loxone.com/windows/10320190503.exe" Filesize="13155791" crc32="44926439"/>
        <Release Version="10.2.5 (2019.04.02)" Path="http://updatefiles.loxone.com/windows/102520190402.exe" Filesize="13155791" crc32="44926439"/>
      </update>
      <update Name="Loxone Smart Home for iOS" type="ios">
        <Test Version="10.3.0 (2019.05.03)"/>
        <Beta Version="10.3.0 (2019.05.03)"/>
        <Release Version="10.2.4 (2019.03.29)"/>
      </update>
      <update Name="Loxone Smart Home for Android" type="android">
        <Test Version="10.3.0 (2019.05.03)"/>
        <Beta Version="10.3.0 (2019.05.03)"/>
        <Release Version="10.2.5 (2019.04.02)"/>
      </update>
      <update Name="Loxone Music Server" type="LoxoneMusicServer">
        <Intern Version="1.3.03.13"/>
        <Beta Version="1.3.03.13"/>
        <Release Version="1.3.03.13"/>
      </update>
      <update Name="LoxLIVE" type="ms">
        <Test Version="10030504" Path="http://updatefiles.loxone.com/bin/10030504_Miniserver.upd" Filesize="11118692" crc32="d76298bf" signature="<SIGNATURE>"/>
        <Beta Version="10020314" Path="http://updatefiles.loxone.com/bin/10020314_Miniserver.upd" Filesize="10990384" crc32="5dd441a" signature="<SIGNATURE>"/>
      </update>
      <update Name="TimeData" type="TimeData">
        <Test Version="20180905" Path="http://updatefiles.loxone.com/Miniserver/20180905_timeData.zip" Filesize="369881" crc32="f592dde6" signature="<SIGNATURE>"/>
        <Beta Version="20180905" Path="http://updatefiles.loxone.com/Miniserver/20180905_timeData.zip" Filesize="369881" crc32="f592dde6" signature="<SIGNATURE>"/>
        <Release Version="20180905" Path="http://updatefiles.loxone.com/Miniserver/20180905_timeData.zip" Filesize="369881" crc32="f592dde6" signature="<SIGNATURE>"/>
      </update>
      <update Name="VenBlindmotorAir" type="air">
        <Test Version="10001009" MsMinVersion="10000924" Path="http://updatefiles.loxone.com/bin/10011009_VenBlindmotorAir.upd" crc32="f8fa38b4" Year="2018" signature="<SIGNATURE>"/>
        <Beta Version="10001009" MsMinVersion="10000924" Path="http://updatefiles.loxone.com/bin/10011009_VenBlindmotorAir.upd" crc32="f8fa38b4" Year="2018" signature="<SIGNATURE>"/>
        <Release Version="10001009" MsMinVersion="10000924" Path="http://updatefiles.loxone.com/bin/10011009_VenBlindmotorAir.upd" crc32="f8fa38b4" Year="2018" signature="<SIGNATURE>"/>
      </update>
      <changelogs>
        <changelog lang="DEU" url="http://www.loxone.com/dede/produkte/software/loxone-config.html"/>
        <changelog lang="ENU" url="http://www.loxone.com/enen/products/software/loxone-config.html"/>
        <changelog lang="CSY" url="http://www.loxone.com/cscz/produkty/software/loxone-config.html"/>
        <changelog lang="ESN" url="http://www.loxone.com/eses/productos/software/loxone-config.html"/>
        <changelog lang="NLD" url="http://www.loxone.com/nlnl/producten/software/loxone-config.html"/>
        <changelog lang="SKY" url="http://www.loxone.com/cscz/produkty/software/loxone-config.html"/>
        <changelogx lang="ENG" url="http://www.loxone.com/enen/products/software/loxone-config.html"/>
        <changelogx lang="FR" url="http://www.loxone.com/frfr/produits/logiciels/loxone-config.html"/>
      </changelogs>
    </Miniserversoftware>


## Loxone Monitor (monitorserver.loxone.com)

The Monitor Server can be enabled in Loxone Config via the "Monitor Server" option. The purpose is to forward the logging, which can be seen in the Loxone Monitor application remotely to help diagnosing issues. The Monitor Server can decided what events are shown and at what detail via the response to the first request from the Miniserver:

    http://monitorserver.loxone.com:80/?504F11223344

Typically the responds looks like this (logging disabled)

    HTTP/1.1 200 OK
    Date: Wed, 01 May 2018 01:23:45 GMT
    Server: Apache/2.2.22 (Debian)
    X-Powered-By: PHP/5.4.45-0+deb7u2
    Cache-Control: no-cache, must-revalidate
    Expires: Mon, 26 Jul 1997 05:00:00 GMT
    Content-Length: 107
    Content-Type: application/xml
    X-Pad: avoid browser bug

    <?xml version="1.0"?>
    <Log Version="10" LogKeep="true" NoIPchange="false">
      <LogMode>Off</LogMode>
    </Log>

But the server could return something like this:

    HTTP/1.1 200 OK
    Date: Wed, 01 May 2018 01:23:45 GMT
    Server: Apache/2.2.22 (Debian)
    X-Powered-By: PHP/5.4.45-0+deb7u2
    Cache-Control: no-cache, must-revalidate
    Expires: Mon, 26 Jul 1997 05:00:00 GMT
    Content-Length: 107
    Content-Type: application/xml
    X-Pad: avoid browser bug

    <Log Version="10" LogKeep="true" NoIPchange="false">
      <LogMode>on</LogMode>
      <LogDest>/dev/udp/192.168.178.200/7777</LogDest>
      <LogLevelCommon>moreinfo</LogLevelCommon>
      <LogLevelSPS>moreinfo</LogLevelSPS>
      <LogLevelProtocol>off</LogLevelProtocol>
      <LogLevelBus>off</LogLevelBus>
      <LogLevelFilesystem>off</LogLevelFilesystem>
      <LogLevelNet>off</LogLevelNet>
    </Log>

This will forward all output to the the UDP port 7777 at the local IP address 192.168.178.200. It will send all possible common and SPS output, but none for Loxone Link (Bus), the filesystem or network access. These are the possible types of data, which can be monitored:

| Type     | Description |
| :------: | ----------- |
| Common   | Displays general information about the Miniserver |
| SPS      | Information about the PLC |
| Protocol | Information on specific protocols such as NTP (time) or UDP |
| Bus      | Information about the CAN bus link |
| File     | Information about the SD card and memory system |
| Network  | Network information for troubleshooting network |

Here are the possible keys:

- `Version` = major version of the Miniserver
- `LogKeep` = boolean, unknown function.
- `NoIPchange` = boolean, if true, the output is send to `/dev/udp/IPADDRESS/PORT` with IPADDRESS being the address of `monitorserver.loxone.com` the the default port being 7777.
- `LogDest` = path for the log file, default is `/dev/null` (logging off)
- `LogMode` = `on` or `off`
- `LogLevelCommon` = `off`,`severe`,`serious`,`warning`,`info`,`moreinfo`
- `LogLevelSPS` = `off`,`severe`,`serious`,`warning`,`info`,`moreinfo`
- `LogLevelProtocol` = `off`,`severe`,`serious`,`warning`,`info`,`moreinfo`
- `LogLevelBus` = `off`,`severe`,`serious`,`warning`,`info`,`moreinfo`
- `LogLevelFilesystem` = `off`,`severe`,`serious`,`warning`,`info`,`moreinfo`
- `LogLevelNet` = `off`,`severe`,`serious`,`warning`,`info`,`moreinfo`
- `LogStart` = Loxone timestamp as an integer
- `LogDay` = integer, number of days logging should be active. Up to 7 days is possible.
- `LogUntil` = UTC date/time string, can be used as an alternative to `LogDay` and supports a longer duration.


## Loxone Log Server (log.loxone.com)

Loxone allows sending Crashlogs automatically to them via the "Loxone Log" setting in Loxone Config. If enabled, the Miniserver will send a binary block of Loxone Support Crashlog, when necessary.

The data is 982 bytes long and send to log.loxone.com:7707 via UDP.

Now the question: what data is in it? Typical crashlog related data:

- timestamp
- serial number of the Miniserver
- version of the Miniserver
- which hardware the Miniserver is running on
- local IP address
- used/maximum memory
- Latitude/Longitude of the Miniserver from the config file.
- name of the owner of the Miniserver from the config file.
- error statistics
- function callstack on a crash

As you can see with the exception of the owner and the Latitude/Longitude of the Miniserver, there is not really any personal data in this block. And the coordinates are send to Loxone via the Weather report anyway.


## Miniserver Web-Interface

The Miniserver offers a HTTP interface at the HTTP port 80 (this port can be changed in Loxone Config). You can use a webbrowser to use the "Loxone Smart Home" directly on the server.

## Miniserver FTP-Interface

The Miniserver offers a FTP interface at the FTP port 21 (this port can be changed in Loxone Config). This is used to upload a configuration or download backups.

The FTP server supports these commands:

| FTP command | Description |
| ----------: | :---------- |
| QUIT        | Logout |
| USER        | User Name |
| PASS        | Password |
| NOOP        | No-Op |
| PASV        | Passive Mode |
| PORT        | Data Port |
| PWD, XPWD   | Print Directory |
| SYST        | System |
| TYPE        | Representation Type |
| OPTS        | Options |
| SITE        | Site Parameters |
| CWD         | Change Working Directory |
| CDUP        | Change to Parent Directory |
| REIN        | Reinitialize |
| FEAT        | Feature Negotiation |
| SIZE        | File Size |
| MDTM        | File Modification Time |
| DELE        | Delete File |
| LIST, NLST  | List, Name List	 |
| MKD, XMKD   | Make Directory |
| RETR        | Retrieve |
| RNFR        | Rename From |
| RNTO        | Rename From	 |
| RMD, XRMD   | Remove Directory |
| STOR        | Store |
