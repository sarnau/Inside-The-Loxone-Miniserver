# Loxone SD Card Format

## Why read this?

All files are directly accessible via FTP directly – which is non obvious, because the FTP server could filter the available list of files. This means there is typically no need to dig into the SD card to recover a file.

1. If the SD card is damaged, this document might help you to potentially recover files.
2. You can also use this to validate if the file system is correct. Potentially repairing it. The Miniserver has only very rudimentary repair code in place.
3. You could even patch the firmware image to load whatever firmware you like.
4. You are interested, just because…

Because everything is stored on the SD card itself, you always switch to a fresh SD card, if your experiment fails. Dont' forget to always make a full backup of your SD card first!
 
## Intro

The Miniserver loads the firmware from the SD card via a little boot loader, which exists in the flash memory on the board. The SD card also contains the file system, which is used for the configuration, the web server and all additional files, like statistics. This filesystem is only accessed by the Miniserver firmware.

## FAT32 container

The Micro-SD card is a standard 2GB memory card with a FAT32 filesystem on it. It contains a single file 'LOXONE_SD', which occupies the whole medium. It is addressed directly, the FAT32 filesystem is ignored. You can not just copy this file onto a different disk, because the *FS Information Sector* needs to point to it and it can't be fragmented in any way.

The FAT32 system on a 2GB memory card is pretty standard:
- 512 bytes sector size
- 3911551 sectors (a bit more than 1.9GB)
- 32 hidden sectors
- a copy of the boot sector #0 in sector #6
- a copy of the FS Information sector #1 in sector #7 (ignore by the Miniserver)
- a FAT32 with 955 sectors, starting at sector #32 (directly after the hidden sectors)
- a one cluster directory with two entries: `LOXONE_SD` as the volume label and a `LOXONE1.FS` file.
- The content of the `LOXONE1.FS` file with 2002157568 bytes (3910464/0x3BAB40 sectors).
- 68 unused sectors behind that file. Probably a safety margin or rounding error.

The LOXONE1.FS file contains the custom Loxone file system, which is as far as I know, not supported by any software, but the Miniserver.

## Finding the firmware and volume

The wrapping file system on the SD card is ignored by the Miniserver, it only looks for the *FS Information Sector*, which is expected in sector #1, following directly after the boot record in sector #0. If it can't be detected, it will assume the SD card has a Master Boot Record (MBR) in sector #0 and pull the start sector for volume #0 from it. In that volume the *FS Information Sector* is loaded again. If it can't be found, the boot will fail. The content of this sector is ignored, besides the 3 signatures, which are used to validate it. Loxone stores private information right in front of the middle signature at the `0x01E4` offset:

| Offset | Description |
| -----: | :---------- |
| 0x1CC  | base sector pointing to the begining of the `LOXONE_SD` file. |
| 0x1D0  | number of reserved sectors, they are ignored, typically a value like 5. |
| 0x1D4  | number of sectors reserved for the firmware image. Typically `0x10005` (ca. 64MB), which feels like a bug, because the additional 5 is not needed and already part of the reserved sectors, but it also doesn't harm. |
| 0x1D8  | offset behind the filesystem relative to the filesystem start. This value *minus* the one in `0x1D4` is the size of the filesystem in sectors. |
| 0x1DC  | unknown, the value seems to be `0x20`. Might be the number of sectors per cluster, but this is hardcoded in the filesystem and this value is not used. |
| 0x1E0  | mode for the transaction cache, typically 0. More to that below at the transaction record. |

The size of the filesystem in sectors seems to be a bit less than the actual size of the `LOXONE1.FS` file. 54 empty sectors are at the end. Again: either a bug or a safety margin.

Because of these data structures, it is not enough to copy the file from the SD card, you should always make an image copy of the whole SD card, never just a copy of the `LOXONE1.FS`! That said: you could write a new *FS Information Sector* sector with the info from above to get it to work with the Miniserver, but this is not really a clean solution.

Note: a sector is *always* 512 bytes.

The 3 areas in the image are as follows:

1. A 5 sector reserved area at the beginning. The first sector of the file has a copy of the *FS Information Sector*, the rest is filled with zeros.
2. The firmware image area, about 32MB in size.
3. The writeable file system

## Firmware image area

This area contains three full copies of the firmware at sector 0x0000, 0x4000 and 0x8000 within this area. The allows up to 8MB for the firmware data. And while the firmware is about 11MB large, it is compressed only about 1/3 of that, so the current firmware versions do fit comfortably.

The firmware data starts with one header sector, which only uses a few words:

| Offset | Description |
| -----: | :---------- |
| 0x000  | Magic value, always `0xC2C101AC`. Used to validate the header. |
| 0x004  | Number of sectors occupied for the firmware, used to load the necessary sectors. |
| 0x008  | Firmware version number, used to detect the latest firmware. |
| 0x00C  | 32-bit XOR checksum over all sectors of the compressed firmware, used to verify after loading all sectors. |
| 0x010  | Size of the compressed firmware in bytes. Used for decompressing the data. |
| 0x014  | Size of the uncompressed firmware in bytes. Used after decompression to validate the success of the decompression. |

During boot the Miniserver tests for the magic value and loads the newest version of the firmware. In case of an error, it tries the next firmware and so on. This avoids a dead server, if a firmware update or a single sector in the firmware area of the SD card failed.

### Compression of the firmware

The firmware is using a simple decompression, which I'll show as Python code:

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


## Loxone File System (LXF)

The Loxone file system is a transaction-based file system. It is not optimized for mediums which have slow seek times – which makes sense, because the only supported medium is a SD card. It also validates consistency via checksums, but only over the data structures of the file system, not the actual files.

It only supports files and directories. Links, file attributes, access rights, etc. are not needed by the Miniserver and therefore supported.

### Clusters

Note: The system combines 32 sectors into one cluster. This means the smallest size of a non-zero file is 16kb. Addressing of data however is always done via sector numbers, relative to the beginning of the file system. Clusters are only used for managing which sectors are used and which ones are empty.

A cluster can contain either system records or raw file data.

#### Reserved Clusters

The first clusters in the file system are reserved and setup during formatting. The exact content is explained in the individual paragraphs about the record formats.

1. Cluster 0 starting at sector 0 contains the transaction records. 2 or 32 sectors depending on the mode for the transaction cache from the header. 2 seems to be the norm.
2. Cluster 1 starting at sector 32 contains the root directory records. This is the root directory of the filesystem.
3. Cluster 2- starting at sector 64 contain the necessary allocation records. The amount of used clusters for the allocation records depends on the size of the filesystem.

All cluster beyond are used on demand. When space is needed the system tries to allocate system records at the beginning of the file system, while data for files are allocated at the end of it. There seems to be no obvious technical reason for this and if the file system is getting full, it is entirely possible for these to end up being mixed up, so it is probably done for safety reasons (protection against bugs) and also makes debugging the file system easier.

### System records

The system records contain the management information about files, directories, allocations and transactions. Because this information is very important, great care was taken to guarantee the validity of these.

|   Offset    | Description |
| ----------- | :---------- |
| 0x000-0x003 | 32-bit type, which defines what the sector contains. 7 types are defined. |
| 0x004-0x007 | Upper-Word of the version for this sector |
| 0x008-0x00B | Lower-Word of the version for this sector |
| 0x00C-0x00F | Link to the next sector, following this sector |
| 0x010-0x1FB | Data, depending on the sector type |
| 0x1FC-0x1FF | CRC32 over the content of this sector |

Each system record exists twice on disk. At `sector` and at `sector+1`, which means that for practical reasons only even sector numbers are used. The server reads both, validates the CRC and returns the sector with the higher version number to the higher levels of code. This ties in with the transaction management, which allows to undo changes in case of a crash during writing. During write the version number is incremented by one and the older version of the record overwritten.

Regular file data is written as raw data to disk. No duplication, no checksums, etc.

| Type | Name | Description |
| ---- | ---- | :---------- |
| LXFF | File | First record of a file, allows up to 1.3MB large files. |
| LXFE | File Extension | Additional records to add up to 1.9MB to a file. |
| LXFD | Directory | First record of a directory with up to 44 entries. |
| LXFC | Directory Extension | Additional records to add up to 61 entries to a directory |
| LXFT | Transaction | Double sectors used to track transactions |
| LXFA | Allocation | Large bitmaps used to track if a cluster is used or free |
| LXFR | Empty File? | Behaves similar to a regular file, does not have any data? I've never seen this one in the wild. |

### File record

|      Offset |          Name | Description |
| ----------- | ------------- | :---------- |
| 0x000-0x07F | filename      | Filename, typically ASCII only |
| 0x080-0x083 | parent sector | Files and directories are stored in a directory. This points to the parent. `0` is the root directory at sector `0x20` |
| 0x084-0x087 | creation timestamp | Loxone timestamp of the creation date/time of this file, like a UNIX timestamp, but starting at 1.1.2009 |
| 0x088-0x08B | modification timestamp | Loxone timestamp of the last modification date/time of this file. Set on close. |
| 0x08C-0x08F | file size     | Size of the file in bytes |
| 0x090-0x093 | maximum file size | This is the maximum size, before additional clusters need to be allocated. It is typically – but not necessarily – the file size rounded up to the next 16kb |
| 0x094-0x1EC | cluster list  | List of up to 86 sectors pointing to the start of clusters containing the actual file data |

### File extension record

If a file is too large, extension records are added. They are linked via the link sector at offset `0x0C` to the file record. Because a file record is stored in a cluster, a file typically has 16KB/2 (duplication sectors) minus 1 (the file record) == 15 file extension records, which is enough for almost 30mb large files. But it can be extended by allocating additional clusters for file extension records and linking them to the file record.

|      Offset |          Name | Description |
| ----------- | ------------- | :---------- |
| 0x000-0x1EC | cluster list  | List of up to 123 sectors pointing to the start of clusters containing the actual file data |

### Directory record

A directory doesn't have data, but is instead a list of file and directory references. It is similar to files with a record and extension records. The file system starts with a root directory, which does not have a parent sector. This root always starts at sector 32.

|      Offset |          Name | Description |
| ----------- | ------------- | :---------- |
| 0x000-0x07F | filename      | Filename, typically ASCII only |
| 0x080-0x083 | parent sector | Files and directories are stored in a directory. This points to the parent. `0` is the root directory at sector `0x20` |
| 0x084-0x087 | creation timestamp | Loxone timestamp of the creation date/time of this file, like a UNIX timestamp, but starting at 1.1.2009 |
| 0x088-0x137 | name hash     | 44 hash values over the names of the file/directory to allow quicker access |
| 0x138-0x1E7 | cluster list  | List of up to 44 sector references to files/directories |

To find a file in a directory a hash value over the name is calculated and then compared. If it matches, the sector from the cluster list is loaded and the full name is compared. This allows a significant speed up. The hash is calculated as follows:

    hash = (CRC32(filename) & 0xFFFFFF) | (len(filename) << 24) | (isDirectory << 31)

The CRC32 is calculated over single bytes of the filename. The top-bit contains the info if the hash is for a file (0) or a directory (1), which is also used to speed up iterating over directories.

A sector reference of 0 represents an empty entry in the directory. A directory has no order, files/directories are added in order of adding them to the parent directory. Deleting objects will create gaps, which will be filled on the next add.

### Directory extension record

If a directory needs to store more than 44 entries, extension records can be added, just like for files. 959 entries will fit into one directory, if it uses one cluster.

|      Offset |          Name | Description |
| ----------- | ------------- | :---------- |
| 0x000-0x0F3 | name hash     | 61 hash values over the names of the file/directory to allow quicker access |
| 0x0F4-0x1E7 | cluster list  | List of up to 61 sector references to files/directories |


### Allocation record

The system needs to keep track, which clusters are used and which ones are available. This is done via the allocation record. The allocation record always starts at sector 64.

|      Offset |          Name | Description |
| ----------- | ------------- | :---------- |
| 0x000-0x003 | available clusters | available clusters in this record |
| 0x004-0x1EB | bitmap        | 122 32-bit values used as a bitmap |

One record can store the state of 32 * 122 = 3904 clusters or 61MB. The number of records needed depend on the size of the file system. The allocation record always starts at sector 64 and extends from there. For a 2GB disk image it is 64 sectors large.

The available clusters field is an optimization, which counts the zero bits in the bitfield. It allows to quickly find allocation records with available space.

The number of allocation records is depended on the size of the volume, because it needs to store the status for all possible clusters. In the above example the number of sectors is 0x3AAB00. To calculate the cluster number we have to do this:

    sectorcount * 512 (bytes per sector) / 16kb (size of a cluster) / (122*32) (number of bits in the allocation record) + 1 (rounding up)
    clustercount = (2 * sectorcount + 31) / 32

For 0x3AAB00 sectors we need 31 allocation records and 2 clusters. Twice the sectors because every sector in the allocation table is stored twice on disc and `+31)/32` to round up, not down. 32 sectors are in a cluster. So, in this example 2 clusters after the root directory are reserved for the allocation table. Unnecessary sectors (because of rounding) in this clusters are simple empty (all zeros).


### Transaction record

To avoid a corrupt filesystem in case of a crash or unexpected power-down, a transaction record is kept. It is driven by the version number in each record. The transaction records always starts at sector 0. Typically it is 1 double-sector, but if the mode of the transaction cache is 2 (see the FS information struct), then 16 double-sectors are used. The transaction records always occupy a cluster, which means in the default configuration 30 empty sectors (all zeros) are behind the two transaction record sectors.

|      Offset |          Name | Description |
| ----------- | ------------- | :---------- |
| 0x000-0x187 | sector list   | 98 sectors |
| 0x188-0x1E9 | 1-byte flags  | 98 flags (0=record was updated, 1=new sector was written) |
| 0x1FA-0x1FB | version       | Version number of the transaction record, used when multiple transaction records are used (off by default) to determine the latest one |

Whenever a record is changed, it's version is bumped up and the older one is to be overwritten. There is a writing cache in between to minimize the number of reads and writes. The cache is written periodically or during certain events, like closing a file.

You might notice, that file data doesn't have version numbers. It still maintains stability against crashes, by never overwriting existing data, but rather writing into an empty space and then releasing the old data. If the system crashes in the middle of writing, all allocation table changes will be undone and the previous state is maintained. Once all data was written to the card, the transaction record is cleared.

The version number is set during boot to the version of the most recent transaction record + 1, so it is always incrementing! Interestingly there seems to be a bug in the code: if the transaction record is complete garbage (even the CRC is wrong), the server will still pull the version number from it. If that number is smaller than previous valid records, it will destroy data.
