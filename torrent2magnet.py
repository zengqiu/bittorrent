# -*- coding: utf-8 -*-

import bencode, hashlib, base64, urllib
import sys
from argparse import ArgumentParser
import libtorrent

def torrent2magnet_libtorrent(input_name):
    info = libtorrent.torrent_info(input_name)
    print 'magnet:?xt=urn:btih:%s&dn=%s' % (info.info_hash(), info.name())
    return 'magnet:?xt=urn:btih:%s&dn=%s' % (info.info_hash(), info.name())

def torrent2magnet_bencode(input_name):
    # torrent = open('AVOP-118.torrent', 'rb').read()
    torrent = open(input_name, 'rb').read()
    metadata = bencode.bdecode(torrent)
    hashcontents = bencode.bencode(metadata['info'])

    # print hashlib.sha1(hashcontents).hexdigest()
    # print 'magnet:?xt=urn:btih:%s&dn=%s' % (hashlib.sha1(hashcontents).hexdigest(), metadata['info']['name'])
    
    digest = hashlib.sha1(hashcontents).digest()
    b32hash = base64.b32encode(digest)
    # params = {
    #     'xt': 'urn:btih:%s' % b32hash,
    #     'dn': metadata['info']['name'],
    #     'tr': metadata['announce'],
    #     'xl': metadata['info']['length']
    # }
    # paramstr = urllib.urlencode(params)
    # magneturi = 'magnet:?%s' % paramstr
    print 'magnet:?xt=urn:btih:%s&dn=%s' % (b32hash, metadata['info']['name'])
    return 'magnet:?xt=urn:btih:%s&dn=%s' % (b32hash, metadata['info']['name'])

def main():
    parser = ArgumentParser(description="A command line tool that converts .torrent file to magnet link")
    parser.add_argument('-i','--input', help='The input torrent file name')
    conditionally_required_arg_parser = ArgumentParser(description="A command line tool that converts .torrent file to magnet link")
    conditionally_required_arg_parser.add_argument('-i', '--input', help='The input torrent file name', required=True)

    input_name = None

    args = vars(parser.parse_known_args()[0])
    if args['input'] is not None and input_name is None:
        input_name = args['input']
        
    if input_name is None and len(sys.argv) >= 2:
        input_name = sys.argv[1]

    if input_name:
        print input_name
        torrent2magnet_libtorrent(input_name)
        # torrent2magnet_bencode(input_name)
    else:
        print ('usage: {0} [-h] [-i INPUT]'.format(sys.argv[0]))

if __name__ == "__main__":
    main()