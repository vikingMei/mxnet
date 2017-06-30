#!/usr/bin/env python
# coding: utf-8
#
# Usage: 
# Author: Summer Qing(qingyun.wu@aispeech.com)

import sys
import json 
import codecs


def main(fname, fout):
    vocab = {}
    vocab[''] = 0   # reserve for padding label

    fid = codecs.open(fname, 'r', 'utf-8')
    while 1:
        line = fid.readline()
        if not line:
            break

        line = line.strip()
        for wrd in line.split(' '):
            if vocab.get(wrd):
                continue
            else:
                vocab[wrd] = len(vocab)
    fid.close()

    with open(fout, 'w') as fid:
        json.dump(vocab, fid, ensure_ascii=False)

if "__main__"==__name__:
    reload(sys)
    sys.setdefaultencoding('utf-8')

    if len(sys.argv)<3:
        print "USAGE: "
        print "     %s vocab-list out" % sys.argv[0]
        print ''
        print 'EXAMPLE: '
        print '     %s comm.vocab.118k.v5.wlist vocab.json'
        sys.exit(0)

    fname = sys.argv[1]
    out = sys.argv[2]

    main(fname, out)
