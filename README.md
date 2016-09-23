
BitTorrent
======
## **bittorrent.py**
GUI for these tools implemented by QT4.

## bittorrent_py2exe.py
A python script for compiling.

## **download.py**
A python script for downloading files from torrent file.

## **magnet2torrent.py**
A python script for converting magnet link to torrent file.

### How To Use
`python magnet2torrent.py -m <magnet link> -o [torrent file]`

### Example
`python magnet2torrent.py -m 'magnet:?xt=urn:btih:ANRBNFHQ5CZM5BZBNSM4WXFDV4RQFHRX' -o 'abc.torrent'`

## **torrent2magnet.py**
A python script for converting torrent file to magnet link.

### How To Use
`python torrent2magnet.py -i <torrent file>`

### Example
`python torrent2magnet.py -i 'abc.torrent'`