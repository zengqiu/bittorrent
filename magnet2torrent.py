# -*- coding: utf-8 -*-

# forked from https://github.com/hpfn/Magnet2Torrent/blob/master/Magnet_To_Torrent2.py

import shutil
import tempfile
import os
import sys
import libtorrent
from time import sleep
from argparse import ArgumentParser
import urllib2
import bencode, hashlib, base64, urllib

def download_torrent(url, filename):
    try:
        if r'bt.box.n0808.com' in url:
            headers = {
                "Referer": "http://bt.box.n0808.com",
                "User-Agent": "Mozilla/5.0"
            }
            request = urllib2.Request(url, headers=headers)
            torrent = urllib2.urlopen(request)
        else:
            torrent = urllib2.urlopen(url, timeout=20)
    except Exception, e:
        print 'Error: ' + str(e)
        print 'URL: ' + url
        return None
        
    data = torrent.read()
    if len(data) > 0:
        with open(filename, 'wb') as output:
            output.write(data)
            return filename
    else:
        print 'Error: Get an 0 byte torrent.'
        print 'URL: ' + url
        return None

def magnet2torrent_cache(magnet, output_name=None):
    if output_name and not os.path.isdir(output_name) and not os.path.isdir(os.path.dirname(os.path.abspath(output_name))):
        print("Invalid output folder: " + os.path.dirname(os.path.abspath(output_name)))
        print("")
        sys.exit(0)

    hash_str = magnet.split('&')[0].split(':')[-1]
    if len(hash_str) == 40:
        hash_sha1 = hash_str.upper()
        hash_base32 = base64.b32encode(hash_str.decode('hex')).upper()
    else:
        hash_base32 = hash_str.upper()
        hash_sha1 = base64.b32decode(hash_str).encode('hex').upper()

    if output_name:
        if os.path.isdir(output_name):
            output = os.path.abspath(os.path.join(output_name, hash_str + '.torrent'))
        elif os.path.isdir(os.path.dirname(os.path.abspath(output_name))):
            output = os.path.abspath(output_name)
    else:
        output = os.path.abspath(hash_str + '.torrent')
    
    url_xunlei = 'http://bt.box.n0808.com/%s/%s/%s.torrent' % (hash_sha1[:2], hash_sha1[-2:], hash_sha1)
    url_torrent = 'http://www.torrent.org.cn/Home/torrent/download.html?hash=%s' % hash_sha1
    url_torcache = 'http://torcache.net/torrent/%s.torrent' % hash_sha1
    url_torrage = 'http://torrage.com/torrent/%s.torrent' % hash_sha1
    url_zoink = 'http://zoink.it/torrent/%s.torrent' % hash_sha1
    url_ip = 'https://178.73.198.210/torrent/%s.torrent' % hash_sha1
    url_vuze = 'http://magnet.vuze.com/magnetLookup?hash=%s' % hash_base32
    url_torrentkittycn = 'http://d1.torrentkittycn.com/?infohash=%s' % hash_sha1
    url_karmorra = 'http://reflektor.karmorra.info/torrent/%s.torrent' % hash_sha1

    urls = [url_xunlei, url_torrent, url_torcache, url_torrage, url_zoink, url_ip, url_vuze, url_torrentkittycn, url_karmorra]

    for url in urls:
        torrent = download_torrent(url, output)
        if torrent:
            return torrent
            
    if not torrent:
        print '[!] Can not download torrent from cache.'
        return None

def magnet2torrent_libtorrent(magnet, output_name=None):
    if output_name and not os.path.isdir(output_name) and not os.path.isdir(os.path.dirname(os.path.abspath(output_name))):
        print("Invalid output folder: " + os.path.dirname(os.path.abspath(output_name)))
        print("")
        sys.exit(0)

    tempdir = tempfile.mkdtemp()
    ses = libtorrent.session()
	
    # one could want to set this
    ses.listen_on(6881, 6882)
	
    ses.add_dht_router("router.utorrent.com", 6881)
    ses.add_dht_router("router.bittorrent.com", 6881)
    ses.add_dht_router("router.bitcomet.com", 6881)
    ses.add_dht_router("dht.transmissionbt.com", 6881)
    ses.add_dht_router("dht.aelitis.com", 6881)
    ses.add_dht_router("67.215.246.10", 6881)
    ses.add_dht_router("82.221.103.244", 6881)

    ses.start_dht()
    ses.start_lsd()
    ses.start_upnp()
    ses.start_natpmp()
    
    # add 'url'. for add_torrent()
    params = {
        'url': magnet,
        'save_path': tempdir,
        'storage_mode': libtorrent.storage_mode_t(2),
        'paused': False,
        'auto_managed': True,
        'duplicate_is_error': True
    }
    # add_magnet_uri is deprecated
    # http://www.rasterbar.com/products/libtorrent/manual.html#add-magnet-uri
    # handle = libtorrent.add_magnet_uri(ses, magnet, params)
    handle = ses.add_torrent(params)

    print("Downloading Metadata (this may take a while)")
    
    # used to control "Maybe..." msgs
    # after sleep(1)
    x = 1
    limit = 120
    
    while (not handle.has_metadata()):
        try:
            sleep(1)
            if x > limit:
                print("Maybe your firewall is blocking, or the magnet link is not right...")
                limit += 30
            x += 1
        except KeyboardInterrupt:
            print("Aborting...")
            ses.pause()
            print("Cleanup dir " + tempdir)
            shutil.rmtree(tempdir)
            sys.exit(0)
    ses.pause()
    print 'Got metadata, starting torrent download...'

    torinfo = handle.get_torrent_info()
    torfile = libtorrent.create_torrent(torinfo)

    output = os.path.abspath(torinfo.name() + ".torrent")

    if output_name:
        if os.path.isdir(output_name):
            output = os.path.abspath(os.path.join(output_name, torinfo.name() + ".torrent"))
        elif os.path.isdir(os.path.dirname(os.path.abspath(output_name))):
            output = os.path.abspath(output_name)

    print("Saving torrent file here: " + output + " ...")
    torcontent = libtorrent.bencode(torfile.generate())
    f = open(output, "wb")
    f.write(libtorrent.bencode(torfile.generate()))
    f.close()
    print("Saved! Cleaning up dir: " + tempdir)
    ses.remove_torrent(handle)
    shutil.rmtree(tempdir)

    return output

def main():
    parser = ArgumentParser(description="A command line tool that converts magnet links in to .torrent files")
    parser.add_argument('-m','--magnet', help='The magnet url')
    parser.add_argument('-o','--output', help='The output torrent file name')

    #
    # This second parser is created to force the user to provide
    # the 'output' arg if they provide the 'magnet' arg.
    #
    # The current version of argparse does not have support
    # for conditionally required arguments. That is the reason
    # for creating the second parser
    #
    # Side note: one should look into forking argparse and adding this
    # feature.
    #
    conditionally_required_arg_parser = ArgumentParser(description="A command line tool that converts magnet links in to .torrent files")
    conditionally_required_arg_parser.add_argument('-m','--magnet', help='The magnet url', required=True)
    conditionally_required_arg_parser.add_argument('-o','--output', help='The output torrent file name')

    magnet = None
    output_name = None

    #
    # Attemos.pathing to retrieve args using the new method
    #
    args = vars(parser.parse_known_args()[0])
    if args['magnet'] is not None:
        magnet = args['magnet']
        argsHack = vars(conditionally_required_arg_parser.parse_known_args()[0])
        output_name = argsHack['output']
    if args['output'] is not None and output_name is None:
        output_name = args['output']
        if magnet is None:
            #
            # This is a special case.
            # This is when the user provides only the "output" args.
            # We're forcing him to provide the 'magnet' args in the new method
            #
            print ('usage: {0} [-h] [-m MAGNET] -o OUTPUT'.format(sys.argv[0]))
            print ('{0}: error: argument -m/--magnet is required'.format(sys.argv[0]))
            sys.exit()
    #
    # Defaulibtorrenting to the old of doing things
    # 
    if output_name is None and magnet is None:
        if len(sys.argv) >= 2:
            magnet = sys.argv[1]
        if len(sys.argv) >= 3:
            output_name = sys.argv[2]

    if magnet:
        print magnet, output_name
        torrent = magnet2torrent_cache(magnet, output_name)
        if torrent:
            print '[*] Get torrent from cache successed.'
        else:
            print '[*] Using libtorrent to get torrent.'
            magnet2torrent_libtorrent(magnet, output_name)
    else:
        print ('usage: {0} [-h] [-m MAGNET] -o OUTPUT'.format(sys.argv[0]))

if __name__ == "__main__":
    main()