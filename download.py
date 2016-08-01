# -*- coding: utf-8 -*-

# forked from https://github.com/arvidn/libtorrent/blob/master/docs/python_binding.rst

import libtorrent as lt
import time
import sys
from argparse import ArgumentParser

def download(input_name):
    ses = lt.session()
    ses.listen_on(6881, 6891)

    e = lt.bdecode(open(input_name, 'rb').read())
    info = lt.torrent_info(e)

    params = {
        'save_path': '.', 
        'storage_mode': lt.storage_mode_t.storage_mode_sparse,
        'ti': info
    }
    h = ses.add_torrent(params)

    s = h.status()

    while (not s.is_seeding):
        s = h.status()
        state_str = ['queued', 'checking', 'downloading metadata', 'downloading', 'finished', 'seeding', 'allocating', 'checking resume data']
        print '%.2f%% complete (down: %.1f kb/s up: %.1f kB/s peers: %d) %s %.3f' % (s.progress*100, s.download_rate/1000, s.upload_rate/1000, s.num_peers, state_str[s.state], s.total_download/1000000)
        time.sleep(1)

def main():
    parser = ArgumentParser(description="A command line tool that download files from .torrent file")
    parser.add_argument('-i','--input', help='The input torrent file name')
    conditionally_required_arg_parser = ArgumentParser(description="A command line tool that download files from .torrent file")
    conditionally_required_arg_parser.add_argument('-i', '--input', help='The input torrent file name', required=True)

    input_name = None

    args = vars(parser.parse_known_args()[0])
    if args['input'] is not None and input_name is None:
        input_name = args['input']
        
    if input_name is None and len(sys.argv) >= 2:
        input_name = sys.argv[1]

    if input_name:
        print input_name
        download(input_name)
    else:
        print ('usage: {0} [-h] [-i INPUT]'.format(sys.argv[0]))

if __name__ == "__main__":
    main()